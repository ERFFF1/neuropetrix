import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

class GeminiService:
    """Gemini AI Studio entegrasyonu için servis"""
    
    def __init__(self, config_path: str = None):
        self.config_path = Path(config_path) if config_path else Path(__file__).parent.parent / "gemini_build"
        self.system_prompt = self._load_system_prompt()
        self.tools_config = self._load_tools_config()
        self.output_schema = self._load_output_schema()
        
    def _load_system_prompt(self) -> str:
        """System prompt dosyasını yükle"""
        try:
            prompt_file = self.config_path / "SystemPrompt.txt"
            if prompt_file.exists():
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    return f.read()
            else:
                logger.warning("SystemPrompt.txt bulunamadı")
                return "NeuroPETRIX v2.0 AI Assistant"
        except Exception as e:
            logger.error(f"System prompt yüklenemedi: {e}")
            return "NeuroPETRIX v2.0 AI Assistant"
    
    def _load_tools_config(self) -> Dict:
        """Tools.json dosyasını yükle"""
        try:
            tools_file = self.config_path / "Tools.json"
            if tools_file.exists():
                with open(tools_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning("Tools.json bulunamadı")
                return {"tools": []}
        except Exception as e:
            logger.error(f"Tools config yüklenemedi: {e}")
            return {"tools": []}
    
    def _load_output_schema(self) -> Dict:
        """OutputSchema.json dosyasını yükle"""
        try:
            schema_file = self.config_path / "OutputSchema.json"
            if schema_file.exists():
                with open(schema_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                logger.warning("OutputSchema.json bulunamadı")
                return {"output_schema": {}}
        except Exception as e:
            logger.error(f"Output schema yüklenemedi: {e}")
            return {"output_schema": {}}
    
    def generate_ai_conclusion(self, 
                              clinical_goal: str,
                              imaging_available: bool,
                              imaging_metrics: Optional[Dict] = None,
                              qc_flags: Optional[List[str]] = None,
                              evidence_summary: Optional[str] = None) -> Dict:
        """AI sonucu üret"""
        try:
            # Kural tabanlı AI sonucu üretimi
            ai_conclusion = self._generate_conclusion_key(clinical_goal, imaging_available, imaging_metrics)
            rationale_keys = self._generate_rationale_keys(clinical_goal, imaging_available, imaging_metrics, qc_flags)
            
            # Optional alanları doldur
            optional_data = self._generate_optional_data(clinical_goal, imaging_metrics, qc_flags, evidence_summary)
            
            result = {
                "ai_conclusion": ai_conclusion,
                "rationale_keys": rationale_keys,
                "optional": optional_data,
                "created_at": datetime.now().isoformat(),
                "model_version": "gemini-1.0.0"
            }
            
            # Validation
            if self._validate_output(result):
                logger.info(f"AI conclusion generated: {ai_conclusion}")
                return result
            else:
                logger.error("AI conclusion validation failed")
                return self._generate_fallback_conclusion(clinical_goal)
                
        except Exception as e:
            logger.error(f"AI conclusion generation failed: {e}")
            return self._generate_fallback_conclusion(clinical_goal)
    
    def _generate_conclusion_key(self, clinical_goal: str, imaging_available: bool, imaging_metrics: Optional[Dict]) -> str:
        """Conclusion key üret"""
        if clinical_goal == "staging":
            return "staging.no_imaging" if not imaging_available else "staging.with_imaging"
        
        elif clinical_goal == "response":
            if not imaging_available:
                return "response.no_imaging"
            else:
                percist = imaging_metrics.get("percist") if imaging_metrics else None
                if percist:
                    return f"response.percist_{percist}"
                else:
                    return "response.no_imaging"
        
        elif clinical_goal == "lymphoma_followup":
            if not imaging_available:
                return "lymphoma_followup.no_imaging"
            else:
                deauville = imaging_metrics.get("deauville") if imaging_metrics else None
                if deauville:
                    if deauville <= 3:
                        return "lymphoma_followup.deauville_1_3"
                    else:
                        return "lymphoma_followup.deauville_4_5"
                else:
                    return "lymphoma_followup.no_imaging"
        
        return "staging.no_imaging"  # fallback
    
    def _generate_rationale_keys(self, clinical_goal: str, imaging_available: bool, 
                                imaging_metrics: Optional[Dict], qc_flags: Optional[List[str]]) -> List[str]:
        """Rationale keys üret"""
        keys = []
        
        if imaging_available:
            keys.append("dicom_available")
            if imaging_metrics:
                if "suvmax" in imaging_metrics:
                    keys.append("suv_analysis")
                if "percist" in imaging_metrics:
                    keys.append("percist_criteria")
                if "deauville" in imaging_metrics:
                    keys.append("deauville_scoring")
        else:
            keys.append("no_dicom")
            keys.append("clinical_assessment")
        
        if qc_flags:
            keys.append("qc_warnings")
        
        keys.append(f"{clinical_goal}_evaluation")
        
        return keys
    
    def _generate_optional_data(self, clinical_goal: str, imaging_metrics: Optional[Dict], 
                               qc_flags: Optional[List[str]], evidence_summary: Optional[str]) -> Dict:
        """Optional data üret"""
        optional = {
            "percist": None,
            "deauville": None,
            "qc_flags": qc_flags or [],
            "grade_summary": None,
            "refs": []
        }
        
        # PERCIST (sadece response için)
        if clinical_goal == "response" and imaging_metrics:
            optional["percist"] = imaging_metrics.get("percist")
        
        # Deauville (sadece lymphoma_followup için)
        if clinical_goal == "lymphoma_followup" and imaging_metrics:
            optional["deauville"] = imaging_metrics.get("deauville")
        
        # GRADE summary
        if evidence_summary:
            if "GRADE A" in evidence_summary:
                optional["grade_summary"] = "GRADE A"
            elif "GRADE B" in evidence_summary:
                optional["grade_summary"] = "GRADE B"
            elif "GRADE C" in evidence_summary:
                optional["grade_summary"] = "GRADE C"
            elif "GRADE D" in evidence_summary:
                optional["grade_summary"] = "GRADE D"
        
        # References
        if clinical_goal == "response":
            optional["refs"] = ["PERCIST_v1.0", "Response_guidelines"]
        elif clinical_goal == "lymphoma_followup":
            optional["refs"] = ["Deauville_criteria", "Lymphoma_guidelines"]
        else:
            optional["refs"] = ["Staging_guidelines"]
        
        return optional
    
    def _validate_output(self, output: Dict) -> bool:
        """Output validation"""
        try:
            schema = self.output_schema.get("output_schema", {})
            required = schema.get("required", [])
            
            # Required fields check
            for field in required:
                if field not in output:
                    logger.error(f"Required field missing: {field}")
                    return False
            
            # Clinical goal validation
            ai_conclusion = output.get("ai_conclusion", "")
            clinical_goal = ai_conclusion.split(".")[0] if "." in ai_conclusion else ""
            
            if clinical_goal == "staging":
                if output.get("optional", {}).get("percist") is not None:
                    logger.error("Staging: PERCIST must be null")
                    return False
                if output.get("optional", {}).get("deauville") is not None:
                    logger.error("Staging: Deauville must be null")
                    return False
            
            elif clinical_goal == "response":
                if output.get("optional", {}).get("percist") is None:
                    logger.error("Response: PERCIST must be calculated")
                    return False
                if output.get("optional", {}).get("deauville") is not None:
                    logger.error("Response: Deauville must be null")
                    return False
            
            elif clinical_goal == "lymphoma_followup":
                if output.get("optional", {}).get("deauville") is None:
                    logger.error("Lymphoma: Deauville must be calculated")
                    return False
                if output.get("optional", {}).get("percist") is not None:
                    logger.error("Lymphoma: PERCIST must be null")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False
    
    def _generate_fallback_conclusion(self, clinical_goal: str) -> Dict:
        """Fallback conclusion üret"""
        return {
            "ai_conclusion": f"{clinical_goal}.no_imaging",
            "rationale_keys": ["fallback", "error_recovery"],
            "optional": {
                "percist": None,
                "deauville": None,
                "qc_flags": ["⚠️ AI conclusion generation failed"],
                "grade_summary": None,
                "refs": []
            },
            "created_at": datetime.now().isoformat(),
            "model_version": "gemini-fallback-1.0.0"
        }
    
    def get_system_info(self) -> Dict:
        """Sistem bilgilerini getir"""
        return {
            "service": "Gemini AI Studio",
            "version": "1.0.0",
            "system_prompt_loaded": bool(self.system_prompt),
            "tools_loaded": len(self.tools_config.get("tools", [])),
            "schema_loaded": bool(self.output_schema),
            "config_path": str(self.config_path)
        }

# Global Gemini service instance
gemini_service = GeminiService()


