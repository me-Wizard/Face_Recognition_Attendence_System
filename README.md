# Face Attendance System

A modular real-time face recognition system for attendance tracking,
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
│   │       └── recognize.py
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

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/camera/start` | Start live detection loop |
| GET | `/detect/status` | Current detection state |
| POST | `/enroll/start` | Enroll a new person |
| GET | `/enroll/{employee_id}` | Check enrollment |
| DELETE | `/enroll/{employee_id}` | Remove a person |
| POST | `/recognize` | Single-shot recognition |
| GET | `/recognize/start` | Start live recognition loop |
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

---

## Database Schema
users
id, name, employee_id, department, enrolled_at
embeddings
id, user_id (FK), vector (JSONB 128-D), sample_idx, created_at

---

## Recognition Settings

| Setting | Value |
|---|---|
| Similarity threshold | 0.65 |
| Embeddings per user | 5 |
| Max faces per frame | 3 |
| Embedding model | FaceNet (128-D) |

---