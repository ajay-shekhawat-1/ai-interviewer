from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.resume import router as resume_router
from app.api.jd import router as jd_router
from app.api.candidate import router as candidate_router
from app.api.interview import router as interview_router
from app.api import questions
from app.api import session
from app.api import evaluation
from app.api import adaptive
from app.api.voice import router as voice_router
from app.api.candidate_profile import router as candidate_profile_router

from app.core.config import get_settings

from app.db.database import Base, engine
from app.db import models


settings = get_settings()


# ---------------------------------------------------------
# DATABASE
# ---------------------------------------------------------

Base.metadata.create_all(bind=engine)


# ---------------------------------------------------------
# APPLICATION
# ---------------------------------------------------------

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Backend API for the AI Interviewer platform.",
)


# ---------------------------------------------------------
# CORS
# ---------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


# ---------------------------------------------------------
# ROUTERS
# ---------------------------------------------------------

app.include_router(resume_router)
app.include_router(jd_router)
app.include_router(candidate_router)
app.include_router(interview_router)
app.include_router(questions.router)
app.include_router(session.router)
app.include_router(evaluation.router)
app.include_router(adaptive.router)
app.include_router(candidate_profile_router)
app.include_router(voice_router)


# ---------------------------------------------------------
# ROOT ENDPOINT
# ---------------------------------------------------------

@app.get("/", tags=["System"])
async def root() -> dict[str, str]:
    return {
        "message": "AI Interviewer API is running",
        "version": settings.app_version,
        "environment": settings.environment,
    }


# ---------------------------------------------------------
# HEALTH ENDPOINT
# ---------------------------------------------------------

@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    return {
        "status": "healthy",
    }