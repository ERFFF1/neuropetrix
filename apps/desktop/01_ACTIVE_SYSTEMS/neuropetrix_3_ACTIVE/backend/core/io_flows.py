"""
NeuroPETRIX IO Flows Definition
Girdi-Çıktı Akışları ve Sistem Yanıtları
"""

from typing import Dict, List, Any, Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class FlowType(str, Enum):
    CLINICAL_WORKFLOW = "clinical_workflow"
    IMAGE_ANALYSIS = "image_analysis"
    REPORT_GENERATION = "report_generation"
    AI_ANALYSIS = "ai_analysis"
    EVIDENCE_SEARCH = "evidence_search"
    PICO_AUTOMATION = "pico_automation"

class InputType(str, Enum):
    ICD_CODE = "icd_code"
    DICOM_IMAGE = "dicom_image"
    PATIENT_DATA = "patient_data"
    CLINICAL_QUERY = "clinical_query"
    VOICE_INPUT = "voice_input"
    TEXT_INPUT = "text_input"

class OutputType(str, Enum):
    CLINICAL_RECOMMENDATION = "clinical_recommendation"
    IMAGE_ANALYSIS_RESULT = "image_analysis_result"
    TSNM_REPORT = "tsnm_report"
    AI_INSIGHT = "ai_insight"
    EVIDENCE_SUMMARY = "evidence_summary"
    PICO_QUESTION = "pico_question"

class FlowStep(BaseModel):
    step_id: str
    step_name: str
    input_type: InputType
    output_type: OutputType
    processing_time: float
    success_rate: float
    dependencies: List[str] = []

class IOFlow(BaseModel):
    flow_id: str
    flow_name: str
    flow_type: FlowType
    description: str
    steps: List[FlowStep]
    total_processing_time: float
    success_rate: float
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]

# Tanımlı IO Akışları
DEFINED_FLOWS = {
    "clinical_workflow": IOFlow(
        flow_id="clinical_workflow_001",
        flow_name="ICD-10 Klinik Workflow",
        flow_type=FlowType.CLINICAL_WORKFLOW,
        description="ICD kodu ile başlayan klinik karar destek süreci",
        steps=[
            FlowStep(
                step_id="step_1",
                step_name="ICD Kod Analizi",
                input_type=InputType.ICD_CODE,
                output_type=OutputType.CLINICAL_RECOMMENDATION,
                processing_time=0.5,
                success_rate=0.95
            ),
            FlowStep(
                step_id="step_2",
                step_name="Klinik Hedef Belirleme",
                input_type=InputType.CLINICAL_QUERY,
                output_type=OutputType.CLINICAL_RECOMMENDATION,
                processing_time=0.3,
                success_rate=0.98,
                dependencies=["step_1"]
            ),
            FlowStep(
                step_id="step_3",
                step_name="Literatür Taraması",
                input_type=InputType.CLINICAL_QUERY,
                output_type=OutputType.EVIDENCE_SUMMARY,
                processing_time=2.0,
                success_rate=0.90,
                dependencies=["step_2"]
            ),
            FlowStep(
                step_id="step_4",
                step_name="SUV Analizi",
                input_type=InputType.DICOM_IMAGE,
                output_type=OutputType.IMAGE_ANALYSIS_RESULT,
                processing_time=3.0,
                success_rate=0.85,
                dependencies=["step_3"]
            ),
            FlowStep(
                step_id="step_5",
                step_name="Segmentasyon",
                input_type=InputType.DICOM_IMAGE,
                output_type=OutputType.IMAGE_ANALYSIS_RESULT,
                processing_time=5.0,
                success_rate=0.80,
                dependencies=["step_4"]
            ),
            FlowStep(
                step_id="step_6",
                step_name="Klinik Yorumlama",
                input_type=InputType.CLINICAL_QUERY,
                output_type=OutputType.CLINICAL_RECOMMENDATION,
                processing_time=1.0,
                success_rate=0.92,
                dependencies=["step_5"]
            ),
            FlowStep(
                step_id="step_7",
                step_name="Rapor Üretimi",
                input_type=InputType.CLINICAL_QUERY,
                output_type=OutputType.TSNM_REPORT,
                processing_time=1.5,
                success_rate=0.95,
                dependencies=["step_6"]
            ),
            FlowStep(
                step_id="step_8",
                step_name="Takip Planlaması",
                input_type=InputType.CLINICAL_QUERY,
                output_type=OutputType.CLINICAL_RECOMMENDATION,
                processing_time=0.5,
                success_rate=0.98,
                dependencies=["step_7"]
            )
        ],
        total_processing_time=14.3,
        success_rate=0.89,
        input_schema={
            "icd_code": {"type": "string", "required": True},
            "patient_data": {"type": "object", "required": True},
            "clinical_target": {"type": "string", "required": True}
        },
        output_schema={
            "workflow_id": {"type": "string"},
            "clinical_recommendation": {"type": "object"},
            "tsnm_report": {"type": "object"},
            "follow_up_plan": {"type": "object"}
        }
    ),
    
    "image_analysis": IOFlow(
        flow_id="image_analysis_001",
        flow_name="DICOM Görüntü Analizi",
        flow_type=FlowType.IMAGE_ANALYSIS,
        description="DICOM görüntülerinin AI destekli analizi",
        steps=[
            FlowStep(
                step_id="step_1",
                step_name="DICOM Yükleme",
                input_type=InputType.DICOM_IMAGE,
                output_type=OutputType.IMAGE_ANALYSIS_RESULT,
                processing_time=2.0,
                success_rate=0.95
            ),
            FlowStep(
                step_id="step_2",
                step_name="Preprocessing",
                input_type=InputType.DICOM_IMAGE,
                output_type=OutputType.IMAGE_ANALYSIS_RESULT,
                processing_time=3.0,
                success_rate=0.90,
                dependencies=["step_1"]
            ),
            FlowStep(
                step_id="step_3",
                step_name="MONAI Segmentasyon",
                input_type=InputType.DICOM_IMAGE,
                output_type=OutputType.IMAGE_ANALYSIS_RESULT,
                processing_time=8.0,
                success_rate=0.85,
                dependencies=["step_2"]
            ),
            FlowStep(
                step_id="step_4",
                step_name="PyRadiomics Analizi",
                input_type=InputType.DICOM_IMAGE,
                output_type=OutputType.IMAGE_ANALYSIS_RESULT,
                processing_time=5.0,
                success_rate=0.80,
                dependencies=["step_3"]
            ),
            FlowStep(
                step_id="step_5",
                step_name="AI Yorumlama",
                input_type=InputType.CLINICAL_QUERY,
                output_type=OutputType.AI_INSIGHT,
                processing_time=2.0,
                success_rate=0.88,
                dependencies=["step_4"]
            )
        ],
        total_processing_time=20.0,
        success_rate=0.84,
        input_schema={
            "dicom_files": {"type": "array", "required": True},
            "analysis_type": {"type": "string", "required": True}
        },
        output_schema={
            "segmentation_results": {"type": "object"},
            "radiomics_features": {"type": "object"},
            "ai_insights": {"type": "object"}
        }
    ),
    
    "pico_automation": IOFlow(
        flow_id="pico_automation_001",
        flow_name="PICO Otomasyonu",
        flow_type=FlowType.PICO_AUTOMATION,
        description="Kanıta dayalı tıp için PICO sorusu otomasyonu",
        steps=[
            FlowStep(
                step_id="step_1",
                step_name="Klinik Veri Analizi",
                input_type=InputType.PATIENT_DATA,
                output_type=OutputType.PICO_QUESTION,
                processing_time=1.0,
                success_rate=0.92
            ),
            FlowStep(
                step_id="step_2",
                step_name="PICO Sorusu Oluşturma",
                input_type=InputType.CLINICAL_QUERY,
                output_type=OutputType.PICO_QUESTION,
                processing_time=0.5,
                success_rate=0.95,
                dependencies=["step_1"]
            ),
            FlowStep(
                step_id="step_3",
                step_name="Literatür Arama",
                input_type=InputType.CLINICAL_QUERY,
                output_type=OutputType.EVIDENCE_SUMMARY,
                processing_time=3.0,
                success_rate=0.88,
                dependencies=["step_2"]
            ),
            FlowStep(
                step_id="step_4",
                step_name="GRADE Değerlendirme",
                input_type=InputType.CLINICAL_QUERY,
                output_type=OutputType.EVIDENCE_SUMMARY,
                processing_time=1.0,
                success_rate=0.90,
                dependencies=["step_3"]
            )
        ],
        total_processing_time=5.5,
        success_rate=0.91,
        input_schema={
            "patient_data": {"type": "object", "required": True},
            "clinical_context": {"type": "string", "required": True}
        },
        output_schema={
            "pico_question": {"type": "object"},
            "evidence_summary": {"type": "object"},
            "grade_assessment": {"type": "object"}
        }
    )
}

class SystemResponse(BaseModel):
    response_id: str
    flow_id: str
    status: str
    processing_time: float
    success: bool
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    error_message: Optional[str] = None
    timestamp: datetime
    performance_metrics: Dict[str, float]

def get_flow_definition(flow_type: str) -> Optional[IOFlow]:
    """Belirtilen flow tipinin tanımını getir"""
    return DEFINED_FLOWS.get(flow_type)

def get_all_flows() -> Dict[str, IOFlow]:
    """Tüm flow tanımlarını getir"""
    return DEFINED_FLOWS

def calculate_flow_performance(flow_id: str, actual_processing_time: float, success: bool) -> Dict[str, float]:
    """Flow performansını hesapla"""
    flow = DEFINED_FLOWS.get(flow_id)
    if not flow:
        return {}
    
    expected_time = flow.total_processing_time
    time_efficiency = (expected_time / actual_processing_time) * 100 if actual_processing_time > 0 else 0
    
    return {
        "expected_processing_time": expected_time,
        "actual_processing_time": actual_processing_time,
        "time_efficiency": time_efficiency,
        "success_rate": flow.success_rate,
        "actual_success": 1.0 if success else 0.0
    }

def validate_flow_input(flow_id: str, input_data: Dict[str, Any]) -> bool:
    """Flow girdi verilerini doğrula"""
    flow = DEFINED_FLOWS.get(flow_id)
    if not flow:
        return False
    
    required_fields = [k for k, v in flow.input_schema.items() if v.get("required", False)]
    
    for field in required_fields:
        if field not in input_data:
            return False
    
    return True

def get_flow_statistics() -> Dict[str, Any]:
    """Flow istatistiklerini getir"""
    total_flows = len(DEFINED_FLOWS)
    total_steps = sum(len(flow.steps) for flow in DEFINED_FLOWS.values())
    avg_processing_time = sum(flow.total_processing_time for flow in DEFINED_FLOWS.values()) / total_flows
    avg_success_rate = sum(flow.success_rate for flow in DEFINED_FLOWS.values()) / total_flows
    
    return {
        "total_flows": total_flows,
        "total_steps": total_steps,
        "average_processing_time": avg_processing_time,
        "average_success_rate": avg_success_rate,
        "flow_types": list(set(flow.flow_type for flow in DEFINED_FLOWS.values())),
        "input_types": list(set(step.input_type for flow in DEFINED_FLOWS.values() for step in flow.steps)),
        "output_types": list(set(step.output_type for flow in DEFINED_FLOWS.values() for step in flow.steps))
    }

