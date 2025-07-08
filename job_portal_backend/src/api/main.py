from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from .auth import router as auth_router
from .jobs import router as jobs_router
from .applications import router as applications_router
from .profile import router as profile_router
from .notifications import router as notifications_router

# CORS: Only allow frontend domains. Set via env or edit list below.
# For localhost/preview, http://localhost:3000 and the Kavia preview domain are safe defaults.
ALLOWED_ORIGINS = [
    os.getenv("FRONTEND_URL", "http://localhost:3000"),
    "https://vscode-internal-61188-beta.beta01.cloud.kavia.ai:3000"
]

app = FastAPI(
    title="IT Job Portal API",
    version="1.0.0",
    description="""
    IT Job Portal API

    This REST API serves job seekers and employers in the IT sector.
    - **Authentication & Registration**
    - **Job Search, Post, Update, Delete**
    - **Apply to Jobs**
    - **Employer Dashboard**
    - **User Profiles**
    - **Notifications (MVP: placeholder endpoint)**

    Fully documented for frontend system consumption.
    """,
    contact={
        "name": "IT Job Portal Support",
        "email": "support@itjobconnect.com"
    },
    openapi_tags=[
        {"name": "Authentication", "description": "Register, login, JWT management."},
        {"name": "Jobs", "description": "Job posting, search, and details (public & employer-specific)."},
        {"name": "Applications", "description": "Apply to jobs, track/applications for users and employers."},
        {"name": "Profile", "description": "Manage and view user profiles."},
        {"name": "Notifications", "description": "Notification system (future/full version)."}
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register all routers with explicit tags for auto-grouping in docs
app.include_router(auth_router)
app.include_router(jobs_router)
app.include_router(applications_router)
app.include_router(profile_router)
app.include_router(notifications_router)

@app.get(
    "/", 
    tags=["Utility"], 
    summary="Health check", 
    description="Use this endpoint to verify the API is running."
)
def health_check():
    """Health check endpoint for the API. Returns {"message": "Healthy"} if alive."""
    return {"message": "Healthy"}

