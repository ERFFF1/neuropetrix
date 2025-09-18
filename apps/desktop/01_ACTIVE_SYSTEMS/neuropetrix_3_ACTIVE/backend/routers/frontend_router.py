from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from fastapi.responses import FileResponse
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import sqlite3
import json
import logging
from datetime import datetime
import os
import uuid

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Frontend API"])

# Pydantic Models
class CaseCreateRequest(BaseModel):
    patient_id: str
    purpose: str
    icd_code: str
    case_meta: Dict[str, Any]

class CaseUpdateRequest(BaseModel):
    systemStatus: Optional[str] = None
    clinicalStatus: Optional[str] = None
    analysis: Optional[Dict[str, Any]] = None
    chatHistory: Optional[List[Dict[str, Any]]] = None
    error: Optional[str] = None
    assignedTo: Optional[str] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None

class ChatMessageRequest(BaseModel):
    message: str
    role: str = "user"

class SearchParams(BaseModel):
    query: Optional[str] = None
    status: Optional[List[str]] = None
    priority: Optional[List[str]] = None
    assignedTo: Optional[str] = None
    dateRange: Optional[Dict[str, str]] = None
    tags: Optional[List[str]] = None
    sortBy: Optional[str] = "createdAt"
    sortOrder: Optional[str] = "desc"
    page: Optional[int] = 1
    limit: Optional[int] = 50

@router.get("/cases")
async def get_cases(params: SearchParams = Depends()):
    """Get cases with filtering and pagination"""
    try:
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        
        # Build query
        query = "SELECT * FROM cases WHERE 1=1"
        query_params = []
        
        if params.query:
            query += " AND (patient_id LIKE ? OR purpose LIKE ?)"
            query_params.extend([f"%{params.query}%", f"%{params.query}%"])
        
        if params.status:
            placeholders = ",".join(["?" for _ in params.status])
            query += f" AND status IN ({placeholders})"
            query_params.extend(params.status)
        
        if params.priority:
            placeholders = ",".join(["?" for _ in params.priority])
            query += f" AND priority IN ({placeholders})"
            query_params.extend(params.priority)
        
        # Add sorting
        query += f" ORDER BY {params.sortBy} {params.sortOrder.upper()}"
        
        # Add pagination
        offset = (params.page - 1) * params.limit
        query += f" LIMIT {params.limit} OFFSET {offset}"
        
        cursor.execute(query, query_params)
        rows = cursor.fetchone()
        
        # Get total count
        count_query = "SELECT COUNT(*) FROM cases WHERE 1=1"
        count_params = []
        
        if params.query:
            count_query += " AND (patient_id LIKE ? OR purpose LIKE ?)"
            count_params.extend([f"%{params.query}%", f"%{params.query}%"])
        
        if params.status:
            placeholders = ",".join(["?" for _ in params.status])
            count_query += f" AND status IN ({placeholders})"
            count_params.extend(params.status)
        
        cursor.execute(count_query, count_params)
        total = cursor.fetchone()[0]
        
        conn.close()
        
        # Convert to frontend format
        cases = []
        if rows:
            cases.append({
                "id": rows[0],
                "createdAt": rows[1],
                "updatedAt": rows[2],
                "patientData": json.loads(rows[3]) if rows[3] else {},
                "analysis": json.loads(rows[4]) if rows[4] else None,
                "chatHistory": json.loads(rows[5]) if rows[5] else [],
                "systemStatus": rows[6] or "draft",
                "clinicalStatus": rows[7] or "new",
                "error": rows[8],
                "assignedTo": rows[9],
                "priority": rows[10] or "normal",
                "tags": json.loads(rows[11]) if rows[11] else []
            })
        
        return {
            "cases": cases,
            "total": total,
            "page": params.page,
            "limit": params.limit
        }
        
    except Exception as e:
        logger.error(f"Get cases error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Get cases error: {str(e)}")

@router.get("/cases/{case_id}")
async def get_case(case_id: str):
    """Get specific case by ID"""
    try:
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Case not found")
        
        return {
            "id": row[0],
            "createdAt": row[1],
            "updatedAt": row[2],
            "patientData": json.loads(row[3]) if row[3] else {},
            "analysis": json.loads(row[4]) if row[4] else None,
            "chatHistory": json.loads(row[5]) if row[5] else [],
            "systemStatus": row[6] or "draft",
            "clinicalStatus": row[7] or "new",
            "error": row[8],
            "assignedTo": row[9],
            "priority": row[10] or "normal",
            "tags": json.loads(row[11]) if row[11] else []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get case error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Get case error: {str(e)}")

@router.post("/cases")
async def create_case(request: CaseCreateRequest):
    """Create new case"""
    try:
        case_id = f"CASE-{uuid.uuid4().hex[:8].upper()}"
        now = datetime.now().isoformat()
        
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        
        # Create cases table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS cases (
                case_id TEXT PRIMARY KEY,
                created_at TEXT,
                updated_at TEXT,
                patient_data TEXT,
                analysis TEXT,
                chat_history TEXT,
                system_status TEXT,
                clinical_status TEXT,
                error TEXT,
                assigned_to TEXT,
                priority TEXT,
                tags TEXT
            )
        """)
        
        cursor.execute("""
            INSERT INTO cases 
            (case_id, created_at, updated_at, patient_data, system_status, clinical_status, priority)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            case_id,
            now,
            now,
            json.dumps(request.case_meta),
            "draft",
            "new",
            "normal"
        ))
        
        conn.commit()
        conn.close()
        
        return {
            "id": case_id,
            "createdAt": now,
            "updatedAt": now,
            "patientData": request.case_meta,
            "analysis": None,
            "chatHistory": [],
            "systemStatus": "draft",
            "clinicalStatus": "new",
            "error": None,
            "assignedTo": None,
            "priority": "normal",
            "tags": []
        }
        
    except Exception as e:
        logger.error(f"Create case error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Create case error: {str(e)}")

@router.patch("/cases/{case_id}")
async def update_case(case_id: str, request: CaseUpdateRequest):
    """Update case"""
    try:
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        
        # Get current case
        cursor.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Build update query
        update_fields = []
        update_values = []
        
        if request.systemStatus is not None:
            update_fields.append("system_status = ?")
            update_values.append(request.systemStatus)
        
        if request.clinicalStatus is not None:
            update_fields.append("clinical_status = ?")
            update_values.append(request.clinicalStatus)
        
        if request.analysis is not None:
            update_fields.append("analysis = ?")
            update_values.append(json.dumps(request.analysis))
        
        if request.chatHistory is not None:
            update_fields.append("chat_history = ?")
            update_values.append(json.dumps(request.chatHistory))
        
        if request.error is not None:
            update_fields.append("error = ?")
            update_values.append(request.error)
        
        if request.assignedTo is not None:
            update_fields.append("assigned_to = ?")
            update_values.append(request.assignedTo)
        
        if request.priority is not None:
            update_fields.append("priority = ?")
            update_values.append(request.priority)
        
        if request.tags is not None:
            update_fields.append("tags = ?")
            update_values.append(json.dumps(request.tags))
        
        if update_fields:
            update_fields.append("updated_at = ?")
            update_values.append(datetime.now().isoformat())
            update_values.append(case_id)
            
            query = f"UPDATE cases SET {', '.join(update_fields)} WHERE case_id = ?"
            cursor.execute(query, update_values)
            conn.commit()
        
        # Get updated case
        cursor.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
        row = cursor.fetchone()
        conn.close()
        
        return {
            "id": row[0],
            "createdAt": row[1],
            "updatedAt": row[2],
            "patientData": json.loads(row[3]) if row[3] else {},
            "analysis": json.loads(row[4]) if row[4] else None,
            "chatHistory": json.loads(row[5]) if row[5] else [],
            "systemStatus": row[6] or "draft",
            "clinicalStatus": row[7] or "new",
            "error": row[8],
            "assignedTo": row[9],
            "priority": row[10] or "normal",
            "tags": json.loads(row[11]) if row[11] else []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update case error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Update case error: {str(e)}")

@router.delete("/cases/{case_id}")
async def delete_case(case_id: str):
    """Delete case"""
    try:
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM cases WHERE case_id = ?", (case_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            raise HTTPException(status_code=404, detail="Case not found")
        
        conn.commit()
        conn.close()
        
        return {"message": "Case deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete case error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Delete case error: {str(e)}")

@router.post("/cases/{case_id}/chat")
async def send_chat_message(case_id: str, request: ChatMessageRequest):
    """Send chat message"""
    try:
        # Get current case
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM cases WHERE case_id = ?", (case_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Case not found")
        
        # Add message to chat history
        chat_history = json.loads(row[5]) if row[5] else []
        
        new_message = {
            "id": str(uuid.uuid4()),
            "role": request.role,
            "content": request.message,
            "timestamp": datetime.now().isoformat()
        }
        
        chat_history.append(new_message)
        
        # Update case
        cursor.execute("""
            UPDATE cases 
            SET chat_history = ?, updated_at = ?
            WHERE case_id = ?
        """, (
            json.dumps(chat_history),
            datetime.now().isoformat(),
            case_id
        ))
        
        conn.commit()
        conn.close()
        
        return new_message
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Send chat message error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Send chat message error: {str(e)}")

@router.get("/cases/{case_id}/chat")
async def get_chat_history(case_id: str):
    """Get chat history for case"""
    try:
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT chat_history FROM cases WHERE case_id = ?", (case_id,))
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Case not found")
        
        return json.loads(row[0]) if row[0] else []
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get chat history error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Get chat history error: {str(e)}")

@router.post("/cases/{case_id}/dicom")
async def upload_dicom(case_id: str, file: UploadFile = File(...)):
    """Upload DICOM file"""
    try:
        # Create uploads directory
        upload_dir = "uploads/dicom"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = os.path.splitext(file.filename)[1] if file.filename else ".dcm"
        filename = f"{file_id}{file_extension}"
        file_path = os.path.join(upload_dir, filename)
        
        # Save file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        return {
            "fileId": file_id,
            "url": f"/uploads/dicom/{filename}",
            "filename": file.filename,
            "size": len(content)
        }
        
    except Exception as e:
        logger.error(f"Upload DICOM error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload DICOM error: {str(e)}")

@router.get("/dicom/metadata/{file_id}")
async def get_dicom_metadata(file_id: str):
    """Get DICOM metadata"""
    try:
        # Mock metadata for now
        return {
            "fileId": file_id,
            "patientName": "Mock Patient",
            "patientId": "P-001",
            "studyDate": "2025-09-05",
            "modality": "CT",
            "seriesDescription": "Chest CT",
            "imageCount": 100,
            "sliceThickness": 1.0,
            "pixelSpacing": [0.5, 0.5]
        }
        
    except Exception as e:
        logger.error(f"Get DICOM metadata error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Get DICOM metadata error: {str(e)}")

@router.post("/cases/{case_id}/report")
async def generate_report(case_id: str):
    """Generate report for case"""
    try:
        # Mock report generation
        report_id = str(uuid.uuid4())
        
        return {
            "reportId": report_id,
            "url": f"/reports/{report_id}/download"
        }
        
    except Exception as e:
        logger.error(f"Generate report error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Generate report error: {str(e)}")

@router.get("/reports/{report_id}/download")
async def download_report(report_id: str):
    """Download report"""
    try:
        # Mock report download
        return {"message": "Report download not implemented yet"}
        
    except Exception as e:
        logger.error(f"Download report error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Download report error: {str(e)}")

@router.get("/health")
async def frontend_health():
    """Frontend API health check"""
    return {
        "status": "healthy",
        "service": "frontend_api",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }
