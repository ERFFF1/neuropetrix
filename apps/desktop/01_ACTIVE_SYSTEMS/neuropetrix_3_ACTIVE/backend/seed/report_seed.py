import sqlite3
import json

def seed_report_data():
    """Rapor verilerini seed et"""
    conn = sqlite3.connect("neuropetrix.db")
    cursor = conn.cursor()
    
    # Örnek rapor verileri
    sample_reports = [
        {
            "patient_id": "P-001",
            "modality": "FDG",
            "version": 1,
            "body": "Sağ akciğer üst lobda 2.5 cm nodül tespit edildi.",
            "structured_json": json.dumps({
                "findings": ["Sağ akciğer üst lobda nodül"],
                "suv_max": 8.5,
                "stage": "T2N0M0"
            })
        },
        {
            "patient_id": "P-002", 
            "modality": "FDG",
            "version": 1,
            "body": "Lenfoma evrelemesi için yapılan incelemede patolojik bulgu saptanmadı.",
            "structured_json": json.dumps({
                "findings": ["Normal FDG dağılımı"],
                "suv_max": 2.1,
                "stage": "Normal"
            })
        }
    ]
    
    for report in sample_reports:
        cursor.execute("""
            INSERT OR IGNORE INTO reports 
            (patient_id, modality, version, body, structured_json)
            VALUES (?, ?, ?, ?, ?)
        """, (
            report["patient_id"],
            report["modality"], 
            report["version"],
            report["body"],
            report["structured_json"]
        ))
    
    conn.commit()
    conn.close()
    print("Rapor verileri seed edildi!")

if __name__ == "__main__":
    seed_report_data()
