from typing import Dict, Any
from datetime import datetime

def render_report(report_data: Dict[str, Any]) -> str:
    """Rapor render etme"""
    try:
        # Basit rapor şablonu
        template = """# {title}

## Hasta Bilgileri
- **Ad:** {name}
- **Yaş:** {age}
- **Cinsiyet:** {gender}

## Bulgular
{findings}

## Sonuç
{conclusion}

---
*Rapor {timestamp} tarihinde oluşturuldu.*
"""
        
        return template.format(
            title=report_data.get("title", "PET/CT Raporu"),
            name=report_data.get("patient", {}).get("name", "N/A"),
            age=report_data.get("patient", {}).get("age", "N/A"),
            gender=report_data.get("patient", {}).get("gender", "N/A"),
            findings=report_data.get("findings", "Bulgular henüz girilmemiş."),
            conclusion=report_data.get("conclusion", "Sonuç henüz girilmemiş."),
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
    except Exception as e:
        return f"Rapor oluşturma hatası: {str(e)}"
