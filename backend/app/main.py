from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.api.resume import router as resume_router
from app.core.config import get_settings
from app.llm.groq_client import (
    get_groq_client,
    get_groq_model,
)
from app.api.jd import router as jd_router

settings = get_settings()


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
# Routers
# ---------------------------------------------------------

app.include_router(resume_router)
app.include_router(jd_router)


# ---------------------------------------------------------
# Root endpoint
# ---------------------------------------------------------

@app.get("/", tags=["System"])
async def root() -> dict[str, str]:
    """
    Basic API information endpoint.
    """

    return {
        "message": "AI Interviewer API is running",
        "version": settings.app_version,
        "environment": settings.environment,
    }


# ---------------------------------------------------------
# Health endpoint
# ---------------------------------------------------------

@app.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    """
    Health check endpoint used by monitoring and deployment platforms.
    """

    return {
        "status": "healthy",
    }


# ---------------------------------------------------------
# Temporary Groq Test Endpoint
# ---------------------------------------------------------

@app.get("/test-groq", tags=["Development"])
async def test_groq() -> dict[str, str]:
    """
    Temporary endpoint used to verify Groq connectivity.
    """

    client = get_groq_client()
    model = get_groq_model()

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": "Reply with exactly: Groq connection successful",
            }
        ],
        temperature=0,
        max_tokens=20,
    )

    message = response.choices[0].message.content

    return {
        "status": "success",
        "model": model,
        "message": message or "",
    }


# ---------------------------------------------------------
# Temporary Groq Model List Endpoint
# ---------------------------------------------------------

@app.get("/test-groq-models", tags=["Development"])
async def test_groq_models() -> dict:
    """
    Temporary development endpoint that lists models
    available to the configured Groq API key.
    """

    try:
        client = get_groq_client()

        models = client.models.list()

        return {
            "status": "success",
            "models": [
                {
                    "id": model.id,
                    "active": model.active,
                }
                for model in models.data
            ],
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Unable to retrieve Groq models: {str(exc)}",
        ) from exc