# Face Attendance System

An enterprise-grade AI-powered face recognition attendance platform with role-based access control, built with FastAPI, Next.js, OpenCV, and DeepFace.

---

## Tech Stack

### Backend
- **FastAPI** — REST API framework
- **OpenCV** — Webcam capture and image processing
- **DeepFace + FaceNet** — Face embedding generation
- **PostgreSQL** — Persistent storage
- **SQLAlchemy** — ORM and database sessions
- **NumPy** — Cosine similarity matching
- **Pandas** — CSV export
- **JWT + bcrypt** — Authentication

### Frontend
- **Next.js 14** — App Router
- **TypeScript** — Type safety
- **Tailwind CSS** — Styling
- **Framer Motion** — Animations
- **Recharts** — Analytics charts
- **Axios** — API communication

---

## Project Structure

Attencence_System/
├── Backend/
│   └── app/
│       ├── main.py
│       ├── api/
│       │   └── routes/
│       │       ├── auth.py
│       │       ├── camera.py
│       │       ├── detect.py
│       │       ├── enroll.py
│       │       ├── recognize.py
│       │       ├── attendance.py
│       │       └── system.py
│       ├── core/
│       │   ├── camera.py
│       │   ├── detector.py
│       │   ├── image_utils.py
│       │   ├── embedding.py
│       │   ├── matcher.py
│       │   └── quality.py
│       ├── services/
│       │   ├── auth_service.py
│       │   ├── detection_service.py
│       │   ├── enrollment_service.py
│       │   ├── recognition_service.py
│       │   └── attendance_service.py
│       └── db/
│           ├── connection.py
│           ├── models.py
│           └── crud.py
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── login/
│   │   │   ├── register/
│   │   │   ├── admin/
│   │   │   │   ├── dashboard/
│   │   │   │   ├── recognition/
│   │   │   │   ├── enrollment/
│   │   │   │   ├── attendance/
│   │   │   │   ├── analytics/
│   │   │   │   ├── system/
│   │   │   │   └── users/
│   │   │   └── user/
│   │   │       ├── dashboard/
│   │   │       ├── attendance/
│   │   │       ├── statistics/
│   │   │       ├── export/
│   │   │       └── profile/
│   │   ├── components/
│   │   │   ├── admin/
│   │   │   ├── user/
│   │   │   └── shared/
│   │   ├── context/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── types/
│   │   └── lib/
│   ├── package.json
│   └── .env.local
├── requirements.txt
├── .env
└── README.md
---

## Setup

### Prerequisites
- Python 3.10
- Node.js 18+
- PostgreSQL
- Conda

### 1. Create Database
```sql
CREATE DATABASE face_attendance;
```

### 2. Backend Setup
```bash
conda create -n attendance python=3.10 -y
conda activate attendance
cd Backend
pip install -r requirements.txt
```

Create `.env` file in `Backend/`:
```env
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/face_attendance
JWT_SECRET=your-secret-key-here
```

Start backend:
```bash
uvicorn app.main:app --reload
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

Create `.env.local` in `frontend/`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## First Time Usage

### 1. Create your first account
Go to `http://localhost:3000/register`

- Select **Admin** role for full access
- Select **User** role for personal attendance view only

### 2. Login
Go to `http://localhost:3000/login`

System automatically redirects based on role:
- Admin → `/admin/dashboard`
- User → `/user/dashboard`

---

## API Endpoints

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/auth/login` | Login and get JWT token |
| POST | `/auth/register` | Create new account |
| GET | `/auth/me` | Get current user |
| GET | `/auth/users` | List all accounts (admin only) |

### Enrollment
| Method | Endpoint | Description |
|---|---|---|
| POST | `/enroll/start` | Enroll new face |
| GET | `/enroll/{employee_id}` | Check enrollment |
| DELETE | `/enroll/{employee_id}` | Remove person |

### Recognition
| Method | Endpoint | Description |
|---|---|---|
| GET | `/recognize/start` | Start live recognition loop |
| POST | `/recognize` | Single frame recognition |

### Attendance
| Method | Endpoint | Description |
|---|---|---|
| GET | `/attendance/today` | Today's attendance |
| GET | `/attendance/history` | Paginated history with filters |
| GET | `/attendance/absent` | Users not present today |
| GET | `/attendance/export/csv` | Download CSV |
| GET | `/attendance/status` | System attendance state |

### System
| Method | Endpoint | Description |
|---|---|---|
| GET | `/system/status` | Live FPS, latency, stats |

---

## Role-Based Access

### Admin
- Enroll and remove users
- Start live recognition
- View all attendance records
- Export attendance CSV
- View analytics and charts
- Monitor system status
- Manage login accounts

### User
- View own attendance history
- View personal statistics
- Export own attendance
- View profile

---

## Attendance Flow

```
Camera Frame
     ↓
Face Detection (Haar Cascade)
     ↓
CLAHE Normalization
     ↓
FaceNet Embedding (128-D)
     ↓
Cosine Similarity Matching
     ↓
Stable Recognition (5 consecutive frames)
     ↓
Cooldown Check (15 seconds)
     ↓
Duplicate Check (once per day)
     ↓
Mark Attendance in PostgreSQL
     ↓
Live Overlay on Camera Feed
```

---

## Camera Overlay States

| State | Color |
|---|---|
| Accumulating frames (N/5) | Green |
| Attendance Marked | Cyan |
| Already Marked Present | Orange |
| Unknown | Red |

---

## Database Schema

```
users          — enrolled face users
embeddings     — 128-D FaceNet vectors (5 per user)
attendance     — attendance records
admin_users    — login accounts with roles
```

---

## Recognition Settings

| Setting | Value |
|---|---|
| Similarity threshold | 0.65 |
| Embeddings per user | 5 |
| Max faces per frame | 3 |
| Embedding model | FaceNet 128-D |
| Stable frames required | 5 |
| Cooldown after marking | 15 seconds |
| Attendance per day | Once per user |
| Frame skip rate | Every 3rd frame |

---

## System Phases

| Phase | Feature |
|---|---|
| Phase 1 | Haar Cascade face detection |
| Phase 2 | FaceNet enrollment with PostgreSQL |
| Phase 3 | Cosine similarity recognition |
| Phase 4 | Attendance management |
| Phase 5 | Dashboard, history, CSV export, FPS optimization |
| Phase 6 | Role-based auth, Admin and User panels |