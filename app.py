"""
app.py — V Secure Technologies Attendance & Field Tracking System.

Run locally:
    flask run                  (uses .env automatically)

Deploy:
    gunicorn app:app --workers 2
"""

import os
from datetime import date, datetime

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from config import config_map
from models import Attendance, Employee, SiteVisit, User, db

# ──────────────────────────────────────────────
#  App factory
# ──────────────────────────────────────────────

def create_app(env: str | None = None) -> Flask:
    """Create and configure the Flask application."""
    env = env or os.environ.get("FLASK_ENV", "development")
    app = Flask(__name__)
    app.config.from_object(config_map.get(env, config_map["default"]))

    # Extensions
    db.init_app(app)

    login_manager = LoginManager(app)
    login_manager.login_view = "login"  # type: ignore[assignment]
    login_manager.login_message = "Please log in to access this page."
    login_manager.login_message_category = "warning"

    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        return db.session.get(User, int(user_id))

    # Jinja2 helpers
    app.jinja_env.globals["format_time"] = _format_time_12hr
    app.jinja_env.globals["today"] = date.today

    # Register routes
    _register_routes(app)

    return app


# ──────────────────────────────────────────────
#  Helpers
# ──────────────────────────────────────────────

def _format_time_12hr(time_str: str | None) -> str:
    """Convert 'HH:MM' to '12-hour AM/PM' format, or return '—'."""
    if not time_str or time_str == "—":
        return "—"
    try:
        t = datetime.strptime(time_str, "%H:%M")
        return t.strftime("%I:%M %p")
    except ValueError:
        return time_str


def _seed_demo_data() -> None:
    """Populate the database with demo data on first run."""
    if User.query.first():
        return  # already seeded

    admin = User(username="admin", role="admin")
    admin.set_password("admin123")

    employees = [
        Employee(name="Ravi Kumar",   department="Engineering", role="Senior Engineer",      email="ravi@vsecure.com"),
        Employee(name="Priya S.",     department="HR",          role="HR Manager",           email="priya@vsecure.com"),
        Employee(name="Arun M.",      department="IT",          role="Developer",            email="arun@vsecure.com"),
        Employee(name="Sanjay K.",    department="Field",       role="Fire Alarm Engineer",  email="sanjay@vsecure.com",  is_field_engineer=True),
        Employee(name="Muthu R.",     department="Field",       role="CCTV Engineer",        email="muthu@vsecure.com",   is_field_engineer=True),
        Employee(name="Lakshmi P.",   department="Field",       role="BMS Engineer",         email="lakshmi@vsecure.com", is_field_engineer=True),
    ]

    db.session.add(admin)
    db.session.add_all(employees)
    db.session.commit()


# ──────────────────────────────────────────────
#  Routes
# ──────────────────────────────────────────────

def _register_routes(app: Flask) -> None:

    # ── Auth ────────────────────────────────────

    @app.route("/", methods=["GET", "POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("dashboard"))
        if request.method == "POST":
            username = request.form.get("username", "").strip()
            password = request.form.get("password", "")
            user = User.query.filter_by(username=username).first()
            if user and user.check_password(password):
                login_user(user)
                next_page = request.args.get("next")
                flash(f"Welcome back, {user.username}!", "success")
                return redirect(next_page or url_for("dashboard"))
            flash("Invalid username or password.", "error")
        return render_template("login.html")

    @app.route("/logout")
    @login_required
    def logout():
        logout_user()
        flash("You have been logged out.", "info")
        return redirect(url_for("login"))

    # ── Dashboard ───────────────────────────────

    @app.route("/dashboard")
    @login_required
    def dashboard():
        today = date.today()
        total_employees   = Employee.query.filter_by(is_field_engineer=False, is_active=True).count()
        present_today     = Attendance.query.filter_by(date=today, status="Present").count()
        absent_today      = Attendance.query.filter_by(date=today, status="Absent").count()
        on_site           = SiteVisit.query.filter_by(date=today).count()
        total_engineers   = Employee.query.filter_by(is_field_engineer=True, is_active=True).count()

        recent_attendance = (
            Attendance.query
            .filter_by(date=today)
            .order_by(Attendance.recorded_at.desc())
            .limit(8)
            .all()
        )
        recent_visits = (
            SiteVisit.query
            .filter_by(date=today)
            .order_by(SiteVisit.recorded_at.desc())
            .limit(5)
            .all()
        )

        return render_template(
            "dashboard.html",
            today=today,
            total_employees=total_employees,
            present_today=present_today,
            absent_today=absent_today,
            on_site=on_site,
            total_engineers=total_engineers,
            recent_attendance=recent_attendance,
            recent_visits=recent_visits,
        )

    # ── Attendance ──────────────────────────────

    @app.route("/attendance", methods=["GET", "POST"])
    @login_required
    def attendance():
        today = date.today()

        if request.method == "POST":
            emp_id    = request.form.get("employee_id", type=int)
            check_in  = request.form.get("check_in") or None
            check_out = request.form.get("check_out") or None
            status    = request.form.get("status", "Present")
            notes     = request.form.get("notes", "").strip() or None

            if not emp_id:
                flash("Please select an employee.", "error")
            else:
                # Update if record exists for today, else create new
                existing = Attendance.query.filter_by(employee_id=emp_id, date=today).first()
                if existing:
                    existing.check_in  = check_in
                    existing.check_out = check_out
                    existing.status    = status
                    existing.notes     = notes
                    flash("Attendance updated successfully.", "success")
                else:
                    record = Attendance(
                        employee_id=emp_id,
                        date=today,
                        check_in=check_in,
                        check_out=check_out,
                        status=status,
                        notes=notes,
                    )
                    db.session.add(record)
                    flash("Attendance recorded successfully.", "success")
                db.session.commit()
            return redirect(url_for("attendance"))

        # GET — load today's attendance
        view_date_str = request.args.get("date")
        try:
            view_date = date.fromisoformat(view_date_str) if view_date_str else today
        except ValueError:
            view_date = today

        employees  = Employee.query.filter_by(is_field_engineer=False, is_active=True).order_by(Employee.name).all()
        records    = (
            Attendance.query
            .filter_by(date=view_date)
            .order_by(Attendance.recorded_at.desc())
            .all()
        )

        return render_template(
            "attendance.html",
            today=today,
            view_date=view_date,
            employees=employees,
            records=records,
        )

    # ── Delete Attendance ────────────────────────

    @app.route("/attendance/delete/<int:record_id>", methods=["POST"])
    @login_required
    def delete_attendance(record_id: int):
        record = db.session.get(Attendance, record_id)
        if record:
            db.session.delete(record)
            db.session.commit()
            flash("Attendance record deleted.", "info")
        return redirect(url_for("attendance"))

    # ── Employees ───────────────────────────────

    @app.route("/employees", methods=["GET", "POST"])
    @login_required
    def employees():
        if request.method == "POST":
            name               = request.form.get("name", "").strip()
            department         = request.form.get("department", "").strip()
            role               = request.form.get("role", "").strip()
            email              = request.form.get("email", "").strip() or None
            phone              = request.form.get("phone", "").strip() or None
            is_field_engineer  = request.form.get("is_field_engineer") == "true"

            if not name or not department:
                flash("Name and department are required.", "error")
            elif email and Employee.query.filter_by(email=email).first():
                flash("An employee with that email already exists.", "error")
            else:
                emp = Employee(
                    name=name,
                    department=department,
                    role=role,
                    email=email,
                    phone=phone,
                    is_field_engineer=is_field_engineer,
                )
                db.session.add(emp)
                db.session.commit()
                flash(f"{name} has been added successfully.", "success")
            return redirect(url_for("employees"))

        search = request.args.get("q", "").strip()
        query  = Employee.query.filter_by(is_active=True)
        if search:
            query = query.filter(Employee.name.ilike(f"%{search}%"))

        all_employees = query.order_by(Employee.name).all()
        office_staff  = [e for e in all_employees if not e.is_field_engineer]
        field_team    = [e for e in all_employees if e.is_field_engineer]

        return render_template(
            "employees.html",
            office_staff=office_staff,
            field_team=field_team,
            search=search,
        )

    # ── Delete Employee ──────────────────────────

    @app.route("/employees/delete/<int:emp_id>", methods=["POST"])
    @login_required
    def delete_employee(emp_id: int):
        emp = db.session.get(Employee, emp_id)
        if emp:
            emp.is_active = False  # soft delete
            db.session.commit()
            flash(f"{emp.name} has been removed.", "info")
        return redirect(url_for("employees"))

    # ── Field Engineers ─────────────────────────

    @app.route("/engineers", methods=["GET", "POST"])
    @login_required
    def engineers():
        today = date.today()

        if request.method == "POST":
            eng_id     = request.form.get("engineer_id", type=int)
            site_name  = request.form.get("site_name", "").strip()
            location   = request.form.get("location", "").strip() or None
            arrival    = request.form.get("arrival_time") or None
            departure  = request.form.get("departure_time") or None
            purpose    = request.form.get("purpose", "").strip() or None
            notes      = request.form.get("notes", "").strip() or None

            if not eng_id or not site_name:
                flash("Engineer and site name are required.", "error")
            else:
                visit = SiteVisit(
                    engineer_id=eng_id,
                    site_name=site_name,
                    location=location,
                    date=today,
                    arrival_time=arrival,
                    departure_time=departure,
                    purpose=purpose,
                    notes=notes,
                )
                db.session.add(visit)
                db.session.commit()
                flash(f"Site visit at '{site_name}' logged successfully.", "success")
            return redirect(url_for("engineers"))

        field_engineers = Employee.query.filter_by(is_field_engineer=True, is_active=True).order_by(Employee.name).all()
        today_visits    = SiteVisit.query.filter_by(date=today).order_by(SiteVisit.recorded_at.desc()).all()
        on_site         = len([v for v in today_visits if v.arrival_time and not v.departure_time])

        return render_template(
            "engineers.html",
            today=today,
            field_engineers=field_engineers,
            today_visits=today_visits,
            on_site=on_site,
        )

    # ── Delete Site Visit ───────────────────────

    @app.route("/engineers/delete/<int:visit_id>", methods=["POST"])
    @login_required
    def delete_visit(visit_id: int):
        visit = db.session.get(SiteVisit, visit_id)
        if visit:
            db.session.delete(visit)
            db.session.commit()
            flash("Site visit record deleted.", "info")
        return redirect(url_for("engineers"))

    # ── Reports ─────────────────────────────────

    @app.route("/reports")
    @login_required
    def reports():
        today = date.today()

        # Month filter
        month_str = request.args.get("month")
        try:
            filter_date = date.fromisoformat(month_str + "-01") if month_str else today.replace(day=1)
        except (ValueError, TypeError):
            filter_date = today.replace(day=1)

        year, month = filter_date.year, filter_date.month

        # Attendance summary per employee for the month
        employees = Employee.query.filter_by(is_field_engineer=False, is_active=True).order_by(Employee.name).all()
        summary = []
        for emp in employees:
            records = Attendance.query.filter(
                Attendance.employee_id == emp.id,
                db.extract("year",  Attendance.date) == year,
                db.extract("month", Attendance.date) == month,
            ).all()
            present   = sum(1 for r in records if r.status == "Present")
            absent    = sum(1 for r in records if r.status == "Absent")
            leave     = sum(1 for r in records if r.status == "Leave")
            half_day  = sum(1 for r in records if r.status == "Half Day")
            summary.append({
                "employee": emp,
                "present": present,
                "absent": absent,
                "leave": leave,
                "half_day": half_day,
                "total": len(records),
            })

        # Field engineer site visits this month
        visits = SiteVisit.query.filter(
            db.extract("year",  SiteVisit.date) == year,
            db.extract("month", SiteVisit.date) == month,
        ).order_by(SiteVisit.date.desc()).all()

        return render_template(
            "reports.html",
            today=today,
            filter_date=filter_date,
            summary=summary,
            visits=visits,
        )


# ──────────────────────────────────────────────
#  Entry point
# ──────────────────────────────────────────────

app = create_app()


@app.cli.command("init-db")
def init_db_command() -> None:
    """Create tables and seed demo data."""
    with app.app_context():
        db.create_all()
        _seed_demo_data()
        print("✅ Database initialised with demo data.")


with app.app_context():
    db.create_all()
    _seed_demo_data()


if __name__ == "__main__":
    app.run(debug=False)
