import os
import uuid
import shutil

import cv2
import numpy as np

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    url_for
)

from app import db
from app.models import Student, FaceData
from app.routes.auth import admin_required
from app.services.face_service import detect_face


# =========================================================
# PATH CONFIGURATION
# =========================================================

BASE_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        ".."
    )
)

FACE_DATA_DIR = os.path.join(
    BASE_DIR,
    "face_data"
)


# =========================================================
# BLUEPRINT
# =========================================================

student_bp = Blueprint(
    "student",
    __name__,
    url_prefix="/students"
)


# =========================================================
# STUDENT LIST
# =========================================================

@student_bp.route("/")
@admin_required
def list_students():
    search = request.args.get(
        "search",
        ""
    ).strip()

    query = Student.query

    if search:
        query = query.filter(
            db.or_(
                Student.name.ilike(
                    f"%{search}%"
                ),
                Student.student_id.ilike(
                    f"%{search}%"
                )
            )
        )

    students = query.order_by(
        Student.id.desc()
    ).all()

    return render_template(
        "students/list.html",
        students=students,
        search=search
    )


# =========================================================
# ADD STUDENT
# =========================================================

@student_bp.route(
    "/add",
    methods=["GET", "POST"]
)
@admin_required
def add_student():

    if request.method == "POST":

        student_id = request.form.get(
            "student_id",
            ""
        ).strip()

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        department = request.form.get(
            "department",
            ""
        ).strip()

        course = request.form.get(
            "course",
            ""
        ).strip()

        semester = request.form.get(
            "semester",
            ""
        ).strip()


        # -------------------------------------------------
        # REQUIRED FIELDS
        # -------------------------------------------------

        if not student_id or not name:

            flash(
                "Student ID and name are required.",
                "danger"
            )

            return render_template(
                "students/add.html"
            )


        # -------------------------------------------------
        # DUPLICATE STUDENT ID
        # -------------------------------------------------

        existing_student = Student.query.filter_by(
            student_id=student_id
        ).first()

        if existing_student:

            flash(
                "Student ID already exists.",
                "danger"
            )

            return render_template(
                "students/add.html"
            )


        # -------------------------------------------------
        # DUPLICATE EMAIL
        # -------------------------------------------------

        if email:

            existing_email = Student.query.filter_by(
                email=email
            ).first()

            if existing_email:

                flash(
                    "Email address already exists.",
                    "danger"
                )

                return render_template(
                    "students/add.html"
                )


        # -------------------------------------------------
        # CREATE STUDENT
        # -------------------------------------------------

        student = Student(
            student_id=student_id,
            name=name,
            email=email or None,
            phone=phone or None,
            department=department or None,
            course=course or None,
            semester=semester or None
        )

        db.session.add(student)
        db.session.commit()


        flash(
            "Student added successfully.",
            "success"
        )

        return redirect(
            url_for(
                "student.list_students"
            )
        )


    return render_template(
        "students/add.html"
    )


# =========================================================
# VIEW STUDENT
# =========================================================

@student_bp.route(
    "/view/<int:student_id>"
)
@admin_required
def view_student(student_id):

    student = Student.query.get_or_404(
        student_id
    )

    return render_template(
        "students/view.html",
        student=student
    )


# =========================================================
# EDIT STUDENT
# =========================================================

@student_bp.route(
    "/edit/<int:student_id>",
    methods=["GET", "POST"]
)
@admin_required
def edit_student(student_id):

    student = Student.query.get_or_404(
        student_id
    )


    if request.method == "POST":

        new_student_id = request.form.get(
            "student_id",
            ""
        ).strip()

        name = request.form.get(
            "name",
            ""
        ).strip()

        email = request.form.get(
            "email",
            ""
        ).strip()

        phone = request.form.get(
            "phone",
            ""
        ).strip()

        department = request.form.get(
            "department",
            ""
        ).strip()

        course = request.form.get(
            "course",
            ""
        ).strip()

        semester = request.form.get(
            "semester",
            ""
        ).strip()


        # -------------------------------------------------
        # REQUIRED FIELDS
        # -------------------------------------------------

        if not new_student_id or not name:

            flash(
                "Student ID and name are required.",
                "danger"
            )

            return render_template(
                "students/edit.html",
                student=student
            )


        # -------------------------------------------------
        # DUPLICATE STUDENT ID
        # -------------------------------------------------

        duplicate_student = Student.query.filter(
            Student.student_id == new_student_id,
            Student.id != student.id
        ).first()

        if duplicate_student:

            flash(
                "Student ID already exists.",
                "danger"
            )

            return render_template(
                "students/edit.html",
                student=student
            )


        # -------------------------------------------------
        # DUPLICATE EMAIL
        # -------------------------------------------------

        if email:

            duplicate_email = Student.query.filter(
                Student.email == email,
                Student.id != student.id
            ).first()

            if duplicate_email:

                flash(
                    "Email address already exists.",
                    "danger"
                )

                return render_template(
                    "students/edit.html",
                    student=student
                )


        # -------------------------------------------------
        # UPDATE STUDENT
        # -------------------------------------------------

        student.student_id = new_student_id
        student.name = name
        student.email = email or None
        student.phone = phone or None
        student.department = department or None
        student.course = course or None
        student.semester = semester or None

        db.session.commit()


        flash(
            "Student updated successfully.",
            "success"
        )

        return redirect(
            url_for(
                "student.view_student",
                student_id=student.id
            )
        )


    return render_template(
        "students/edit.html",
        student=student
    )


# =========================================================
# DELETE STUDENT
# =========================================================

@student_bp.route(
    "/delete/<int:student_id>",
    methods=["POST"]
)
@admin_required
def delete_student(student_id):

    student = Student.query.get_or_404(
        student_id
    )


    # -------------------------------------------------
    # DELETE FACE DATA FOLDER
    # -------------------------------------------------

    student_folder = os.path.join(
        FACE_DATA_DIR,
        str(student.id)
    )

    if os.path.exists(student_folder):

        shutil.rmtree(
            student_folder,
            ignore_errors=True
        )


    # -------------------------------------------------
    # DELETE DATABASE RECORD
    # -------------------------------------------------

    db.session.delete(
        student
    )

    db.session.commit()


    flash(
        "Student deleted successfully.",
        "success"
    )

    return redirect(
        url_for(
            "student.list_students"
        )
    )


# =========================================================
# REGISTER FACE
# =========================================================

@student_bp.route(
    "/register-face/<int:student_id>",
    methods=["GET", "POST"]
)
@admin_required
def register_face(student_id):

    student = Student.query.get_or_404(
        student_id
    )


    # =====================================================
    # GET REQUEST
    # =====================================================

    if request.method == "GET":

        return render_template(
            "students/register_face.html",
            student=student
        )


    # =====================================================
    # POST REQUEST
    # =====================================================

    try:

        # -------------------------------------------------
        # CHECK FILE
        # -------------------------------------------------

        if "face_image" not in request.files:

            flash(
                "No face image was received.",
                "danger"
            )

            return redirect(
                url_for(
                    "student.register_face",
                    student_id=student.id
                )
            )


        image_file = request.files[
            "face_image"
        ]


        # -------------------------------------------------
        # CHECK FILENAME
        # -------------------------------------------------

        if not image_file.filename:

            flash(
                "Please capture a face image.",
                "danger"
            )

            return redirect(
                url_for(
                    "student.register_face",
                    student_id=student.id
                )
            )


        # -------------------------------------------------
        # READ IMAGE
        # -------------------------------------------------

        image_bytes = image_file.read()

        if not image_bytes:

            flash(
                "The uploaded image is empty.",
                "danger"
            )

            return redirect(
                url_for(
                    "student.register_face",
                    student_id=student.id
                )
            )


        # -------------------------------------------------
        # CONVERT IMAGE
        # -------------------------------------------------

        image_array = np.frombuffer(
            image_bytes,
            dtype=np.uint8
        )

        image = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )

        if image is None:

            flash(
                "Invalid image file.",
                "danger"
            )

            return redirect(
                url_for(
                    "student.register_face",
                    student_id=student.id
                )
            )


        print(
            "Image size:",
            image.shape[1],
            "x",
            image.shape[0]
        )


        # -------------------------------------------------
        # CREATE STUDENT FACE FOLDER
        # -------------------------------------------------

        student_folder = os.path.join(
            FACE_DATA_DIR,
            str(student.id)
        )

        os.makedirs(
            student_folder,
            exist_ok=True
        )


        # -------------------------------------------------
        # CREATE UNIQUE IMAGE NAME
        # -------------------------------------------------

        filename = (
            "face_"
            + uuid.uuid4().hex
            + ".jpg"
        )

        image_path = os.path.join(
            student_folder,
            filename
        )


        # -------------------------------------------------
        # SAVE IMAGE
        # -------------------------------------------------

        saved = cv2.imwrite(
            image_path,
            image
        )

        if not saved:

            flash(
                "Failed to save the face image.",
                "danger"
            )

            return redirect(
                url_for(
                    "student.register_face",
                    student_id=student.id
                )
            )


        # =================================================
        # FACE DETECTION
        # =================================================

        print(
            "Running DeepFace face detection..."
        )

        face_detected, face_message = detect_face(
            image_path
        )

        print(
            "Face detection result:",
            face_detected,
            face_message
        )


        # -------------------------------------------------
        # FACE NOT VALID
        # -------------------------------------------------

        if not face_detected:

            if os.path.exists(image_path):

                os.remove(
                    image_path
                )

            flash(
                face_message,
                "danger"
            )

            return redirect(
                url_for(
                    "student.register_face",
                    student_id=student.id
                )
            )


        # =================================================
        # FACE DETECTED
        # =================================================

        face_data = FaceData.query.filter_by(
            student_id=student.id
        ).first()


        # -------------------------------------------------
        # UPDATE EXISTING FACE
        # -------------------------------------------------

        if face_data:

            old_image_path = (
                face_data.image_path
            )


            # Delete old image

            if (
                old_image_path
                and os.path.exists(old_image_path)
                and old_image_path != image_path
            ):

                try:

                    os.remove(
                        old_image_path
                    )

                except OSError:

                    pass


            face_data.image_path = (
                image_path
            )

            # Clear old embedding until a new
            # embedding-generation feature is added.

            face_data.embedding = None


        # -------------------------------------------------
        # CREATE NEW FACE DATA
        # -------------------------------------------------

        else:

            face_data = FaceData(
                student_id=student.id,
                image_path=image_path,
                embedding=None
            )

            db.session.add(
                face_data
            )


        # -------------------------------------------------
        # SAVE DATABASE
        # -------------------------------------------------

        db.session.commit()


        # -------------------------------------------------
        # SUCCESS
        # -------------------------------------------------

        flash(
            "Face detected and registered successfully.",
            "success"
        )

        return redirect(
            url_for(
                "student.view_student",
                student_id=student.id
            )
        )


    # =====================================================
    # ERROR HANDLING
    # =====================================================

    except Exception as error:

        db.session.rollback()


        # Delete image if something failed

        try:

            if (
                "image_path" in locals()
                and os.path.exists(image_path)
            ):

                os.remove(
                    image_path
                )

        except Exception:

            pass


        print(
            "Face registration error:",
            error
        )


        flash(
            f"Face registration failed: {error}",
            "danger"
        )


        return redirect(
            url_for(
                "student.register_face",
                student_id=student.id
            )
        )