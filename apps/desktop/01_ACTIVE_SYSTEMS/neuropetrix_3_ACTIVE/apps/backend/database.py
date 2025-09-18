import sqlite3
import os
from datetime import datetime

DATABASE_PATH = "neuropetrix.db"

def init_database():
    """Veritabanını başlat ve tabloları oluştur"""
    conn = sqlite3.connect("neuropetrix.db")
    cursor = conn.cursor()
    
    # Mevcut tabloları sil (eğer varsa)
    cursor.execute("DROP TABLE IF EXISTS suv_measurements")
    cursor.execute("DROP TABLE IF EXISTS clinical_recommendations")
    cursor.execute("DROP TABLE IF EXISTS critical_appraisals")
    cursor.execute("DROP TABLE IF EXISTS evidence_searches")
    cursor.execute("DROP TABLE IF EXISTS pico_questions")
    cursor.execute("DROP TABLE IF EXISTS patient_cases")
    cursor.execute("DROP TABLE IF EXISTS patients")
    cursor.execute("DROP TABLE IF EXISTS multimodal_data")
    cursor.execute("DROP TABLE IF EXISTS clinical_feedback")
    cursor.execute("DROP TABLE IF EXISTS audit_trail")
    cursor.execute("DROP TABLE IF EXISTS compliance_logs")
    
    # Hasta tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            diagnosis TEXT NOT NULL,
            icd_codes TEXT,
            medications TEXT,
            comorbidities TEXT,
            clinical_goals TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Hasta vakaları tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patient_cases (
            id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            case_type TEXT NOT NULL,
            clinical_context TEXT NOT NULL,
            imaging_data TEXT,
            lab_data TEXT,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (id)
        )
    """)
    
    # SUV ölçümleri tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS suv_measurements (
            id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            case_id TEXT NOT NULL,
            region TEXT NOT NULL,
            suv_value REAL NOT NULL,
            measurement_date DATETIME NOT NULL,
            region_volume REAL,
            notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (case_id) REFERENCES patient_cases (id)
        )
    """)
    
    # PICO soruları tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS pico_questions (
            id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            case_id TEXT NOT NULL,
            population TEXT NOT NULL,
            intervention TEXT NOT NULL,
            comparison TEXT NOT NULL,
            outcome TEXT NOT NULL,
            clinical_context TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (case_id) REFERENCES patient_cases (id)
        )
    """)
    
    # Kanıt arama tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS evidence_searches (
            id TEXT PRIMARY KEY,
            pico_id TEXT NOT NULL,
            search_query TEXT NOT NULL,
            databases TEXT NOT NULL,
            results_count INTEGER,
            search_date DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pico_id) REFERENCES pico_questions (id)
        )
    """)
    
    # Eleştirel değerlendirme tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS critical_appraisals (
            id TEXT PRIMARY KEY,
            evidence_id TEXT NOT NULL,
            study_type TEXT NOT NULL,
            quality_score REAL,
            bias_assessment TEXT,
            applicability_score REAL,
            grade_level TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (evidence_id) REFERENCES evidence_searches (id)
        )
    """)
    
    # Klinik öneriler tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clinical_recommendations (
            id TEXT PRIMARY KEY,
            appraisal_id TEXT NOT NULL,
            recommendation_text TEXT NOT NULL,
            confidence_level REAL,
            evidence_strength TEXT,
            applicability_notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (appraisal_id) REFERENCES critical_appraisals (id)
        )
    """)
    
    # Multimodal veri tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS multimodal_data (
            id TEXT PRIMARY KEY,
            patient_id TEXT NOT NULL,
            case_id TEXT NOT NULL,
            data_type TEXT NOT NULL,  -- 'imaging', 'clinical', 'textual'
            data_source TEXT NOT NULL,
            data_content TEXT NOT NULL,
            processed_features TEXT,
            fusion_score REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (case_id) REFERENCES patient_cases (id)
        )
    """)
    
    # Klinik geri bildirim tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clinical_feedback (
            id TEXT PRIMARY KEY,
            recommendation_id TEXT NOT NULL,
            feedback_type TEXT NOT NULL,  -- 'positive', 'negative', 'neutral'
            feedback_text TEXT,
            confidence_rating REAL,
            implementation_notes TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (recommendation_id) REFERENCES clinical_recommendations (id)
        )
    """)
    
    # Denetim izi tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS audit_trail (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            action TEXT NOT NULL,
            data_type TEXT NOT NULL,
            data_id TEXT,
            old_value TEXT,
            new_value TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Uyumluluk logları tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS compliance_logs (
            id TEXT PRIMARY KEY,
            regulation_type TEXT NOT NULL,  -- 'KVKK', 'HIPAA', 'GDPR', etc.
            compliance_status TEXT NOT NULL,  -- 'compliant', 'non_compliant', 'pending'
            action_taken TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # İndeksler
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_patients_created ON patients(created_at)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_cases_patient ON patient_cases(patient_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_suv_patient ON suv_measurements(patient_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_suv_region ON suv_measurements(region)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_suv_date ON suv_measurements(measurement_date)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_pico_patient ON pico_questions(patient_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_trail(timestamp)")
    
    conn.commit()
    conn.close()
    print("Veritabanı başlatıldı!")

def seed_sample_data():
    """Örnek veri ekle"""
    conn = sqlite3.connect("neuropetrix.db")
    cursor = conn.cursor()
    
    # Örnek hasta
    cursor.execute("""
        INSERT OR IGNORE INTO patients (id, name, age, gender, diagnosis, icd_codes, medications, comorbidities, clinical_goals)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "P20241225001",
        "Ahmet Yılmaz",
        65,
        "Erkek",
        "Akciğer Kanseri",
        "C34.90,C78.00",
        "Cisplatin,Pemetrexed",
        "Hipertansiyon,Diyabet",
        "Tedavi yanıtı değerlendirme,Progresyon takibi"
    ))
    
    # Örnek vaka
    cursor.execute("""
        INSERT OR IGNORE INTO patient_cases (id, patient_id, case_type, clinical_context, notes)
        VALUES (?, ?, ?, ?, ?)
    """, (
        "C20241225001",
        "P20241225001",
        "initial",
        "İlk PET/CT değerlendirmesi",
        "Hasta kemoterapi öncesi bazal değerlendirme için geldi"
    ))
    
    # Örnek SUV ölçümleri
    suv_measurements = [
        ("SUV20241225001", "P20241225001", "C20241225001", "Primer Lezyon", 8.5, "2024-12-25", 15.2, "Bazal ölçüm"),
        ("SUV20241225002", "P20241225001", "C20241225001", "Lenf Nodu 1", 4.2, "2024-12-25", 8.5, "Mediastinal"),
        ("SUV20241225003", "P20241225001", "C20241225001", "Lenf Nodu 2", 3.8, "2024-12-25", 6.2, "Hiler")
    ]
    
    for measurement in suv_measurements:
        cursor.execute("""
            INSERT OR IGNORE INTO suv_measurements (id, patient_id, case_id, region, suv_value, measurement_date, region_volume, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, measurement)
    
    # Örnek PICO sorusu
    cursor.execute("""
        INSERT OR IGNORE INTO pico_questions (id, patient_id, case_id, population, intervention, comparison, outcome, clinical_context)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        "PICO20241225001",
        "P20241225001",
        "C20241225001",
        "65 yaş üstü akciğer kanseri hastaları",
        "Cisplatin + Pemetrexed kombinasyonu",
        "Sadece destek tedavi",
        "Genel sağkalım ve progresyonsuz sağkalım",
        "İlk basamak tedavi seçimi"
    ))
    
    conn.commit()
    conn.close()
    print("Örnek veriler eklendi!")

def get_db_connection():
    """Veritabanı bağlantısı döndür"""
    return sqlite3.connect(DATABASE_PATH)

def get_report_template(modality="TSNM"):
    """Belirtilen modalite için rapor template'i getir"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT jinja FROM report_templates 
        WHERE modality = ? AND is_default = 1
        LIMIT 1
    """, (modality,))
    
    result = cursor.fetchone()
    conn.close()
    
    return result[0] if result else None

def get_sentence_bank(category=None):
    """Cümle bankasından cümleleri getir"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if category:
        cursor.execute("""
            SELECT key, text FROM sentence_bank 
            WHERE category = ?
            ORDER BY key
        """, (category,))
    else:
        cursor.execute("""
            SELECT category, key, text FROM sentence_bank 
            ORDER BY category, key
        """)
    
    result = cursor.fetchall()
    conn.close()
    
    return result

def add_sentence_bank(category, key, text):
    """Cümle bankasına yeni cümle ekle"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            INSERT INTO sentence_bank (category, key, text) 
            VALUES (?, ?, ?)
        """, (category, key, text))
        conn.commit()
        success = True
    except sqlite3.IntegrityError:
        success = False
    
    conn.close()
    return success

if __name__ == "__main__":
    init_database()
    seed_sample_data()
