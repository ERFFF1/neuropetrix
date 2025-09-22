#!/bin/bash

echo "🧪 NeuroPETrix Schema Validation Testleri"

# Test verileri
TEST_DATA='{
  "patient_data": {
    "name": "Test Patient",
    "age": 65,
    "gender": "M",
    "diagnosis": "Lung cancer"
  },
  "imaging_data": {
    "dicom_files": ["file1.dcm", "file2.dcm"],
    "modality": "PT",
    "acquisition_date": "2024-01-15"
  }
}'

echo "1. Patient Data Validation Testi:"
curl -X POST http://localhost:8000/validate/patient \
  -H "Content-Type: application/json" \
  -d '{"name": "Test Patient", "age": 65, "gender": "M"}'

echo -e "\n\n2. Imaging Data Validation Testi:"
curl -X POST http://localhost:8000/validate/imaging \
  -H "Content-Type: application/json" \
  -d '{"dicom_files": ["file1.dcm"], "modality": "PT"}'

echo -e "\n\n3. PICO Question Validation Testi:"
curl -X POST http://localhost:8000/pico/validate \
  -H "Content-Type: application/json" \
  -d '{
    "picoQuestion": {
      "population": "65 yaşında erkek hasta",
      "intervention": "FDG-PET/CT",
      "comparison": "Standart görüntüleme",
      "outcome": "Tanısal doğruluk"
    }
  }'

echo -e "\n\n✅ Schema validation testleri tamamlandı!"


