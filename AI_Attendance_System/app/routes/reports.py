from datetime import datetime, date

from flask import (
    Blueprint,
    render_template,
    request
)

from app.models import Student, Attendance
from app.routes.auth import admin_required


reports_bp = Blueprint(
    "reports",
    __name__,
    url_prefix="/reports"
)


@reports_bp.route("/")
@admin_required
def reports_page():

    selected_date = request.args.get(
        "date",
        ""
    ).strip()

    if selected_date:

        try:
            report_date = datetime.strptime(
                selected_date,
                "%Y-%m-%d"
            ).date()

        except ValueError:
            report_date = date.today()

    else:
        report_date = date.today()


    total_students = Student.query.count()


    present_today = Attendance.query.filter_by(
        date=report_date,
        status="Present"
    ).count()


    absent_today = max(
        total_students - present_today,
        0
    )


    attendance_percentage = (
        (present_today / total_students) * 100
        if total_students > 0
        else 0
    )


    attendance_records = (
        Attendance.query
        .filter_by(
            date=report_date
        )
        .order_by(
            Attendance.time.asc()
        )
        .all()
    )


    return render_template(
        "reports/index.html",
        report_date=report_date,
        selected_date=report_date.strftime(
            "%Y-%m-%d"
        ),
        total_students=total_students,
        present_today=present_today,
        absent_today=absent_today,
        attendance_percentage=round(
            attendance_percentage,
            2
        ),
        attendance_records=attendance_records
    )