"""Bloom FastAPI backend entry point."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import chat, hr


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    if settings.applicationinsights_connection_string:
        from azure.monitor.opentelemetry import configure_azure_monitor
        configure_azure_monitor(
            connection_string=settings.applicationinsights_connection_string,
        )
    yield


app = FastAPI(
    title="Bloom API",
    description="Women's health at work, powered by Microsoft Foundry",
    version="0.1.0",
    lifespan=lifespan,
)

settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(chat.router)
app.include_router(hr.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "bloom-backend"}
