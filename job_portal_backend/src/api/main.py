from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .auth import router as auth_router
from .jobs import router as jobs_router
from .applications import router as applications_router
from .profile import router as profile_router
from .notifications import router as notifications_router

app = FastAPI(
    title="IT Job Portal API",
    version="1.0.0",
    description="APIs for IT Job Portal - User registration, authentication, and job functionalities."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(jobs_router)
app.include_router(applications_router)
app.include_router(profile_router)
app.include_router(notifications_router)

@app.get("/")
def health_check():
    """Health check endpoint for the API."""
    return {"message": "Healthy"}
