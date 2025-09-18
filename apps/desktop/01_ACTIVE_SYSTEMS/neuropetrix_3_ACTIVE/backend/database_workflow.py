"""
NeuroPETRIX Workflow Database
SQLite database for workflow state persistence
"""

import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)

class WorkflowDatabase:
    def __init__(self, db_path: str = "neuropetrix_workflow.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Workflow cases table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflow_cases (
                    case_id TEXT PRIMARY KEY,
                    patient_id TEXT,
                    purpose TEXT,
                    icd_code TEXT,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            
            # Workflow steps table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflow_steps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    case_id TEXT,
                    step_name TEXT,
                    status TEXT,
                    input_data TEXT,
                    output_data TEXT,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    error_message TEXT,
                    FOREIGN KEY (case_id) REFERENCES workflow_cases (case_id)
                )
            """)
            
            # Job queue table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS job_queue (
                    job_id TEXT PRIMARY KEY,
                    case_id TEXT,
                    function_name TEXT,
                    status TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP,
                    result_data TEXT,
                    error_message TEXT,
                    FOREIGN KEY (case_id) REFERENCES workflow_cases (case_id)
                )
            """)
            
            conn.commit()
            logger.info("Workflow database initialized")
    
    def create_case(self, case_id: str, patient_id: Optional[str], purpose: str, 
                   icd_code: Optional[str], metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Create a new workflow case"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO workflow_cases (case_id, patient_id, purpose, icd_code, status, metadata)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (case_id, patient_id, purpose, icd_code, "created", 
                      json.dumps(metadata) if metadata else None))
                conn.commit()
                logger.info(f"Case created: {case_id}")
                return True
        except Exception as e:
            logger.error(f"Error creating case {case_id}: {e}")
            return False
    
    def update_case_status(self, case_id: str, status: str) -> bool:
        """Update case status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE workflow_cases 
                    SET status = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE case_id = ?
                """, (status, case_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating case status {case_id}: {e}")
            return False
    
    def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        """Get case information"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT case_id, patient_id, purpose, icd_code, status, 
                           created_at, updated_at, metadata
                    FROM workflow_cases WHERE case_id = ?
                """, (case_id,))
                row = cursor.fetchone()
                if row:
                    return {
                        "case_id": row[0],
                        "patient_id": row[1],
                        "purpose": row[2],
                        "icd_code": row[3],
                        "status": row[4],
                        "created_at": row[5],
                        "updated_at": row[6],
                        "metadata": json.loads(row[7]) if row[7] else None
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting case {case_id}: {e}")
            return None
    
    def add_workflow_step(self, case_id: str, step_name: str, status: str,
                         input_data: Optional[Dict[str, Any]] = None,
                         output_data: Optional[Dict[str, Any]] = None,
                         error_message: Optional[str] = None) -> bool:
        """Add a workflow step"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO workflow_steps 
                    (case_id, step_name, status, input_data, output_data, started_at, error_message)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
                """, (case_id, step_name, status,
                      json.dumps(input_data) if input_data else None,
                      json.dumps(output_data) if output_data else None,
                      error_message))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding workflow step {case_id}/{step_name}: {e}")
            return False
    
    def update_workflow_step(self, case_id: str, step_name: str, status: str,
                            output_data: Optional[Dict[str, Any]] = None,
                            error_message: Optional[str] = None) -> bool:
        """Update workflow step"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE workflow_steps 
                    SET status = ?, output_data = ?, completed_at = CURRENT_TIMESTAMP, error_message = ?
                    WHERE case_id = ? AND step_name = ? AND status = 'running'
                """, (status, json.dumps(output_data) if output_data else None, error_message, case_id, step_name))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating workflow step {case_id}/{step_name}: {e}")
            return False
    
    def get_workflow_steps(self, case_id: str) -> List[Dict[str, Any]]:
        """Get all workflow steps for a case"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT step_name, status, input_data, output_data, 
                           started_at, completed_at, error_message
                    FROM workflow_steps WHERE case_id = ? ORDER BY started_at
                """, (case_id,))
                rows = cursor.fetchall()
                return [{
                    "step_name": row[0],
                    "status": row[1],
                    "input_data": json.loads(row[2]) if row[2] else None,
                    "output_data": json.loads(row[3]) if row[3] else None,
                    "started_at": row[4],
                    "completed_at": row[5],
                    "error_message": row[6]
                } for row in rows]
        except Exception as e:
            logger.error(f"Error getting workflow steps {case_id}: {e}")
            return []
    
    def add_job(self, job_id: str, case_id: str, function_name: str, status: str = "queued") -> bool:
        """Add a job to the queue"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO job_queue (job_id, case_id, function_name, status)
                    VALUES (?, ?, ?, ?)
                """, (job_id, case_id, function_name, status))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding job {job_id}: {e}")
            return False
    
    def update_job_status(self, job_id: str, status: str, result_data: Optional[Dict[str, Any]] = None,
                         error_message: Optional[str] = None) -> bool:
        """Update job status"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                if status == "running":
                    cursor.execute("""
                        UPDATE job_queue 
                        SET status = ?, started_at = CURRENT_TIMESTAMP
                        WHERE job_id = ?
                    """, (status, job_id))
                elif status in ["done", "failed"]:
                    cursor.execute("""
                        UPDATE job_queue 
                        SET status = ?, completed_at = CURRENT_TIMESTAMP, 
                            result_data = ?, error_message = ?
                        WHERE job_id = ?
                    """, (status, json.dumps(result_data) if result_data else None, error_message, job_id))
                else:
                    cursor.execute("""
                        UPDATE job_queue SET status = ? WHERE job_id = ?
                    """, (status, job_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating job status {job_id}: {e}")
            return False
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job information"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT job_id, case_id, function_name, status, created_at, 
                           started_at, completed_at, result_data, error_message
                    FROM job_queue WHERE job_id = ?
                """, (job_id,))
                row = cursor.fetchone()
                if row:
                    return {
                        "job_id": row[0],
                        "case_id": row[1],
                        "function_name": row[2],
                        "status": row[3],
                        "created_at": row[4],
                        "started_at": row[5],
                        "completed_at": row[6],
                        "result_data": json.loads(row[7]) if row[7] else None,
                        "error_message": row[8]
                    }
                return None
        except Exception as e:
            logger.error(f"Error getting job {job_id}: {e}")
            return None
    
    def get_all_cases(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get all cases"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT case_id, patient_id, purpose, icd_code, status, 
                           created_at, updated_at, metadata
                    FROM workflow_cases ORDER BY created_at DESC LIMIT ?
                """, (limit,))
                rows = cursor.fetchall()
                return [{
                    "case_id": row[0],
                    "patient_id": row[1],
                    "purpose": row[2],
                    "icd_code": row[3],
                    "status": row[4],
                    "created_at": row[5],
                    "updated_at": row[6],
                    "metadata": json.loads(row[7]) if row[7] else None
                } for row in rows]
        except Exception as e:
            logger.error(f"Error getting all cases: {e}")
            return []

# Global database instance
workflow_db = WorkflowDatabase()

