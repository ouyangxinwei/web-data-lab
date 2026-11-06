from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.health import router as health_router
from app.core.config import allowed_origins

app = FastAPI(title="Web Data Lab API", version="0.1.0", description="Backend service for API and HTML data collection experiments.")

# Restrict browser access to configured frontend origins; configure production explicitly.
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins(),
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)
app.include_router(health_router, prefix="/api")

@app.get("/")
def root():
    return {"name": "Web Data Lab API", "docs": "/docs", "health": "/api/health"}
