"""
Database Models - SQLAlchemy Models
NeuroPETRIX veritabanı modelleri
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional

Base = declarative_base()

class User(Base):
    """Kullanıcı Modeli"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    role = Column(String(20), default="user")  # admin, radiologist, clinician, technician, viewer
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reports = relationship("Report", back_populates="author")
    workflows = relationship("Workflow", back_populates="created_by_user")

class Patient(Base):
    """Hasta Modeli"""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    nash_id = Column(String(50), unique=True, index=True, nullable=False)  # Anonimleştirilmiş ID
    mrn = Column(String(50), unique=True, index=True)  # Medical Record Number
    age_group = Column(String(10))  # 0-18, 19-65, 65+
    gender = Column(String(10))
    study_type = Column(String(50), default="FDG-PET/CT")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    reports = relationship("Report", back_populates="patient")
    suv_trends = relationship("SUVTrend", back_populates="patient")

class Report(Base):
    """Rapor Modeli"""
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(50), unique=True, index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    status = Column(String(20), default="draft")  # draft, in_review, approved, finalized, archived
    report_type = Column(String(50), default="PET/CT")
    study_date = Column(DateTime)
    conclusion = Column(Text)
    findings = Column(JSON)
    recommendations = Column(JSON)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="reports")
    author = relationship("User", back_populates="reports")
    workflows = relationship("Workflow", back_populates="report")

class Workflow(Base):
    """Workflow Modeli"""
    __tablename__ = "workflows"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_id = Column(String(50), unique=True, index=True, nullable=False)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=False)
    current_status = Column(String(20), default="draft")
    template = Column(String(50), default="standard_report")
    steps = Column(JSON)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    report = relationship("Report", back_populates="workflows")
    created_by_user = relationship("User", back_populates="workflows")

class SUVTrend(Base):
    """SUV Trend Modeli"""
    __tablename__ = "suv_trends"
    
    id = Column(Integer, primary_key=True, index=True)
    log_id = Column(String(50), unique=True, index=True, nullable=False)
    patient_id = Column(Integer, ForeignKey("patients.id"), nullable=False)
    measurement_date = Column(DateTime, nullable=False)
    suv_max = Column(Float, nullable=False)
    suv_peak = Column(Float)
    suv_mean = Column(Float)
    location = Column(String(100))
    tracer_type = Column(String(20), default="FDG")
    confidence = Column(Float, default=0.0)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    patient = relationship("Patient", back_populates="suv_trends")

class FHIRReport(Base):
    """FHIR Rapor Modeli"""
    __tablename__ = "fhir_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    resource_id = Column(String(50), unique=True, index=True, nullable=False)
    patient_nash_id = Column(String(50), nullable=False)
    report_date = Column(DateTime, nullable=False)
    status = Column(String(20), default="final")
    category = Column(String(50))
    code = Column(String(20))
    subject = Column(JSON)
    performer = Column(JSON)
    result = Column(JSON)
    conclusion = Column(Text)
    fhir_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
class ComplianceReport(Base):
    """Compliance Rapor Modeli"""
    __tablename__ = "compliance_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(50), unique=True, index=True, nullable=False)
    report_date = Column(DateTime, nullable=False)
    standards = Column(JSON)  # List of standards
    overall_status = Column(String(20))
    compliance_score = Column(Float)
    checklists = Column(JSON)
    recommendations = Column(JSON)
    next_assessment = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

class PatentedModule(Base):
    """Patentli Modül Modeli"""
    __tablename__ = "patented_modules"
    
    id = Column(Integer, primary_key=True, index=True)
    module_id = Column(String(50), unique=True, index=True, nullable=False)
    module_name = Column(String(100), nullable=False)
    protection_level = Column(String(20))  # public, protected, confidential, patented
    patent_number = Column(String(50))
    license_key = Column(String(100))
    is_locked = Column(Boolean, default=False)
    access_restrictions = Column(JSON)
    metadata = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ClinicalVariation(Base):
    """Klinik Varyasyon Modeli"""
    __tablename__ = "clinical_variations"
    
    id = Column(Integer, primary_key=True, index=True)
    body_region = Column(String(50), nullable=False)
    variation_type = Column(String(20), nullable=False)  # physiological, pathological
    organ = Column(String(50), nullable=False)
    sentence_template = Column(Text, nullable=False)
    suv_max_placeholder = Column(String(20), default="{suv_max}")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AIIntegration(Base):
    """AI Entegrasyon Modeli"""
    __tablename__ = "ai_integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    interpretation_id = Column(String(50), unique=True, index=True, nullable=False)
    body_region = Column(String(50), nullable=False)
    organ = Column(String(50), nullable=False)
    variation_type = Column(String(20), nullable=False)
    suv_max = Column(Float, nullable=False)
    tracer_type = Column(String(20), default="FDG")
    patient_age_group = Column(String(10))
    clinical_goal = Column(String(100))
    icd_codes = Column(JSON)
    json_variation = Column(Text)
    gpt4all_comment = Column(Text)
    gemini_suggestion = Column(Text)
    final_interpretation = Column(Text)
    confidence_score = Column(Float)
    recommendations = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class SystemMetrics(Base):
    """Sistem Metrikleri Modeli"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    cpu_percent = Column(Float)
    memory_percent = Column(Float)
    disk_percent = Column(Float)
    network_io_sent_bytes = Column(Float)
    network_io_recv_bytes = Column(Float)
    process_count = Column(Integer)
    thread_count = Column(Integer)
    uptime_seconds = Column(Float)
    load_average = Column(JSON)
    requests_per_second = Column(Float)
    cache_hit_rate = Column(Float)
    gc_collections = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    """Audit Log Modeli"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String(50), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(String(50))
    details = Column(JSON)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    user = relationship("User")
