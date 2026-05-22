"""
app/services/attendance_service.py
------------------------------------
PLACEHOLDER — Attendance recording service.

Future implementation will:
- Accept a recognised identity_id from the matcher.
- Check if the person has already been marked present today.
- Write an attendance record to the database via db/connection.py.
- Enforce configurable cooldown periods (e.g., mark once per 30 minutes).
- Expose functions for querying daily attendance reports.

TODO:
    - mark_present(identity_id: str, timestamp: datetime) -> bool
    - is_already_marked(identity_id: str, date: date) -> bool
    - get_daily_report(date: date) -> list[AttendanceRecord]
"""
