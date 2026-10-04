from datetime import datetime
from app import db


class FaceData(db.Model):
    __tablename__ = "face_data"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"), nullable=False)
    image_path = db.Column(db.String(255), nullable=False)
    embedding = db.Column(db.JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    student = db.relationship(
        "Student",
        backref=db.backref("face_data", uselist=False, cascade="all, delete-orphan"),
    )

    def __repr__(self):
        return f"<FaceData {self.id} for Student {self.student_id}>"