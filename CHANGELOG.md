# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-10-20

### Added
- Admin login with Werkzeug password hashing
- Live dashboard with stats: present, absent, on-site engineers
- Daily attendance marking (Present, Absent, Leave, Half Day) with check-in/check-out times
- Hours-worked calculation per attendance record
- Date picker to view historical attendance records
- Delete attendance records
- Employee management: add/search/soft-delete office staff and field engineers
- Field engineer site visit logging with location, purpose, arrival/departure times
- Site visit status badges (On Site / Completed / Scheduled)
- Monthly reports with attendance % progress bars per employee
- Field engineer monthly visit history
- Responsive navigation with mobile hamburger menu
- Auto-dismissing flash messages
- Professional CSS design system with CSS variables
- `.gitignore`, `.env.example`, `config.py`, `Procfile`, `LICENSE`, `README.md`, `CONTRIBUTING.md`
- Environment-based configuration (no hardcoded secrets)
- Soft-delete for employees (preserves historical records)

---

[Unreleased]: https://github.com/gowthaman14082004-hash/attendance-tracker/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/gowthaman14082004-hash/attendance-tracker/releases/tag/v1.0.0
