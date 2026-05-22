"""
app/api/routes/recognize.py
----------------------------
PLACEHOLDER — Face recognition and attendance marking routes.

Future implementation will:
- Expose a GET /recognize/start endpoint.
- Run the full recognition pipeline:
    detect → embed → match → mark attendance.
- Stream results back to the client (SSE or WebSocket).
- Return recognised identity and confidence score per frame.

TODO:
    - GET  /recognize/start   — Begin recognition loop.
    - GET  /recognize/status  — Return last recognised identity.
    - POST /recognize/verify  — One-shot verification from uploaded image.
"""
