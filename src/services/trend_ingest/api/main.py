"""Lightweight app factory for trend ingestion.

This module avoids importing heavy dependencies at import time so the scaffold
can be inspected and syntax-checked without installing runtime packages.
"""

def create_app():
    try:
        from fastapi import FastAPI
    except Exception:
        # FastAPI not installed in this environment; return a simple placeholder
        class _DummyApp:
            def __init__(self):
                self._routes = {}
            def add_route(self, path, fn, methods=None):
                self._routes[path] = (fn, methods)
        return _DummyApp()

    app = FastAPI(title="Trend Ingest Service")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    @app.post("/ingest")
    async def ingest(payload: dict):
        # Ingestion logic implemented in services; this is a thin wrapper
        return {"status": "accepted"}

    return app


__all__ = ["create_app"]
