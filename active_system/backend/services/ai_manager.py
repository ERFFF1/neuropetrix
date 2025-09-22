"""
AI Manager - Tüm AI modüllerini yöneten merkezi servis
"""
import logging
from typing import Dict, List, Any, Optional, Union
from enum import Enum
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)

class AIModuleType(str, Enum):
    GEMINI = "gemini"
    WHISPER = "whisper"
    MONAI = "monai"
    RADIOMICS = "radiomics"
    CLINICAL_AI = "clinical_ai"

class AIStatus(str, Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    LOADING = "loading"
    ERROR = "error"

class AIManager:
    """Tüm AI modüllerini yöneten merkezi sınıf"""
    
    def __init__(self):
        self.modules: Dict[AIModuleType, Dict[str, Any]] = {}
        self.initialized = False
        self._initialize_modules()
    
    def _initialize_modules(self):
        """AI modüllerini başlat"""
        logger.info("🤖 AI Manager başlatılıyor...")
        
        # Gemini modülü
        self.modules[AIModuleType.GEMINI] = {
            "status": AIStatus.AVAILABLE,
            "service": None,
            "capabilities": ["text_generation", "clinical_analysis", "evidence_search"],
            "last_used": None
        }
        
        # Whisper modülü
        self.modules[AIModuleType.WHISPER] = {
            "status": AIStatus.AVAILABLE,
            "service": None,
            "capabilities": ["speech_to_text", "transcription"],
            "last_used": None
        }
        
        # MONAI modülü
        self.modules[AIModuleType.MONAI] = {
            "status": AIStatus.AVAILABLE,
            "service": None,
            "capabilities": ["image_segmentation", "medical_imaging", "deep_learning"],
            "last_used": None
        }
        
        # PyRadiomics modülü
        self.modules[AIModuleType.RADIOMICS] = {
            "status": AIStatus.AVAILABLE,
            "service": None,
            "capabilities": ["feature_extraction", "radiomics_analysis"],
            "last_used": None
        }
        
        # Clinical AI modülü
        self.modules[AIModuleType.CLINICAL_AI] = {
            "status": AIStatus.AVAILABLE,
            "service": None,
            "capabilities": ["clinical_decision_support", "icd_analysis", "workflow_automation"],
            "last_used": None
        }
        
        self.initialized = True
        logger.info("✅ AI Manager başlatıldı - 5 modül yüklendi")
    
    async def get_module_status(self, module_type: AIModuleType) -> Dict[str, Any]:
        """Modül durumunu getir"""
        if module_type not in self.modules:
            return {"status": AIStatus.ERROR, "error": "Module not found"}
        
        module = self.modules[module_type]
        return {
            "status": module["status"],
            "capabilities": module["capabilities"],
            "last_used": module["last_used"],
            "available": module["status"] == AIStatus.AVAILABLE
        }
    
    async def get_all_modules_status(self) -> Dict[str, Any]:
        """Tüm modüllerin durumunu getir"""
        status = {}
        for module_type, module_data in self.modules.items():
            status[module_type.value] = await self.get_module_status(module_type)
        
        return {
            "total_modules": len(self.modules),
            "available_modules": sum(1 for m in self.modules.values() if m["status"] == AIStatus.AVAILABLE),
            "modules": status,
            "initialized": self.initialized
        }
    
    async def execute_ai_task(self, module_type: AIModuleType, task: str, **kwargs) -> Dict[str, Any]:
        """AI görevini çalıştır"""
        if module_type not in self.modules:
            return {"error": "Module not found", "success": False}
        
        module = self.modules[module_type]
        if module["status"] != AIStatus.AVAILABLE:
            return {"error": f"Module {module_type.value} not available", "success": False}
        
        try:
            # Modül kullanım zamanını güncelle
            module["last_used"] = datetime.now().isoformat()
            
            # Görev tipine göre yönlendir
            if module_type == AIModuleType.GEMINI:
                return await self._execute_gemini_task(task, **kwargs)
            elif module_type == AIModuleType.WHISPER:
                return await self._execute_whisper_task(task, **kwargs)
            elif module_type == AIModuleType.MONAI:
                return await self._execute_monai_task(task, **kwargs)
            elif module_type == AIModuleType.RADIOMICS:
                return await self._execute_radiomics_task(task, **kwargs)
            elif module_type == AIModuleType.CLINICAL_AI:
                return await self._execute_clinical_ai_task(task, **kwargs)
            else:
                return {"error": "Unknown task type", "success": False}
                
        except Exception as e:
            logger.error(f"AI task execution error: {str(e)}")
            return {"error": str(e), "success": False}
    
    async def _execute_gemini_task(self, task: str, **kwargs) -> Dict[str, Any]:
        """Gemini görevini çalıştır"""
        if task == "clinical_analysis":
            return {
                "success": True,
                "result": "Mock clinical analysis completed",
                "module": "gemini",
                "task": task
            }
        elif task == "evidence_search":
            return {
                "success": True,
                "result": "Mock evidence search completed",
                "module": "gemini",
                "task": task
            }
        else:
            return {"error": "Unknown Gemini task", "success": False}
    
    async def _execute_whisper_task(self, task: str, **kwargs) -> Dict[str, Any]:
        """Whisper görevini çalıştır"""
        if task == "transcribe":
            return {
                "success": True,
                "result": "Mock transcription completed",
                "module": "whisper",
                "task": task
            }
        else:
            return {"error": "Unknown Whisper task", "success": False}
    
    async def _execute_monai_task(self, task: str, **kwargs) -> Dict[str, Any]:
        """MONAI görevini çalıştır"""
        if task == "segment":
            return {
                "success": True,
                "result": "Mock segmentation completed",
                "module": "monai",
                "task": task
            }
        else:
            return {"error": "Unknown MONAI task", "success": False}
    
    async def _execute_radiomics_task(self, task: str, **kwargs) -> Dict[str, Any]:
        """PyRadiomics görevini çalıştır"""
        if task == "extract_features":
            return {
                "success": True,
                "result": "Mock feature extraction completed",
                "module": "radiomics",
                "task": task
            }
        else:
            return {"error": "Unknown PyRadiomics task", "success": False}
    
    async def _execute_clinical_ai_task(self, task: str, **kwargs) -> Dict[str, Any]:
        """Clinical AI görevini çalıştır"""
        if task == "icd_analysis":
            return {
                "success": True,
                "result": "Mock ICD analysis completed",
                "module": "clinical_ai",
                "task": task
            }
        elif task == "workflow_automation":
            return {
                "success": True,
                "result": "Mock workflow automation completed",
                "module": "clinical_ai",
                "task": task
            }
        else:
            return {"error": "Unknown Clinical AI task", "success": False}
    
    async def get_ai_insights(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """AI modüllerinden genel içgörüler al"""
        insights = {
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "recommendations": [],
            "confidence": 0.0
        }
        
        # Tüm modüllerden içgörü topla
        for module_type in self.modules:
            if self.modules[module_type]["status"] == AIStatus.AVAILABLE:
                try:
                    result = await self.execute_ai_task(module_type, "insight", context=context)
                    if result.get("success"):
                        insights["recommendations"].append({
                            "module": module_type.value,
                            "insight": result.get("result", "")
                        })
                except Exception as e:
                    logger.warning(f"Failed to get insight from {module_type.value}: {str(e)}")
        
        # Güven skorunu hesapla
        insights["confidence"] = len(insights["recommendations"]) / len(self.modules) * 100
        
        return insights

# Global AI Manager instance
ai_manager = AIManager()
