from flask import Flask
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    app.config.from_object("config.Config")

    db.init_app(app)

    from app.models import (
        Admin,
        Student,
        FaceData,
        Attendance
    )

    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.student import student_bp
    from app.routes.recognition import recognition_bp
    from app.routes.attendance import attendance_bp
    from app.routes.reports import reports_bp


    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(recognition_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(reports_bp)
    

    with app.app_context():
        db.create_all()

    return app