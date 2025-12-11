"""
SQLAlchemy models for project, and surveyor.
"""
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class SurveyorALS(Base):
    """Licensed surveyors in the system"""
    __tablename__ = "SurveyorALS"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    ftp_number = Column(String(50), nullable=True)
    city = Column(String(200), nullable=True)

    # Relationships
    projects = relationship("Project", back_populates="surveyor")


class Project(Base):
    """Projects being tracked in the system"""
    __tablename__ = "Project"

    id = Column(Integer, primary_key=True, index=True)
    proj_num = Column(String(100), nullable=False, unique=True)
    name = Column(String(300), nullable=False)
    surveyor_id = Column(Integer, ForeignKey("SurveyorALS.id"), nullable=True)
    municipality = Column(String(200), nullable=True)

    # Relationships
    surveyor = relationship("SurveyorALS", back_populates="projects")
    title_documents = relationship("TitleDocument", back_populates="project", cascade="all, delete-orphan")
    legal_documents = relationship("LegalDocument", back_populates="project", cascade="all, delete-orphan")
    document_tasks = relationship("DocumentTask", back_populates="project", cascade="all, delete-orphan")
