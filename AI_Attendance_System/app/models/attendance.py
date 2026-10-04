from datetime import datetime

from app import db


class Attendance(db.Model):
    __tablename__ = "attendance"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id"),
        nullable=False
    )
    student = db.relationship(
    "Student",
    backref=db.backref("attendance_records", lazy=True)
    )

    date = db.Column(
        db.Date,
        nullable=False
    )

    time = db.Column(
        db.Time,
        nullable=False
    )

    status = db.Column(
        db.String(20),
        nullable=False,
        default="Present"
    )

    confidence = db.Column(
        db.Float,
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return f"<Attendance Student {self.student_id} {self.date}>"