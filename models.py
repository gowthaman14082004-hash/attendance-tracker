"""
models.py — SQLAlchemy database models.

Tables
------
User        — admin / employee login accounts
Employee    — office staff and field engineers
Attendance  — daily check-in / check-out records
SiteVisit   — field engineer on-site visit log
"""

from datetime import date, datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

db = SQLAlchemy()


# ──────────────────────────────────────────────
#  User
# ──────────────────────────────────────────────

class User(UserMixin, db.Model):
    """Application login account (admin or employee)."""

    __tablename__ = "users"

    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(80), unique=True, nullable=False, index=True)
    password_hash: str = db.Column(db.String(256), nullable=False)
    role: str = db.Column(db.String(20), default="employee")  # admin | employee
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password: str) -> None:
        """Hash and store *password*."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Return True if *password* matches the stored hash."""
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<User {self.username!r} role={self.role!r}>"


# ──────────────────────────────────────────────
#  Employee
# ──────────────────────────────────────────────

class Employee(db.Model):
    """Office employee or field engineer record."""

    __tablename__ = "employees"

    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(120), nullable=False)
    department: str = db.Column(db.String(80), nullable=False)
    role: str = db.Column(db.String(80), nullable=False)
    email: str = db.Column(db.String(120), unique=True, nullable=True)
    phone: str = db.Column(db.String(20), nullable=True)
    is_field_engineer: bool = db.Column(db.Boolean, default=False, index=True)
    is_active: bool = db.Column(db.Boolean, default=True)
    created_at: datetime = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    attendance_records = db.relationship(
        "Attendance", backref="employee", lazy="dynamic", cascade="all, delete-orphan"
    )
    site_visits = db.relationship(
        "SiteVisit", backref="engineer", lazy="dynamic", cascade="all, delete-orphan"
    )

    @property
    def initials(self) -> str:
        """Return up to 2 uppercase initials from the employee's name."""
        parts = self.name.split()
        return "".join(p[0] for p in parts[:2]).upper()

    def __repr__(self) -> str:
        kind = "Engineer" if self.is_field_engineer else "Employee"
        return f"<{kind} {self.name!r}>"


# ──────────────────────────────────────────────
#  Attendance
# ──────────────────────────────────────────────

class Attendance(db.Model):
    """Daily attendance record for an office employee."""

    __tablename__ = "attendance"

    id: int = db.Column(db.Integer, primary_key=True)
    employee_id: int = db.Column(
        db.Integer, db.ForeignKey("employees.id"), nullable=False, index=True
    )
    date: date = db.Column(db.Date, default=date.today, nullable=False, index=True)
    check_in: str = db.Column(db.String(10), nullable=True)   # "HH:MM"
    check_out: str = db.Column(db.String(10), nullable=True)  # "HH:MM"
    status: str = db.Column(db.String(20), default="Present")  # Present | Absent | Leave | Half Day
    notes: str = db.Column(db.String(255), nullable=True)
    recorded_at: datetime = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def hours_worked(self) -> str:
        """Return formatted hours worked, e.g. '8h 30m'."""
        if not self.check_in or not self.check_out:
            return "—"
        try:
            fmt = "%H:%M"
            start = datetime.strptime(self.check_in, fmt)
            end = datetime.strptime(self.check_out, fmt)
            delta = end - start
            if delta.total_seconds() < 0:
                return "—"
            h, rem = divmod(int(delta.total_seconds()), 3600)
            m = rem // 60
            return f"{h}h {m:02d}m"
        except ValueError:
            return "—"

    def __repr__(self) -> str:
        return f"<Attendance emp={self.employee_id} date={self.date} status={self.status!r}>"


# ──────────────────────────────────────────────
#  SiteVisit
# ──────────────────────────────────────────────

class SiteVisit(db.Model):
    """Field engineer on-site visit record."""

    __tablename__ = "site_visits"

    id: int = db.Column(db.Integer, primary_key=True)
    engineer_id: int = db.Column(
        db.Integer, db.ForeignKey("employees.id"), nullable=False, index=True
    )
    site_name: str = db.Column(db.String(150), nullable=False)
    location: str = db.Column(db.String(255), nullable=True)
    date: date = db.Column(db.Date, default=date.today, nullable=False, index=True)
    arrival_time: str = db.Column(db.String(10), nullable=True)    # "HH:MM"
    departure_time: str = db.Column(db.String(10), nullable=True)  # "HH:MM"
    purpose: str = db.Column(db.String(200), nullable=True)
    notes: str = db.Column(db.String(500), nullable=True)
    recorded_at: datetime = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self) -> str:
        return f"<SiteVisit eng={self.engineer_id} site={self.site_name!r} date={self.date}>"
