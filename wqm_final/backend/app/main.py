from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="NFLNN-based Water Quality Prediction API",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": f"{settings.APP_NAME} is Running 🚀",
        "version": settings.APP_VERSION
    }


@app.get("/health", tags=["Health"])
async def health():
    return {
        "status": "Healthy"
    }