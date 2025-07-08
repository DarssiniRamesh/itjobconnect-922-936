from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from src.database import SessionLocal
from src.models import Application, Job, User, UserRole
from .auth import get_current_user

router = APIRouter(
    prefix="/applications",
    tags=["Applications"]
)

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----- Schemas -----

class ApplicationCreateRequest(BaseModel):
    job_id: int = Field(..., description="The job ID the user is applying to")
    cover_letter: Optional[str] = Field(None, description="Optional cover letter for the job application")

class ApplicationResponse(BaseModel):
    id: int
    job_id: int
    user_id: int
    applied_at: datetime
    cover_letter: Optional[str]

    class Config:
        orm_mode = True

class EmployerApplicationResponse(BaseModel):
    id: int
    job_id: int
    user_id: int
    applied_at: datetime
    cover_letter: Optional[str]
    applicant_name: Optional[str]
    applicant_email: Optional[str]

    class Config:
        orm_mode = True

# ----- Helpers -----

def job_seeker_required(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.JOB_SEEKER:
        raise HTTPException(status_code=403, detail="Job seekers only.")
    return current_user

def employer_required(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.EMPLOYER:
        raise HTTPException(status_code=403, detail="Employers only.")
    return current_user

# ----- Endpoints -----

# PUBLIC_INTERFACE
@router.post(
    "/",
    summary="Apply to a job (Job seeker only)",
    response_model=ApplicationResponse,
    status_code=status.HTTP_201_CREATED,
)
def apply_to_job(
    req: ApplicationCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(job_seeker_required),
):
    """
    Apply to a job. Job seekers can apply once per job.
    """
    # Check job exists
    job = db.query(Job).filter(Job.id == req.job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    # Prevent employer from applying to their own posting
    if job.employer_id == current_user.id:
        raise HTTPException(status_code=403, detail="Cannot apply to your own job posting.")
    existing = db.query(Application).filter(Application.user_id == current_user.id, Application.job_id == req.job_id).first()
    if existing:
        raise HTTPException(status_code=409, detail="Already applied to this job.")
    app = Application(
        job_id=req.job_id,
        user_id=current_user.id,
        cover_letter=req.cover_letter,
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return app

# PUBLIC_INTERFACE
@router.get(
    "/my",
    summary="Get current job seeker's applications/status",
    response_model=List[ApplicationResponse]
)
def my_applications(
    db: Session = Depends(get_db),
    current_user: User = Depends(job_seeker_required),
):
    """
    List all job applications made by the current job seeker.
    """
    apps = db.query(Application).filter(Application.user_id == current_user.id).order_by(Application.applied_at.desc()).all()
    return apps

# PUBLIC_INTERFACE
@router.get(
    "/employer",
    summary="Employer: List job applications received for my jobs",
    response_model=List[EmployerApplicationResponse]
)
def employer_applications(
    job_id: Optional[int] = Query(None, description="Filter by a specific job ID"),
    db: Session = Depends(get_db),
    current_user: User = Depends(employer_required),
):
    """
    List applications to employer's jobs. Optionally filter by job_id.
    """
    query = db.query(Application).join(Job).filter(Job.employer_id == current_user.id)
    if job_id:
        query = query.filter(Application.job_id == job_id)
    results = query.order_by(Application.applied_at.desc()).all()
    # Attach applicant info for employer
    resp = []
    for app in results:
        resp.append(EmployerApplicationResponse(
            id=app.id,
            job_id=app.job_id,
            user_id=app.user_id,
            applied_at=app.applied_at,
            cover_letter=app.cover_letter,
            applicant_name=app.user.full_name if getattr(app.user, "full_name", None) else None,
            applicant_email=app.user.email if getattr(app.user, "email", None) else None,
        ))
    return resp

# PUBLIC_INTERFACE
@router.get(
    "/{application_id}",
    summary="Get detailed info for a specific application (owner or employer)",
    response_model=EmployerApplicationResponse,
)
def application_info(
    application_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    View application detail. Only the job seeker who applied or the employer who posted the job can access.
    """
    app = db.query(Application).filter(Application.id == application_id).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found.")
    # Permission check
    if current_user.role == UserRole.JOB_SEEKER:
        if app.user_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not allowed.")
    elif current_user.role == UserRole.EMPLOYER:
        if app.job.employer_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not allowed.")
    else:
        raise HTTPException(status_code=403, detail="Invalid role.")
    return EmployerApplicationResponse(
        id=app.id,
        job_id=app.job_id,
        user_id=app.user_id,
        applied_at=app.applied_at,
        cover_letter=app.cover_letter,
        applicant_name=app.user.full_name if getattr(app.user, "full_name", None) else None,
        applicant_email=app.user.email if getattr(app.user, "email", None) else None,
    )

# Optionally: in future employers may want to update or delete applications; Not implemented for MVP
