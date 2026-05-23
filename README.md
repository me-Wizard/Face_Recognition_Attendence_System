# Face Attendance System

A modular real-time face recognition and attendance tracking system,
built with FastAPI, OpenCV, DeepFace, and PostgreSQL.

---

## Tech Stack

- **FastAPI** — REST API framework
- **OpenCV** — webcam capture and image processing
- **DeepFace + FaceNet** — face embedding generation
- **PostgreSQL** — persistent storage
- **SQLAlchemy** — ORM and database sessions
- **NumPy** — cosine similarity matching

---

## Project Structure
face-attendance-system/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── routes/
│   │       ├── camera.py
│   │       ├── detect.py
│   │       ├── enroll.py
│   │       ├── recognize.py
│   │       └── attendance.py
│   ├── core/
│   │   ├── camera.py
│   │   ├── detector.py
│   │   ├── image_utils.py
│   │   ├── embedding.py
│   │   ├── matcher.py
│   │   └── quality.py
│   ├── services/
│   │   ├── detection_service.py
│   │   ├── enrollment_service.py
│   │   ├── recognition_service.py
│   │   └── attendance_service.py
│   └── db/
│       ├── connection.py
│       ├── models.py
│       └── crud.py
├── .env
├── requirements.txt
└── README.md

---

## Setup

**1. Create environment**
```bash
conda create -n attendance python=3.10 -y
conda activate attendance
pip install -r requirements.txt
```

**2. Create database**
```sql
CREATE DATABASE face_attendance;
```

**3. Configure `.env`**
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/face_attendance
```

**4. Start server**
```bash
uvicorn app.main:app --reload
```

All tables are auto-created on startup.

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | System info and version |
| GET | `/camera/start` | Start live detection loop |
| GET | `/detect/status` | Current detection state |
| POST | `/enroll/start` | Enroll a new person |
| GET | `/enroll/{employee_id}` | Check enrollment status |
| DELETE | `/enroll/{employee_id}` | Remove a person |
| POST | `/recognize` | Single-shot recognition |
| GET | `/recognize/start` | Start live recognition + attendance loop |
| GET | `/attendance/today` | Get today's attendance records |
| GET | `/attendance/status` | Get attendance system state |
| GET | `/docs` | Swagger UI |

---

## Enrollment Request

```json
{
  "name": "John Doe",
  "employee_id": "EMP-001",
  "department": "Engineering"
}
```

## Recognition Response

```json
{
  "matched": true,
  "name": "John Doe",
  "employee_id": "EMP-001",
  "department": "Engineering",
  "confidence": 0.85
}
```

## Attendance Responses

**Marked successfully:**
```json
{
  "status": "success",
  "message": "Attendance Marked",
  "name": "John Doe",
  "employee_id": "EMP-001",
  "confidence": 0.85
}
```

**Already marked today:**
```json
{
  "status": "exists",
  "message": "Already Marked Present",
  "name": "John Doe",
  "employee_id": "EMP-001",
  "confidence": 0.85
}
```

**Unknown face:**
```json
{
  "status": "failed",
  "message": "Unknown User"
}
```

---

## Database Schema
users
─────────────────────────────────────────
id            UUID        primary key
name          VARCHAR
employee_id   VARCHAR     unique
department    VARCHAR
enrolled_at   TIMESTAMP
embeddings
─────────────────────────────────────────
id            INTEGER     primary key
user_id       UUID        FK → users.id
vector        JSONB       128-D FaceNet vector
sample_idx    INTEGER     1–5
created_at    TIMESTAMP
attendance
─────────────────────────────────────────
id            INTEGER     primary key
user_id       UUID        FK → users.id
date          DATE
time          TIME
status        VARCHAR     e.g. "present"
created_at    TIMESTAMP

---

## Attendance Flow
camera frame
↓
face detection
↓
embedding generation
↓
recognition matching
↓
stable recognition (5 consecutive frames)
↓
cooldown check (15 second window)
↓
duplicate check (once per day)
↓
mark attendance in DB
↓
display result on camera overlay

---

## Camera Overlay States

| State | Overlay Text | Box Color |
|---|---|---|
| Accumulating frames | `Recognized (N/5)` | Green |
| Attendance marked | `Attendance Marked` | Cyan |
| Already marked today | `Already Marked Present` | Orange |
| Not recognized | `Unknown` | Red |

---

## Recognition Settings

| Setting | Value |
|---|---|
| Similarity threshold | 0.65 |
| Embeddings per user | 5 |
| Max faces per frame | 3 |
| Embedding model | FaceNet (128-D) |
| Stable frames required | 5 consecutive |
| Cooldown after marking | 15 seconds |
| Attendance per day | Once per user |

---

## System Phases

| Phase | Feature |
|---|---|
| Phase 1 | Haar Cascade face detection |
| Phase 2 | FaceNet enrollment with PostgreSQL |
| Phase 3 | Cosine similarity recognition |
| Phase 4 | Attendance management with duplicate prevention |

---

## Usage Flow

Enroll a person     →  POST /enroll/start
Start recognition   →  GET  /recognize/start
Face detected       →  system counts 5 stable frames
Attendance marked   →  overlay shows "Attendance Marked"
Check records       →  GET  /attendance/today

