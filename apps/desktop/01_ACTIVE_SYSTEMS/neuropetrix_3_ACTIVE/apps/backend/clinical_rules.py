# Clinical rules for NeuroPETrix

CLINICAL_RULES = {
    "lung_cancer": {
        "screening": {
            "age_range": [55, 80],
            "smoking_history": "30+ pack years",
            "quit_smoking": "15 years or less",
            "recommendation": "Annual LDCT screening"
        },
        "staging": {
            "pet_ct_indication": "Suspicious nodules >8mm",
            "biopsy_threshold": "SUVmax >2.5",
            "follow_up": "3-6 months for indeterminate nodules"
        }
    },
    "lymphoma": {
        "staging": {
            "pet_ct_required": True,
            "deauville_criteria": True,
            "interim_pet": "After 2-4 cycles",
            "end_of_treatment": True
        },
        "response_assessment": {
            "deauville_1_2": "Complete response",
            "deauville_3": "Partial response",
            "deauville_4_5": "Progressive disease"
        }
    },
    "prostate_cancer": {
        "psma_pet": {
            "indication": "Biochemical recurrence",
            "psa_threshold": "0.2 ng/mL",
            "staging": "High-risk disease",
            "restaging": "After treatment failure"
        }
    }
}

def get_clinical_rule(cancer_type: str, rule_type: str) -> dict:
    """Klinik kural getir"""
    return CLINICAL_RULES.get(cancer_type, {}).get(rule_type, {})

def apply_clinical_rule(patient_data: dict, cancer_type: str, rule_type: str) -> dict:
    """Klinik kuralı uygula"""
    rule = get_clinical_rule(cancer_type, rule_type)
    
    if not rule:
        return {"recommendation": "Kural bulunamadı"}
    
    # Basit kural uygulama
    result = {
        "rule_applied": f"{cancer_type}_{rule_type}",
        "recommendation": rule.get("recommendation", "Öneri bulunamadı"),
        "confidence": 0.8
    }
    
    return result