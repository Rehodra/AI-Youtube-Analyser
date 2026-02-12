import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings

from app.routes import job, auth, test_db

app = FastAPI(title="YT Recommender Backend")

FRONTEND_URL = settings.frontend_url
SESSION_SECRET = settings.jwt_secret_key or "dev-secret-key"

# Session Middleware (OAuth)
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    max_age=3600,
    same_site="lax",
    https_only=True, 
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        FRONTEND_URL,
        "http://localhost:5173",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Routers
app.include_router(auth.router)
app.include_router(job.router)
app.include_router(test_db.router, prefix="/api")
