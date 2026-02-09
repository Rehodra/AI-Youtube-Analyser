from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.routes import job, auth, test_db

app = FastAPI(title="YT Recommender Backend")

# Session Middleware (OAuth)
app.add_middleware(
    SessionMiddleware,
    secret_key="CHANGE_THIS_SECRET_IN_PRODUCTION",
    max_age=3600,
    same_site="lax",
    https_only=True,  # ✅ REQUIRED in production
)

# CORS Middleware (FIXED)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8000",
        "https://tubeintelligence-client.vercel.app",  # ✅ NO trailing slash
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router)
app.include_router(job.router)
app.include_router(test_db.router, prefix="/api")



# Optional startup/shutdown events can be added here
