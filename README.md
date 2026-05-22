Phase 1 — MVP / Prototype Architecture (Python-Based)

                ┌────────────────────┐
                │   Mobile/Web App   │
                │  (Camera + UI)     │
                └─────────┬──────────┘
                          │
                          │ HTTP/API Request
                          ▼
                ┌────────────────────┐
                │   FastAPI Backend  │
                │  Main Application  │
                └─────────┬──────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ▼                 ▼                 ▼

┌────────────────┐ ┌────────────────┐ ┌────────────────┐
│ Face Detection │ │ Face Embedding │ │ Attendance     │
│ Haar Cascade   │ │ FaceNet        │ │ Management     │
└────────┬───────┘ └────────┬───────┘ └────────┬───────┘
         │                  │                  │
         └──────────┬───────┴──────────┬───────┘
                    ▼                  ▼

           ┌──────────────────┐   ┌──────────────────┐
           │ FAISS Vector DB  │   │ PostgreSQL DB    │
           │ Embedding Search │   │ Students & Logs  │
           └──────────────────┘   └──────────────────┘

MVP Stack (Prototype Phase)

FastAPI
→ backend APIs
OpenCV
→ image processing + camera handling
Haar Cascade
→ face detection/localization
FaceNet
→ embedding generation
FAISS
→ fast embedding matching
PostgreSQL
→ students + attendance records
CLAHE
→ brightness normalization
Cosine Similarity
→ embedding comparison


Purpose Of MVP

This phase is ONLY for:

✅ validating recognition quality
✅ testing attendance flow
✅ threshold tuning
✅ handling edge cases
✅ checking real-world performance
✅ validating UX

NOT final deployment architecture.


Phase 2 — Final Product Architecture (Standalone Mobile App)

             ┌────────────────────────┐
             │ Shared Tablet/Mobile   │
             │ Standalone Attendance  │
             └──────────┬─────────────┘
                        │
                        ▼
             ┌────────────────────────┐
             │ React Native / Flutter │
             │ UI + Camera Handling   │
             └──────────┬─────────────┘
                        │
                        ▼
             ┌────────────────────────┐
             │ MediaPipe Detection    │
             │ Mobile Face Detection  │
             └──────────┬─────────────┘
                        │
                        ▼
             ┌────────────────────────┐
             │ MobileFaceNet / ArcFace│
             │ TFLite / ONNX Runtime  │
             └──────────┬─────────────┘
                        │
                        ▼
             ┌────────────────────────┐
             │ Local Similarity Search│
             │ Cosine Similarity      │
             └──────────┬─────────────┘
                        │
                        ▼
             ┌────────────────────────┐
             │ SQLite Local Database  │
             │ Attendance + Embeddings│
             └────────────────────────┘


Final Product Stack (Production Phase)
React Native
or Flutter
→ mobile application
MediaPipe Face Detection
→ mobile-optimized face detection
MobileFaceNet / ArcFace
→ mobile embedding generation
TensorFlow Lite / ONNX Runtime
→ on-device inference engine
SQLite
→ local attendance database
Cosine Similarity
→ local embedding matching
Final Product Characteristics

✅ standalone mobile/tablet app
✅ no external server required
✅ no internet dependency
✅ one-time installation
✅ offline attendance support
✅ touchless attendance
✅ portable setup
✅ suitable for schools/offices/small businesses