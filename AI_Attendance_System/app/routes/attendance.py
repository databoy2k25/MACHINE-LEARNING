import csv
from io import StringIO, BytesIO

from flask import (
    Blueprint,
    render_template,
    request,
    Response,
    send_file
)

from openpyxl import Workbook

from app.models import Attendance, Student
from app.routes.auth import admin_required


attendance_bp = Blueprint(
    "attendance",
    __name__,
    url_prefix="/attendance"
)


@attendance_bp.route("/")
@admin_required
def attendance_page():

    date_filter = request.args.get(
        "date",
        ""
    ).strip()

    student_filter = request.args.get(
        "student",
        ""
    ).strip()

    query = Attendance.query

    if date_filter:
        query = query.filter(
            Attendance.date == date_filter
        )

    if student_filter:
        query = query.join(
            Student,
            Attendance.student_id == Student.id
        ).filter(
            Student.name.ilike(
                f"%{student_filter}%"
            )
        )

    attendance_records = (
        query
        .order_by(
            Attendance.date.desc(),
            Attendance.time.desc()
        )
        .all()
    )

    return render_template(
        "attendance/index.html",
        attendance_records=attendance_records,
        date_filter=date_filter,
        student_filter=student_filter
    )


@attendance_bp.route("/export")
@admin_required
def export_attendance():

    records = (
        Attendance.query
        .order_by(
            Attendance.date.desc(),
            Attendance.time.desc()
        )
        .all()
    )

    output = StringIO()

    writer = csv.writer(output)

    writer.writerow([
        "Student ID",
        "Name",
        "Date",
        "Time",
        "Status",
        "Confidence"
    ])

    for attendance in records:

        writer.writerow([
            attendance.student.student_id,
            attendance.student.name,
            attendance.date.strftime(
                "%d-%m-%Y"
            ),
            attendance.time.strftime(
                "%I:%M:%S %p"
            ),
            attendance.status,
            (
                f"{attendance.confidence * 100:.2f}%"
                if attendance.confidence is not None
                else ""
            )
        ])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition":
                "attachment; filename=attendance_report.csv"
        }
    )


@attendance_bp.route("/export-excel")
@admin_required
def export_attendance_excel():

    records = (
        Attendance.query
        .order_by(
            Attendance.date.desc(),
            Attendance.time.desc()
        )
        .all()
    )

    workbook = Workbook()

    worksheet = workbook.active
    worksheet.title = "Attendance"

    worksheet.append([
        "Student ID",
        "Name",
        "Date",
        "Time",
        "Status",
        "Confidence"
    ])

    for attendance in records:

        worksheet.append([
            attendance.student.student_id,
            attendance.student.name,
            attendance.date.strftime(
                "%d-%m-%Y"
            ),
            attendance.time.strftime(
                "%I:%M:%S %p"
            ),
            attendance.status,
            (
                f"{attendance.confidence * 100:.2f}%"
                if attendance.confidence is not None
                else ""
            )
        ])

    worksheet.column_dimensions["A"].width = 15
    worksheet.column_dimensions["B"].width = 25
    worksheet.column_dimensions["C"].width = 15
    worksheet.column_dimensions["D"].width = 18
    worksheet.column_dimensions["E"].width = 15
    worksheet.column_dimensions["F"].width = 15

    file_data = BytesIO()

    workbook.save(file_data)

    file_data.seek(0)

    return send_file(
        file_data,
        as_attachment=True,
        download_name="attendance_report.xlsx",
        mimetype=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        )
    )