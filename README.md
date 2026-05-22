# Face Attendance System

Real-time face detection system built with **FastAPI** + **OpenCV**.  
Designed with a strict modular architecture so embedding, FAISS matching, and database attendance recording can be added incrementally without refactoring existing code.

---

## Features (Phase 1 — Detection)

| Feature | Status |
|---|---|
| Webcam capture via OpenCV | ✅ |
| Grayscale conversion | ✅ |
| CLAHE brightness normalisation | ✅ |
| Haar Cascade face detection | ✅ |
| Bounding box drawing | ✅ |
| "Face Detected / No Face Detected" status | ✅ |
| Zoomed crop window per face | ✅ |
| Exit loop with `q` key | ✅ |
| `/camera/start` API endpoint | ✅ |
| `/detect/status` API endpoint | ✅ |

---

## Project Structure

```
face-attendance-system/
├── app/
│   ├── main.py                        # FastAPI app factory, router registration
│   │
│   ├── api/
│   │   └── routes/
│   │       ├── camera.py              # GET /camera/start
│   │       ├── detect.py              # GET /detect/status
│   │       ├── enroll.py              # PLACEHOLDER — enrollment
│   │       └── recognize.py           # PLACEHOLDER — recognition
│   │
│   ├── core/
│   │   ├── camera.py                  # Camera class (open / read / release)
│   │   ├── detector.py                # FaceDetector (Haar Cascade)
│   │   ├── image_utils.py             # CLAHE, draw boxes, crop faces
│   │   ├── embedding.py               # PLACEHOLDER — face embeddings
│   │   └── matcher.py                 # PLACEHOLDER — FAISS matching
│   │
│   ├── services/
│   │   ├── detection_service.py       # Orchestrates the full detection loop
│   │   └── attendance_service.py      # PLACEHOLDER — attendance recording
│   │
│   └── db/
│       ├── connection.py              # PLACEHOLDER — DB engine & sessions
│       └── models.py                  # PLACEHOLDER — ORM models
│
├── requirements.txt
└── README.md
```

---

## Quickstart

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the API server

```bash
uvicorn app.main:app --reload
```

### 3. Open interactive API docs

```
http://127.0.0.1:8000/docs
```

### 4. Start face detection

```bash
curl http://127.0.0.1:8000/camera/start
```

An OpenCV window titled **"Face Detection — Press 'q' to quit"** will open.  
A second window per face (e.g. **"Face 1"**) shows the cropped 200×200 region.  
Press **`q`** inside the OpenCV window to stop.

### 5. Check detection status

```bash
curl http://127.0.0.1:8000/detect/status
```

Example response:

```json
{
  "running": true,
  "face_detected": true,
  "face_count": 1,
  "status_label": "Face Detected"
}
```

---

## API Reference

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/` | System info |
| `GET` | `/camera/start` | Start detection loop (background thread) |
| `GET` | `/detect/status` | Live detection state snapshot |
| `GET` | `/docs` | Swagger UI |

---

## Frame Processing Pipeline

```
Webcam frame (BGR)
       │
       ▼
 to_grayscale()          → single-channel H×W array
       │
       ▼
 apply_clahe()           → brightness-normalised grayscale
       │
       ▼
 FaceDetector.detect()   → list of (x, y, w, h) bounding boxes
       │
       ▼
 draw_bounding_boxes()   → annotated BGR frame  ─────────► imshow("Face Detection")
       │
       ▼
 show_cropped_faces()    → 200×200 crops        ─────────► imshow("Face N")
```

---

## Architecture Rules

- **Routes** contain zero OpenCV or business logic — they call services only.  
- **Services** orchestrate core modules — they own the processing loop.  
- **Core modules** are pure functions / classes with no cross-module imports.  
- **DB and embedding modules** are empty placeholders with full docstrings.

---

## Scaling Roadmap

```
Phase 1 (current)   Detection only
Phase 2             Add embedding.py → extract 128-D face vectors
Phase 3             Add matcher.py   → FAISS nearest-neighbour search
Phase 4             Add db/          → SQLAlchemy + PostgreSQL
Phase 5             Add enroll.py    → Register students via API
Phase 6             Add recognize.py → Full attendance marking pipeline
```

---

## Detection Parameters

Tunable in `app/core/detector.py`:

| Parameter | Value | Effect |
|---|---|---|
| `scaleFactor` | `1.1` | 10 % image pyramid reduction per level |
| `minNeighbors` | `6` | Higher = fewer false positives |
| `minSize` | `(60, 60)` | Ignore faces smaller than 60×60 px |
| `MAX_FACES` | `3` | Cap detections to 3 per frame |

CLAHE parameters in `app/core/image_utils.py`:

| Parameter | Value |
|---|---|
| `clipLimit` | `2.0` |
| `tileGridSize` | `(8, 8)` |
