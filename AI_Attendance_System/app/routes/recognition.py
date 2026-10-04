import os
import uuid
from datetime import date, datetime
from flask import Blueprint, flash, redirect, render_template, request, url_for
from deepface import DeepFace
import numpy as np
from app import db
from app.models.attendance import Attendance
from app.models.face_data import FaceData
from app.models.student import Student
from app.routes.auth import (admin_required, student_required)

recognition_bp = Blueprint("recognition", __name__, url_prefix="/recognition")


def cosine_distance(source_rep, test_rep):
    a = np.asarray(source_rep)
    b = np.asarray(test_rep)
    return 1 - (np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


@recognition_bp.route("/")
@student_required
def recognition_page():
    return render_template("recognition/index.html")


@recognition_bp.route(
    "/recognize",
    methods=["POST"]
)
@student_required
def recognize_face():
    if "face_image" not in request.files:
        flash("No image capture received.", "danger")
        return redirect(url_for("recognition.recognition_page"))

    file = request.files["face_image"]
    if file.filename == "":
        flash("Empty image payload.", "danger")
        return redirect(url_for("recognition.recognition_page"))

    temp_dir = os.path.join("app", "face_data", "temp")
    os.makedirs(temp_dir, exist_ok=True)
    temp_filename = f"rec_{uuid.uuid4().hex}.jpg"
    temp_path = os.path.join(temp_dir, temp_filename)
    file.save(temp_path)

    try:
        captured_objs = DeepFace.represent(
            img_path=temp_path,
            model_name="Facenet512",
            detector_backend="opencv",
            enforce_detection=True,
        )
        captured_embedding = captured_objs[0]["embedding"]
    except Exception:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        flash("No face detected in camera frame. Please center your face.", "warning")
        return redirect(url_for("recognition.recognition_page"))

    face_records = FaceData.query.all()
    best_match_student_id = None
    min_distance = float("inf")
    threshold = 0.30

    for record in face_records:
        if not record.embedding:
            try:
                objs = DeepFace.represent(
                    img_path=record.image_path,
                    model_name="Facenet512",
                    detector_backend="opencv",
                    enforce_detection=False,
                )
                record.embedding = objs[0]["embedding"]
                db.session.commit()
            except Exception:
                continue

        dist = cosine_distance(captured_embedding, record.embedding)
        if dist < min_distance:
            min_distance = dist
            best_match_student_id = record.student_id

    if os.path.exists(temp_path):
        os.remove(temp_path)

    if best_match_student_id and min_distance <= threshold:
        student = Student.query.get(best_match_student_id)
        today = date.today()
        now_time = datetime.now().time()

        existing = Attendance.query.filter_by(
            student_id=student.id, date=today
        ).first()

        if existing:
            flash(f"{student.name} is already marked present today.", "info")
        else:
            confidence_score = max(
                0.0, round((1.0 - (min_distance / threshold)) * 100, 2)
            )
            new_attendance = Attendance(
                student_id=student.id,
                date=today,
                time=now_time,
                status="Present",
                confidence=confidence_score,
            )
            db.session.add(new_attendance)
            db.session.commit()
            flash(
                f"Attendance marked for {student.name} (Match Confidence: {confidence_score}%).",
                "success",
            )
    else:
        flash("Face not recognized. Please try again.", "danger")

    return redirect(url_for("recognition.recognition_page"))