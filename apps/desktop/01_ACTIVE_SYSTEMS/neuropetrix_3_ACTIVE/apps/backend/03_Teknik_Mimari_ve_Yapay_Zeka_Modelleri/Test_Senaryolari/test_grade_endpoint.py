import requests
import json
import time

def test_grade_endpoint():
    """GRADE endpoint'ini test et"""
    
    # Test verisi
    test_data = {
        "patient_data": {
            "age": 65,
            "gender": "M",
            "diagnosis": "Lung cancer"
        },
        "clinical_context": "Suspicious lung nodule on CT"
    }
    
    try:
        # POST isteği gönder
        response = requests.post(
            "http://localhost:8000/pico/generate",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print("✅ GRADE endpoint test başarılı!")
        else:
            print("❌ GRADE endpoint test başarısız!")
            
    except Exception as e:
        print(f"❌ Test hatası: {str(e)}")

def test_evidence_search():
    """Evidence search endpoint'ini test et"""
    
    test_data = {
        "picoQuestion": {
            "population": "65 yaşında erkek hasta",
            "intervention": "FDG-PET/CT görüntüleme",
            "comparison": "Standart görüntüleme",
            "outcome": "Tanısal doğruluk"
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/evidence/search",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"Evidence Search Status: {response.status_code}")
        print(f"Evidence Response: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"Evidence search test hatası: {str(e)}")

if __name__ == "__main__":
    print("🧪 NeuroPETrix Test Senaryoları Başlatılıyor...")
    
    # GRADE endpoint testi
    print("\n1. GRADE Endpoint Testi:")
    test_grade_endpoint()
    
    # Evidence search testi
    print("\n2. Evidence Search Testi:")
    test_evidence_search()
    
    print("\n✅ Tüm testler tamamlandı!")


