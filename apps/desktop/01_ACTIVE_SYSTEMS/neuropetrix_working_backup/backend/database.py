import sqlite3
import os
from pathlib import Path

DATABASE_PATH = Path(__file__).parent / "neuropetrix.db"

def init_database():
    """Veritabanını başlat ve tabloları oluştur"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Report Templates tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS report_templates(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            modality TEXT NOT NULL,
            name TEXT NOT NULL,
            jinja TEXT NOT NULL,
            is_default INTEGER NOT NULL DEFAULT 1
        )
    """)
    
    # Sentence Bank tablosu
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sentence_bank(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            key TEXT NOT NULL UNIQUE,
            text TEXT NOT NULL
        )
    """)
    
    # Varsayılan TSNM template'i ekle
    cursor.execute("""
        INSERT OR IGNORE INTO report_templates (modality, name, jinja, is_default) 
        VALUES (?, ?, ?, ?)
    """, (
        "TSNM",
        "TSNM Standard Template",
        """
# TSNM Raporu - {{ patient_id }}

## Teknik Bilgiler
- **Cihaz:** {{ device_model }}
- **FDG Dozu:** {{ fdg_dose_mbq }} MBq
- **Glisemi:** {{ glycemia_mgdl }} mg/dL
- **Açlık Süresi:** {{ fasting_hours }} saat

## Bulgular
{% for finding in findings %}
### {{ finding.category }}
{{ finding.description }}
{% endfor %}

## Yorum
{{ interpretation }}

## Sonuç
{{ conclusion }}

## Öneriler
{% for recommendation in recommendations %}
- {{ recommendation.text }}
{% endfor %}
        """,
        1
    ))
    
    # Varsayılan cümle bankası ekle
    default_sentences = [
        ("bulgu", "primer_lez", "Primer lezyon olarak sağ üst lob anterior segmentte 2.5x2.0 cm boyutunda FDG tutulumu artışı gösteren nodüler lezyon izlenmektedir."),
        ("bulgu", "lenf_nodu", "Sağ hiler ve mediastinal lenf nodlarında FDG tutulumu artışı mevcuttur."),
        ("bulgu", "uzak_met", "Uzak metastaz bulgusu saptanmamıştır."),
        ("yorum", "ilk_defa", "İlk kez yapılan TSNM incelemesinde malignite şüphesi uyandıran bulgular mevcuttur."),
        ("yorum", "malignite_suphe", "FDG tutulumu artışı malignite şüphesi uyandırmaktadır."),
        ("yorum", "klinik_onem", "Bu bulgular klinik olarak önem taşımaktadır."),
        ("öneri", "onerilen_mudahale", "Histopatolojik doğrulama için biyopsi önerilir."),
        ("öneri", "takip", "3 ay sonra kontrol TSNM önerilir."),
        ("öneri", "cerrahi", "Cerrahi rezeksiyon değerlendirilmelidir.")
    ]
    
    for category, key, text in default_sentences:
        cursor.execute("""
            INSERT OR IGNORE INTO sentence_bank (category, key, text) 
            VALUES (?, ?, ?)
        """, (category, key, text))
    
    conn.commit()
    conn.close()

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
    print("Veritabanı başlatıldı ve tablolar oluşturuldu!")
