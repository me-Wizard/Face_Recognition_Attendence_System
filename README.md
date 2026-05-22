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



           