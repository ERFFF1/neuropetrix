from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File
from typing import Dict, List, Any, Optional
from pydantic import BaseModel
import json
import logging
import asyncio
from datetime import datetime
import sqlite3
import os
import tempfile
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/advanced-ai", tags=["Advanced AI Pipeline"])

class AIAnalysisRequest(BaseModel):
    case_id: str
    patient_id: str
    analysis_type: str  # "comprehensive", "segmentation", "radiomics", "prognosis"
    ai_model_config: Optional[Dict[str, Any]] = None
    priority: str = "normal"  # "low", "normal", "high", "urgent"

class AIAnalysisResult(BaseModel):
    case_id: str
    patient_id: str
    analysis_type: str
    status: str
    results: Optional[Dict[str, Any]] = None
    confidence_scores: Optional[Dict[str, float]] = None
    processing_time: Optional[float] = None
    model_versions: Optional[Dict[str, str]] = None
    error_message: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None

class ModelTrainingRequest(BaseModel):
    model_name: str
    training_data_path: str
    model_type: str  # "segmentation", "classification", "regression"
    hyperparameters: Optional[Dict[str, Any]] = None
    validation_split: float = 0.2

# Mock AI models and their capabilities
AI_MODELS = {
    "lung_segmentation": {
        "name": "Lung Lesion Segmentation v2.1",
        "type": "segmentation",
        "modality": "PET/CT",
        "accuracy": 0.94,
        "description": "Advanced lung lesion segmentation using 3D U-Net"
    },
    "lymph_node_detection": {
        "name": "Lymph Node Detection v1.8",
        "type": "detection",
        "modality": "PET/CT",
        "accuracy": 0.89,
        "description": "Automated lymph node detection and classification"
    },
    "prognosis_prediction": {
        "name": "Survival Prediction v3.0",
        "type": "regression",
        "modality": "Multi-modal",
        "accuracy": 0.82,
        "description": "Multi-modal survival prediction model"
    },
    "radiomics_classifier": {
        "name": "Radiomics Classifier v2.5",
        "type": "classification",
        "modality": "PET/CT",
        "accuracy": 0.91,
        "description": "Advanced radiomics feature classification"
    }
}

@router.get("/models")
async def get_available_models():
    """Get available AI models and their capabilities"""
    return {
        "status": "success",
        "models": AI_MODELS,
        "total_models": len(AI_MODELS),
        "timestamp": datetime.now().isoformat()
    }

@router.get("/models/{model_name}")
async def get_model_details(model_name: str):
    """Get detailed information about a specific model"""
    if model_name not in AI_MODELS:
        raise HTTPException(status_code=404, detail=f"Model {model_name} not found")
    
    model_info = AI_MODELS[model_name].copy()
    
    # Add additional model details
    model_info.update({
        "input_requirements": {
            "image_format": "NIfTI",
            "image_size": "512x512x64",
            "preprocessing": "Normalization, Resampling"
        },
        "output_format": {
            "segmentation": "NIfTI mask",
            "classification": "Probability scores",
            "regression": "Continuous values"
        },
        "performance_metrics": {
            "dice_score": 0.94,
            "sensitivity": 0.92,
            "specificity": 0.96,
            "auc": 0.95
        },
        "training_data": {
            "total_cases": 1250,
            "validation_cases": 250,
            "test_cases": 200
        }
    })
    
    return {
        "status": "success",
        "model": model_info,
        "timestamp": datetime.now().isoformat()
    }

@router.post("/analyze", response_model=AIAnalysisResult)
async def run_ai_analysis(background_tasks: BackgroundTasks, request: AIAnalysisRequest):
    """Run comprehensive AI analysis on a case"""
    try:
        # Create analysis record
        analysis_id = f"AI-{request.case_id}-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Store analysis request in database
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        
        # Create AI analyses table if not exists
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_analyses (
                id TEXT PRIMARY KEY,
                case_id TEXT,
                patient_id TEXT,
                analysis_type TEXT,
                status TEXT,
                model_config TEXT,
                priority TEXT,
                results TEXT,
                confidence_scores TEXT,
                processing_time REAL,
                model_versions TEXT,
                error_message TEXT,
                created_at TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        
        cursor.execute("""
            INSERT INTO ai_analyses 
            (id, case_id, patient_id, analysis_type, status, model_config, priority, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            analysis_id,
            request.case_id,
            request.patient_id,
            request.analysis_type,
            "queued",
            json.dumps(request.ai_model_config) if request.ai_model_config else None,
            request.priority,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        # Start background analysis
        background_tasks.add_task(
            run_comprehensive_analysis,
            analysis_id,
            request
        )
        
        return AIAnalysisResult(
            case_id=request.case_id,
            patient_id=request.patient_id,
            analysis_type=request.analysis_type,
            status="queued",
            created_at=datetime.now().isoformat()
        )
        
    except Exception as e:
        logger.error(f"AI analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"AI analysis error: {str(e)}")

@router.get("/analysis/{analysis_id}")
async def get_analysis_status(analysis_id: str):
    """Get AI analysis status and results"""
    try:
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM ai_analyses WHERE id = ?
        """, (analysis_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        return {
            "status": "success",
            "analysis": {
                "id": row[0],
                "case_id": row[1],
                "patient_id": row[2],
                "analysis_type": row[3],
                "status": row[4],
                "model_config": json.loads(row[5]) if row[5] else None,
                "priority": row[6],
                "results": json.loads(row[7]) if row[7] else None,
                "confidence_scores": json.loads(row[8]) if row[8] else None,
                "processing_time": row[9],
                "model_versions": json.loads(row[10]) if row[10] else None,
                "error_message": row[11],
                "created_at": row[12],
                "completed_at": row[13]
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Get analysis status error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Get analysis status error: {str(e)}")

@router.get("/analyses")
async def get_all_analyses(limit: int = 50, status: str = None):
    """Get all AI analyses with optional filtering"""
    try:
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        
        query = "SELECT * FROM ai_analyses"
        params = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        
        analyses = []
        for row in cursor.fetchall():
            analyses.append({
                "id": row[0],
                "case_id": row[1],
                "patient_id": row[2],
                "analysis_type": row[3],
                "status": row[4],
                "priority": row[6],
                "processing_time": row[9],
                "created_at": row[12],
                "completed_at": row[13]
            })
        
        conn.close()
        
        return {
            "status": "success",
            "analyses": analyses,
            "total": len(analyses),
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Get analyses error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Get analyses error: {str(e)}")

@router.post("/train")
async def train_model(background_tasks: BackgroundTasks, request: ModelTrainingRequest):
    """Start model training process"""
    try:
        training_id = f"TRAIN-{request.model_name}-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Store training request
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS model_training (
                id TEXT PRIMARY KEY,
                model_name TEXT,
                model_type TEXT,
                status TEXT,
                training_data_path TEXT,
                hyperparameters TEXT,
                validation_split REAL,
                created_at TIMESTAMP,
                completed_at TIMESTAMP,
                performance_metrics TEXT
            )
        """)
        
        cursor.execute("""
            INSERT INTO model_training 
            (id, model_name, model_type, status, training_data_path, hyperparameters, validation_split, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            training_id,
            request.model_name,
            request.model_type,
            "queued",
            request.training_data_path,
            json.dumps(request.hyperparameters) if request.hyperparameters else None,
            request.validation_split,
            datetime.now().isoformat()
        ))
        
        conn.commit()
        conn.close()
        
        # Start background training
        background_tasks.add_task(
            train_model_background,
            training_id,
            request
        )
        
        return {
            "status": "success",
            "training_id": training_id,
            "message": "Model training started",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Model training error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Model training error: {str(e)}")

@router.get("/training/{training_id}")
async def get_training_status(training_id: str):
    """Get model training status"""
    try:
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM model_training WHERE id = ?
        """, (training_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            raise HTTPException(status_code=404, detail="Training not found")
        
        return {
            "status": "success",
            "training": {
                "id": row[0],
                "model_name": row[1],
                "model_type": row[2],
                "status": row[3],
                "training_data_path": row[4],
                "hyperparameters": json.loads(row[5]) if row[5] else None,
                "validation_split": row[6],
                "created_at": row[7],
                "completed_at": row[8],
                "performance_metrics": json.loads(row[9]) if row[9] else None
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Get training status error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Get training status error: {str(e)}")

@router.get("/performance")
async def get_ai_performance_metrics():
    """Get overall AI system performance metrics"""
    try:
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        
        # Get analysis statistics
        cursor.execute("SELECT COUNT(*) FROM ai_analyses")
        total_analyses = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ai_analyses WHERE status = 'completed'")
        completed_analyses = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM ai_analyses WHERE status = 'failed'")
        failed_analyses = cursor.fetchone()[0]
        
        # Get average processing time
        cursor.execute("SELECT AVG(processing_time) FROM ai_analyses WHERE processing_time IS NOT NULL")
        avg_processing_time = cursor.fetchone()[0] or 0
        
        conn.close()
        
        # Calculate success rate
        success_rate = (completed_analyses / max(total_analyses, 1)) * 100
        
        return {
            "status": "success",
            "metrics": {
                "total_analyses": total_analyses,
                "completed_analyses": completed_analyses,
                "failed_analyses": failed_analyses,
                "success_rate": round(success_rate, 2),
                "average_processing_time": round(avg_processing_time, 2),
                "available_models": len(AI_MODELS),
                "system_uptime": "99.9%",  # Mock data
                "model_accuracy": {
                    "lung_segmentation": 0.94,
                    "lymph_node_detection": 0.89,
                    "prognosis_prediction": 0.82,
                    "radiomics_classifier": 0.91
                }
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Get performance metrics error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Get performance metrics error: {str(e)}")

async def run_comprehensive_analysis(analysis_id: str, request: AIAnalysisRequest):
    """Background task for running comprehensive AI analysis"""
    try:
        logger.info(f"Starting AI analysis {analysis_id}")
        
        # Update status to processing
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE ai_analyses SET status = 'processing' WHERE id = ?
        """, (analysis_id,))
        conn.commit()
        conn.close()
        
        # Simulate AI processing time based on analysis type
        processing_times = {
            "comprehensive": 120.0,
            "segmentation": 45.0,
            "radiomics": 30.0,
            "prognosis": 60.0
        }
        
        processing_time = processing_times.get(request.analysis_type, 60.0)
        await asyncio.sleep(2)  # Simulate processing
        
        # Generate mock results based on analysis type
        results = generate_mock_results(request.analysis_type)
        confidence_scores = generate_confidence_scores(request.analysis_type)
        model_versions = {
            "lung_segmentation": "v2.1",
            "lymph_node_detection": "v1.8",
            "prognosis_prediction": "v3.0",
            "radiomics_classifier": "v2.5"
        }
        
        # Update database with results
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE ai_analyses 
            SET status = 'completed', 
                results = ?, 
                confidence_scores = ?, 
                processing_time = ?, 
                model_versions = ?, 
                completed_at = ?
            WHERE id = ?
        """, (
            json.dumps(results),
            json.dumps(confidence_scores),
            processing_time,
            json.dumps(model_versions),
            datetime.now().isoformat(),
            analysis_id
        ))
        conn.commit()
        conn.close()
        
        logger.info(f"AI analysis {analysis_id} completed successfully")
        
    except Exception as e:
        logger.error(f"AI analysis {analysis_id} failed: {str(e)}")
        
        # Update database with error
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE ai_analyses 
            SET status = 'failed', 
                error_message = ?, 
                completed_at = ?
            WHERE id = ?
        """, (str(e), datetime.now().isoformat(), analysis_id))
        conn.commit()
        conn.close()

async def train_model_background(training_id: str, request: ModelTrainingRequest):
    """Background task for model training"""
    try:
        logger.info(f"Starting model training {training_id}")
        
        # Update status to training
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE model_training SET status = 'training' WHERE id = ?
        """, (training_id,))
        conn.commit()
        conn.close()
        
        # Simulate training time
        await asyncio.sleep(5)
        
        # Generate mock performance metrics
        performance_metrics = {
            "accuracy": 0.92,
            "precision": 0.89,
            "recall": 0.91,
            "f1_score": 0.90,
            "auc": 0.94,
            "training_loss": 0.15,
            "validation_loss": 0.18
        }
        
        # Update database with results
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE model_training 
            SET status = 'completed', 
                performance_metrics = ?, 
                completed_at = ?
            WHERE id = ?
        """, (
            json.dumps(performance_metrics),
            datetime.now().isoformat(),
            training_id
        ))
        conn.commit()
        conn.close()
        
        logger.info(f"Model training {training_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Model training {training_id} failed: {str(e)}")
        
        # Update database with error
        conn = sqlite3.connect('neuropetrix_workflow.db')
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE model_training 
            SET status = 'failed', 
                completed_at = ?
            WHERE id = ?
        """, (datetime.now().isoformat(), training_id))
        conn.commit()
        conn.close()

def generate_mock_results(analysis_type: str) -> Dict[str, Any]:
    """Generate mock analysis results"""
    import random
    
    if analysis_type == "comprehensive":
        return {
            "segmentation": {
                "lung_lesions": {
                    "count": random.randint(1, 5),
                    "total_volume": round(random.uniform(10.0, 100.0), 2),
                    "largest_lesion_volume": round(random.uniform(5.0, 50.0), 2)
                },
                "lymph_nodes": {
                    "count": random.randint(0, 3),
                    "suspicious_count": random.randint(0, 2)
                }
            },
            "radiomics": {
                "firstorder": {
                    "mean": round(random.uniform(2.0, 8.0), 3),
                    "std": round(random.uniform(0.5, 2.0), 3),
                    "skewness": round(random.uniform(-1.0, 1.0), 3)
                },
                "shape": {
                    "volume": round(random.uniform(10.0, 100.0), 2),
                    "sphericity": round(random.uniform(0.3, 0.9), 3)
                }
            },
            "prognosis": {
                "survival_probability_1yr": round(random.uniform(0.6, 0.95), 3),
                "survival_probability_2yr": round(random.uniform(0.4, 0.85), 3),
                "risk_score": round(random.uniform(0.2, 0.8), 3)
            }
        }
    elif analysis_type == "segmentation":
        return {
            "lung_lesions": {
                "count": random.randint(1, 5),
                "total_volume": round(random.uniform(10.0, 100.0), 2),
                "largest_lesion_volume": round(random.uniform(5.0, 50.0), 2)
            }
        }
    elif analysis_type == "radiomics":
        return {
            "firstorder": {
                "mean": round(random.uniform(2.0, 8.0), 3),
                "std": round(random.uniform(0.5, 2.0), 3),
                "skewness": round(random.uniform(-1.0, 1.0), 3)
            },
            "shape": {
                "volume": round(random.uniform(10.0, 100.0), 2),
                "sphericity": round(random.uniform(0.3, 0.9), 3)
            }
        }
    elif analysis_type == "prognosis":
        return {
            "survival_probability_1yr": round(random.uniform(0.6, 0.95), 3),
            "survival_probability_2yr": round(random.uniform(0.4, 0.85), 3),
            "risk_score": round(random.uniform(0.2, 0.8), 3)
        }
    
    return {}

def generate_confidence_scores(analysis_type: str) -> Dict[str, float]:
    """Generate mock confidence scores"""
    import random
    
    if analysis_type == "comprehensive":
        return {
            "segmentation": round(random.uniform(0.85, 0.95), 3),
            "radiomics": round(random.uniform(0.80, 0.90), 3),
            "prognosis": round(random.uniform(0.75, 0.85), 3)
        }
    elif analysis_type == "segmentation":
        return {"segmentation": round(random.uniform(0.85, 0.95), 3)}
    elif analysis_type == "radiomics":
        return {"radiomics": round(random.uniform(0.80, 0.90), 3)}
    elif analysis_type == "prognosis":
        return {"prognosis": round(random.uniform(0.75, 0.85), 3)}
    
    return {}

@router.get("/health")
async def advanced_ai_health():
    """Advanced AI service health check"""
    return {
        "status": "healthy",
        "service": "advanced_ai",
        "version": "1.0.0",
        "available_models": len(AI_MODELS),
        "timestamp": datetime.now().isoformat()
    }
