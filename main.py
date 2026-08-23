from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from config import settings
from routers.contact import router as contact_router, limiter
from routers.auth import router as auth_router
from routers.agents import router as agents_router
from database import engine
from models.base import Base

app = FastAPI(
    title="Signal Backend API",
    description="FastAPI service handling contact form processing, Turnstile, email, auth, database, and AI agent APIs.",
    version="1.0.0"
)

# Register slowapi rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register endpoints
app.include_router(contact_router)
app.include_router(auth_router)
app.include_router(agents_router)

@app.on_event("startup")
async def startup_event():
    # Only suitable for dev. In prod use Alembic migrations.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def root():
    return {
        "status": "online",
        "service": "Signal FastAPI Backend",
        "endpoints": ["POST /api/contact"]
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=True)
