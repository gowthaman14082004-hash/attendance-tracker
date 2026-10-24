# 🏢 Attendance Tracker

> **V Secure Technologies — Attendance & Field Tracking System**
> A clean, production-ready Flask web application for tracking office employee attendance and field engineer site visits.

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0.3-000000?logo=flask&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-D71F00?logo=sqlalchemy&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 **Secure Login** | Admin authentication with hashed passwords via Werkzeug |
| 📊 **Live Dashboard** | Real-time overview of present/absent staff and field engineer status |
| ✅ **Attendance Tracking** | Mark daily check-in/check-out with status (Present, Absent, Leave, Half Day) |
| 📍 **Field Engineer Visits** | Log site visits with location, arrival/departure times, and purpose |
| 👥 **Employee Management** | Add, search, and soft-delete office staff and field engineers |
| 📈 **Monthly Reports** | Attendance percentage per employee, visit history, and summary stats |
| 📱 **Responsive Design** | Works on desktop, tablet, and mobile |

---

## 🛠️ Tech Stack

- **Backend**: Python 3.10+, Flask 3.0, Flask-Login, Flask-SQLAlchemy
- **Database**: SQLite (default) / PostgreSQL (production)
- **Frontend**: Jinja2 templates, custom CSS (Inter font, CSS variables)
- **Auth**: Werkzeug password hashing
- **Deploy**: Gunicorn + Render / Heroku

---

## 🚀 Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/gowthaman14082004-hash/attendance-tracker.git
cd attendance-tracker
```

### 2. Create a virtual environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

```bash
cp .env.example .env
# Edit .env and set your SECRET_KEY
```

### 5. Run the app

```bash
flask run
```

Open [http://localhost:5000](http://localhost:5000) and sign in with:
- **Username**: `admin`
- **Password**: `admin123`

> ⚠️ Change the default password immediately in production.

---

## 📁 Project Structure

```
attendance-tracker/
├── app.py               # Flask app (routes, factory)
├── models.py            # SQLAlchemy models
├── config.py            # Environment-based configuration
├── requirements.txt     # Pinned dependencies
├── Procfile             # Gunicorn deployment
├── .env.example         # Environment variable template
├── .gitignore
├── LICENSE
├── static/
│   └── style.css        # Custom design system
└── templates/
    ├── base.html        # Layout with nav & footer
    ├── login.html       # Sign-in page
    ├── dashboard.html   # Overview & quick actions
    ├── attendance.html  # Mark & view attendance
    ├── employees.html   # Manage staff
    ├── engineers.html   # Field engineer site visits
    └── reports.html     # Monthly reports
```

---

## 🌐 Deployment

### Deploy to Render (Free Tier)

1. Push your code to GitHub
2. Go to [render.com](https://render.com) → **New Web Service**
3. Connect your GitHub repo
4. Set these environment variables in Render dashboard:
   - `SECRET_KEY` — a long random string
   - `FLASK_ENV` — `production`
5. Render will automatically detect the `Procfile` and deploy

### Manual (Gunicorn)

```bash
gunicorn app:app --workers 2 --bind 0.0.0.0:$PORT
```

---

## 🗄️ Database Models

| Model | Description |
|-------|-------------|
| `User` | Login accounts (admin / employee) |
| `Employee` | Office staff and field engineers |
| `Attendance` | Daily attendance records |
| `SiteVisit` | Field engineer on-site visit log |

---

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">
  Built with ❤️ by <a href="https://github.com/gowthaman14082004-hash">gowthaman14082004-hash</a>
</div>
