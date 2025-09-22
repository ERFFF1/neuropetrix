import json
from typing import Dict, Any, List

def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> Dict[str, Any]:
    """JSON şemasını doğrula"""
    try:
        # Basit JSON şema doğrulama
        errors = []
        
        for field, field_schema in schema.items():
            if field_schema.get("required", False) and field not in data:
                errors.append(f"Required field '{field}' is missing")
            
            if field in data:
                field_type = field_schema.get("type")
                if field_type and not isinstance(data[field], field_type):
                    errors.append(f"Field '{field}' must be of type {field_type}")
        
        if errors:
            return {
                "valid": False,
                "errors": errors
            }
        
        return {
            "valid": True,
            "message": "JSON schema validation passed"
        }
        
    except Exception as e:
        return {
            "valid": False,
            "error": str(e)
        }

def validate_patient_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Hasta verilerini doğrula"""
    schema = {
        "name": {"type": str, "required": True},
        "age": {"type": int, "required": True},
        "gender": {"type": str, "required": True},
        "diagnosis": {"type": str, "required": False}
    }
    
    return validate_json_schema(data, schema)

def validate_imaging_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Görüntü verilerini doğrula"""
    schema = {
        "dicom_files": {"type": list, "required": True},
        "modality": {"type": str, "required": True},
        "acquisition_date": {"type": str, "required": False}
    }
    
    return validate_json_schema(data, schema)


