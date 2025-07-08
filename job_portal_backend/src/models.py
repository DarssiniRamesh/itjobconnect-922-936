from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

import enum

class UserRole(str, enum.Enum):
    JOB_SEEKER = "job_seeker"
    EMPLOYER = "employer"

# PUBLIC_INTERFACE
class User(Base):
    """User model representing job seekers and employers."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(64), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(Enum(UserRole), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    jobs = relationship("Job", back_populates="employer", cascade="all, delete")
    applications = relationship("Application", back_populates="user", cascade="all, delete")


# PUBLIC_INTERFACE
class Job(Base):
    """Job model representing IT job postings."""

    __tablename__ = "jobs"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    location = Column(String(255))
    company = Column(String(255))
    posted_at = Column(DateTime, default=datetime.utcnow)
    employer_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    employer = relationship("User", back_populates="jobs", lazy='joined')
    applications = relationship("Application", back_populates="job", cascade="all, delete")


# PUBLIC_INTERFACE
class Application(Base):
    """Application model for job applications linked to users and jobs."""

    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    applied_at = Column(DateTime, default=datetime.utcnow)
    cover_letter = Column(Text)

    user = relationship("User", back_populates="applications")
    job = relationship("Job", back_populates="applications")
