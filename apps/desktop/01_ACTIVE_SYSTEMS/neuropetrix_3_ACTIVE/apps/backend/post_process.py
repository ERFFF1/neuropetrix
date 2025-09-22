from typing import Dict, Any, List
import json

def post_process_analysis_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Analiz sonucunu post-process et"""
    try:
        # Sonuçları işle ve formatla
        processed_result = {
            "success": True,
            "processed_at": "2024-01-15T10:30:00Z",
            "analysis": result,
            "summary": {
                "total_findings": len(result.get("findings", [])),
                "confidence_score": result.get("confidence", 0.0),
                "recommendations_count": len(result.get("recommendations", []))
            }
        }
        
        return processed_result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "processed_at": "2024-01-15T10:30:00Z"
        }

def format_clinical_recommendations(recommendations: List[str]) -> str:
    """Klinik önerileri formatla"""
    if not recommendations:
        return "Öneri bulunamadı."
    
    formatted = "## Klinik Öneriler\n\n"
    for i, rec in enumerate(recommendations, 1):
        formatted += f"{i}. {rec}\n"
    
    return formatted

def calculate_risk_score(factors: Dict[str, Any]) -> float:
    """Risk skoru hesapla"""
    try:
        # Basit risk hesaplama
        base_score = 0.5
        
        if factors.get("age", 0) > 65:
            base_score += 0.1
        
        if factors.get("smoking", False):
            base_score += 0.2
            
        if factors.get("family_history", False):
            base_score += 0.15
            
        return min(1.0, base_score)
        
    except Exception:
        return 0.5