"""
Database Configuration and Models
Veritabanı konfigürasyonu ve modelleri
"""

import asyncio
import asyncpg
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from typing import Optional, List, Dict, Any
import uuid
import logging

logger = logging.getLogger(__name__)

# Database URL
DATABASE_URL = "postgresql://neuropetrix:password@localhost:5432/neuropetrix"
ASYNC_DATABASE_URL = "postgresql+asyncpg://neuropetrix:password@localhost:5432/neuropetrix"

# SQLite fallback for development
SQLITE_URL = "sqlite:///./neuropetrix.db"
ASYNC_SQLITE_URL = "sqlite+aiosqlite:///./neuropetrix.db"

# Base class for models
Base = declarative_base()

# Database Models
class Patient(Base):
    """Hasta modeli"""
    __tablename__ = "patients"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(String(10), nullable=False)
    phone = Column(String(20), nullable=True)
    email = Column(String(100), nullable=True)
    address = Column(Text, nullable=True)
    medical_history = Column(Text, nullable=True)
    allergies = Column(JSON, nullable=True)
    emergency_contact = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)

class Report(Base):
    """Rapor modeli"""
    __tablename__ = "reports"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), nullable=False)
    report_type = Column(String(50), nullable=False)  # pet-ct, pet-mri, spect, other
    study_date = Column(DateTime, nullable=False)
    findings = Column(Text, nullable=False)
    impression = Column(Text, nullable=False)
    recommendations = Column(Text, nullable=True)
    attachments = Column(JSON, nullable=True)
    status = Column(String(20), default="draft")  # draft, completed, reviewed
    created_by = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SUVMeasurement(Base):
    """SUV ölçüm modeli"""
    __tablename__ = "suv_measurements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), nullable=False)
    report_id = Column(UUID(as_uuid=True), nullable=True)
    measurement_date = Column(DateTime, nullable=False)
    suv_max = Column(Float, nullable=False)
    suv_mean = Column(Float, nullable=False)
    suv_peak = Column(Float, nullable=True)
    lesion_location = Column(String(200), nullable=True)
    lesion_size = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ClinicalWorkflow(Base):
    """Klinik workflow modeli"""
    __tablename__ = "clinical_workflows"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    patient_id = Column(UUID(as_uuid=True), nullable=False)
    icd_code = Column(String(20), nullable=False)
    workflow_type = Column(String(50), nullable=False)
    status = Column(String(20), default="pending")  # pending, in_progress, completed, failed
    steps = Column(JSON, nullable=True)
    results = Column(JSON, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    created_by = Column(String(100), nullable=True)

class SystemMetrics(Base):
    """Sistem metrikleri modeli"""
    __tablename__ = "system_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime, default=datetime.utcnow)
    cpu_percent = Column(Float, nullable=False)
    memory_percent = Column(Float, nullable=False)
    memory_used_mb = Column(Float, nullable=False)
    memory_available_mb = Column(Float, nullable=False)
    disk_usage_percent = Column(Float, nullable=False)
    network_io = Column(JSON, nullable=True)
    active_connections = Column(Integer, nullable=False)
    response_time_ms = Column(Float, nullable=False)
    requests_per_second = Column(Float, nullable=False)
    cache_hit_rate = Column(Float, nullable=False)

class User(Base):
    """Kullanıcı modeli"""
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    full_name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    roles = Column(JSON, nullable=True)  # ["admin", "doctor", "technician"]
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLog(Base):
    """Audit log modeli"""
    __tablename__ = "audit_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50), nullable=False)
    resource_id = Column(String(100), nullable=True)
    details = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)

# Database Engine and Session
class DatabaseManager:
    """Veritabanı yöneticisi"""
    
    def __init__(self, database_url: str = None, async_url: str = None):
        self.database_url = database_url or SQLITE_URL
        self.async_url = async_url or ASYNC_SQLITE_URL
        self.engine = None
        self.async_engine = None
        self.SessionLocal = None
        self.AsyncSessionLocal = None
    
    def create_engines(self):
        """Engine'leri oluştur"""
        try:
            # Sync engine
            self.engine = create_engine(
                self.database_url,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=300
            )
            
            # Async engine
            self.async_engine = create_async_engine(
                self.async_url,
                echo=False,
                pool_pre_ping=True,
                pool_recycle=300
            )
            
            # Session makers
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            self.AsyncSessionLocal = sessionmaker(
                self.async_engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            
            logger.info("Database engines created successfully")
            
        except Exception as e:
            logger.error(f"Database engine creation failed: {e}")
            raise
    
    def create_tables(self):
        """Tabloları oluştur"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Table creation failed: {e}")
            raise
    
    async def create_tables_async(self):
        """Async tablo oluşturma"""
        try:
            async with self.async_engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully (async)")
        except Exception as e:
            logger.error(f"Async table creation failed: {e}")
            raise
    
    def get_session(self) -> Session:
        """Sync session al"""
        return self.SessionLocal()
    
    def get_async_session(self) -> AsyncSession:
        """Async session al"""
        return self.AsyncSessionLocal()
    
    async def close(self):
        """Bağlantıları kapat"""
        if self.async_engine:
            await self.async_engine.dispose()
        if self.engine:
            self.engine.dispose()
        logger.info("Database connections closed")

# Global database manager
db_manager = DatabaseManager()

# Dependency for FastAPI
def get_db():
    """FastAPI dependency for database session"""
    db = db_manager.get_session()
    try:
        yield db
    finally:
        db.close()

async def get_async_db():
    """FastAPI dependency for async database session"""
    async with db_manager.get_async_session() as session:
        yield session

# Database initialization
async def init_database():
    """Veritabanını başlat"""
    try:
        db_manager.create_engines()
        await db_manager.create_tables_async()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

# Migration utilities
class DatabaseMigration:
    """Veritabanı migration sınıfı"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    async def migrate_data(self):
        """Veri migration"""
        try:
            # Mock migration - gerçek implementasyonda veri transferi yapılacak
            logger.info("Starting data migration...")
            
            # Migration steps
            await self._migrate_patients()
            await self._migrate_reports()
            await self._migrate_suv_measurements()
            
            logger.info("Data migration completed successfully")
            
        except Exception as e:
            logger.error(f"Data migration failed: {e}")
            raise
    
    async def _migrate_patients(self):
        """Hasta verilerini migrate et"""
        logger.info("Migrating patient data...")
        # Mock implementation
        await asyncio.sleep(0.1)
    
    async def _migrate_reports(self):
        """Rapor verilerini migrate et"""
        logger.info("Migrating report data...")
        # Mock implementation
        await asyncio.sleep(0.1)
    
    async def _migrate_suv_measurements(self):
        """SUV ölçüm verilerini migrate et"""
        logger.info("Migrating SUV measurement data...")
        # Mock implementation
        await asyncio.sleep(0.1)
    
    async def backup_database(self, backup_path: str):
        """Veritabanı yedeği al"""
        try:
            logger.info(f"Creating database backup: {backup_path}")
            # Mock backup implementation
            await asyncio.sleep(0.1)
            logger.info("Database backup completed")
        except Exception as e:
            logger.error(f"Database backup failed: {e}")
            raise
    
    async def restore_database(self, backup_path: str):
        """Veritabanı yedeğini geri yükle"""
        try:
            logger.info(f"Restoring database from backup: {backup_path}")
            # Mock restore implementation
            await asyncio.sleep(0.1)
            logger.info("Database restore completed")
        except Exception as e:
            logger.error(f"Database restore failed: {e}")
            raise

# Global migration instance
migration = DatabaseMigration(db_manager)
