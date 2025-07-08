from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from src.database import SessionLocal
from src.models import Job, User, UserRole
from .auth import get_current_user

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"]
)

# Dependency for DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ---------- Schemas ----------

class JobBaseSchema(BaseModel):
    title: str = Field(..., description="Job title")
    description: Optional[str] = Field(None, description="Job description")
    location: Optional[str] = Field(None, description="Job location/city/remote")
    company: Optional[str] = Field(None, description="Company name")

class JobCreateSchema(JobBaseSchema):
    pass

class JobUpdateSchema(BaseModel):
    title: Optional[str]
    description: Optional[str]
    location: Optional[str]
    company: Optional[str]

class EmployerJobResponse(JobBaseSchema):
    id: int
    posted_at: datetime

    class Config:
        orm_mode = True

class PublicJobResponse(JobBaseSchema):
    id: int
    posted_at: datetime
    employer_id: int
    employer_name: Optional[str] = None

    class Config:
        orm_mode = True

# ----------- Helpers/Permissions -----------

def employer_required(current_user: User = Depends(get_current_user)):
    if current_user.role != UserRole.EMPLOYER:
        raise HTTPException(status_code=403, detail="Employers only.")
    return current_user

# ----------- API Endpoints -----------

# PUBLIC_INTERFACE
@router.post(
    "/",
    summary="Create a new job posting (Employer only)",
    response_model=EmployerJobResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_job(
    job: JobCreateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(employer_required),
):
    """
    Create a new job posting. Only accessible by employers.
    """
    new_job = Job(
        title=job.title,
        description=job.description,
        location=job.location,
        company=job.company,
        employer_id=current_user.id,
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    return new_job

# PUBLIC_INTERFACE
@router.put(
    "/{job_id}",
    summary="Update a job posting (Employer only)",
    response_model=EmployerJobResponse
)
def update_job(
    job_id: int,
    job_update: JobUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(employer_required)
):
    """
    Update a job posting. Employer must own the job.
    """
    job = db.query(Job).filter(Job.id == job_id, Job.employer_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or not owned by employer.")
    for attr, value in job_update.dict(exclude_unset=True).items():
        setattr(job, attr, value)
    db.commit()
    db.refresh(job)
    return job

# PUBLIC_INTERFACE
@router.delete(
    "/{job_id}",
    summary="Delete a job posting (Employer only)",
    status_code=status.HTTP_204_NO_CONTENT
)
def delete_job(
    job_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(employer_required)
):
    """
    Delete a job posting. Employer must own the job.
    """
    job = db.query(Job).filter(Job.id == job_id, Job.employer_id == current_user.id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or not owned by employer.")
    db.delete(job)
    db.commit()
    return

# PUBLIC_INTERFACE
@router.get(
    "/",
    summary="List and filter/search available jobs",
    response_model=List[PublicJobResponse]
)
def list_jobs(
    title: Optional[str] = Query(None, description="Filter by job title"),
    company: Optional[str] = Query(None, description="Filter by company name"),
    location: Optional[str] = Query(None, description="Filter by job location"),
    keywords: Optional[str] = Query(None, description="Search by keyword in title/desc"),
    db: Session = Depends(get_db),
):
    """
    List jobs, with optional filtering and search parameters.
    """
    jobs_query = db.query(Job)
    if title:
        jobs_query = jobs_query.filter(Job.title.ilike(f"%{title}%"))
    if company:
        jobs_query = jobs_query.filter(Job.company.ilike(f"%{company}%"))
    if location:
        jobs_query = jobs_query.filter(Job.location.ilike(f"%{location}%"))
    if keywords:
        keyword_pattern = f"%{keywords}%"
        jobs_query = jobs_query.filter(
            (Job.title.ilike(keyword_pattern)) | (Job.description.ilike(keyword_pattern))
        )
    jobs = jobs_query.order_by(Job.posted_at.desc()).all()
    # Attach employer_name manually
    result = []
    for j in jobs:
        employer_name = j.employer.full_name if j.employer and j.employer.full_name else None
        result.append(PublicJobResponse(
            id=j.id,
            title=j.title,
            description=j.description,
            location=j.location,
            company=j.company,
            posted_at=j.posted_at,
            employer_id=j.employer_id,
            employer_name=employer_name,
        ))
    return result

# PUBLIC_INTERFACE
@router.get(
    "/{job_id}",
    summary="Get job details by ID",
    response_model=PublicJobResponse
)
def get_job(job_id: int, db: Session = Depends(get_db)):
    """
    Retrieve detailed information for a specific job by ID.
    """
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    employer_name = job.employer.full_name if job.employer and job.employer.full_name else None
    return PublicJobResponse(
        id=job.id,
        title=job.title,
        description=job.description,
        location=job.location,
        company=job.company,
        posted_at=job.posted_at,
        employer_id=job.employer_id,
        employer_name=employer_name,
    )
