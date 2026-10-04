from functools import wraps

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for
)

from werkzeug.security import check_password_hash

from app import db
from app.models import Admin


auth_bp = Blueprint(
    "auth",
    __name__,
    url_prefix="/auth"
)


# =========================================================
# ADMIN ACCESS PROTECTION
# =========================================================

def admin_required(view_function):
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):

        if "admin_id" not in session:
            flash(
                "Please login to access this page.",
                "warning"
            )

            return redirect(
                url_for("auth.login")
            )

        return view_function(*args, **kwargs)

    return wrapped_view


# =========================================================
# STUDENT ACCESS PROTECTION
# =========================================================

def student_required(view_function):
    @wraps(view_function)
    def wrapped_view(*args, **kwargs):

        if "student_logged_in" not in session:
            flash(
                "Please login to continue.",
                "warning"
            )

            return redirect(
                url_for("auth.student_login")
            )

        return view_function(*args, **kwargs)

    return wrapped_view


# =========================================================
# ADMIN LOGIN
# =========================================================

@auth_bp.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if "admin_id" in session:
        return redirect(
            url_for("auth.dashboard")
        )

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if not username or not password:

            flash(
                "Username and password are required.",
                "danger"
            )

            return render_template(
                "auth/login.html"
            )

        admin = Admin.query.filter_by(
            username=username
        ).first()

        if admin and check_password_hash(
            admin.password,
            password
        ):

            session.clear()

            session["admin_id"] = admin.id
            session["admin_username"] = admin.username

            flash(
                "Login successful.",
                "success"
            )

            return redirect(
                url_for("auth.dashboard")
            )

        flash(
            "Invalid username or password.",
            "danger"
        )

    return render_template(
        "auth/login.html"
    )


# =========================================================
# STUDENT LOGIN
# =========================================================

@auth_bp.route(
    "/student-login",
    methods=["GET", "POST"]
)
def student_login():

    if "student_logged_in" in session:
        return redirect(
            url_for(
                "recognition.recognition_page"
            )
        )

    if request.method == "POST":

        username = request.form.get(
            "username",
            ""
        ).strip()

        password = request.form.get(
            "password",
            ""
        )

        if (
            username == "student"
            and password == "student123"
        ):

            session.clear()

            session["student_logged_in"] = True
            session["student_username"] = username

            return redirect(
                url_for(
                    "recognition.recognition_page"
                )
            )

        flash(
            "Invalid student username or password.",
            "danger"
        )

    return render_template(
        "auth/student_login.html"
    )


# =========================================================
# ADMIN DASHBOARD
# =========================================================

@auth_bp.route("/dashboard")
@admin_required
def dashboard():

    from datetime import date
    from app.models import Student, Attendance

    today = date.today()

    total_students = Student.query.count()

    present_today = Attendance.query.filter_by(
        date=today,
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

    today_attendance = (
        Attendance.query
        .filter_by(
            date=today
        )
        .order_by(
            Attendance.time.desc()
        )
        .all()
    )

    return render_template(
        "auth/dashboard.html",
        total_students=total_students,
        present_today=present_today,
        absent_today=absent_today,
        attendance_percentage=round(
            attendance_percentage,
            2
        ),
        today_attendance=today_attendance
    )


# =========================================================
# ADMIN LOGOUT
# =========================================================

@auth_bp.route("/logout")
def logout():

    session.clear()

    flash(
        "You have been logged out.",
        "info"
    )

    return redirect(
        url_for("auth.login")
    )


# =========================================================
# STUDENT LOGOUT
# =========================================================

@auth_bp.route("/student-logout")
def student_logout():

    session.clear()

    flash(
        "You have been logged out.",
        "info"
    )

    return redirect(
        url_for("auth.student_login")
    )