"""
PDF Report Generation Service
NeuroPETRIX - Medical AI Analysis Reports
"""

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class PDFReportService:
    """PDF rapor oluşturma servisi"""
    
    def __init__(self):
        self.reports_dir = Path("backend/reports")
        self.reports_dir.mkdir(exist_ok=True)
        
    def generate_case_report(self, case_data: Dict[str, Any]) -> str:
        """Vaka raporu oluştur"""
        try:
            # Rapor ID oluştur
            report_id = f"report_{case_data.get('id', 'unknown')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # HTML template oluştur
            html_content = self._create_html_template(case_data)
            
            # HTML dosyasını kaydet
            html_file = self.reports_dir / f"{report_id}.html"
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"PDF raporu oluşturuldu: {report_id}")
            return str(html_file)
            
        except Exception as e:
            logger.error(f"PDF raporu oluşturulamadı: {e}")
            raise
    
    def _create_html_template(self, case_data: Dict[str, Any]) -> str:
        """HTML template oluştur"""
        
        # Hasta bilgileri
        patient_data = case_data.get('patientData', {})
        analysis = case_data.get('analysis', {})
        
        html = f"""
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>NeuroPETRIX - Vaka Raporu</title>
            <style>
                body {{
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                    line-height: 1.6;
                    color: #333;
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                    background-color: #f8f9fa;
                }}
                .header {{
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 30px;
                    border-radius: 10px;
                    text-align: center;
                    margin-bottom: 30px;
                }}
                .header h1 {{
                    margin: 0;
                    font-size: 2.5em;
                    font-weight: 300;
                }}
                .header p {{
                    margin: 10px 0 0 0;
                    opacity: 0.9;
                }}
                .section {{
                    background: white;
                    padding: 25px;
                    margin-bottom: 20px;
                    border-radius: 8px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .section h2 {{
                    color: #667eea;
                    border-bottom: 2px solid #667eea;
                    padding-bottom: 10px;
                    margin-bottom: 20px;
                }}
                .info-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                }}
                .info-item {{
                    display: flex;
                    justify-content: space-between;
                    padding: 10px 0;
                    border-bottom: 1px solid #eee;
                }}
                .info-label {{
                    font-weight: 600;
                    color: #555;
                }}
                .info-value {{
                    color: #333;
                }}
                .analysis-result {{
                    background: #f8f9fa;
                    padding: 20px;
                    border-radius: 8px;
                    border-left: 4px solid #28a745;
                }}
                .summary {{
                    background: #e3f2fd;
                    padding: 20px;
                    border-radius: 8px;
                    border-left: 4px solid #2196f3;
                }}
                .footer {{
                    text-align: center;
                    margin-top: 40px;
                    padding: 20px;
                    color: #666;
                    font-size: 0.9em;
                }}
                .qr-code {{
                    text-align: center;
                    margin: 20px 0;
                }}
                .qr-code img {{
                    width: 100px;
                    height: 100px;
                }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>NeuroPETRIX</h1>
                <p>AI Destekli Tıbbi Analiz Raporu</p>
                <p>Rapor Tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
            </div>
            
            <div class="section">
                <h2>Hasta Bilgileri</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">Hasta ID:</span>
                        <span class="info-value">{patient_data.get('patientId', 'N/A')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Yaş:</span>
                        <span class="info-value">{patient_data.get('age', 'N/A')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Cinsiyet:</span>
                        <span class="info-value">{patient_data.get('gender', 'N/A')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Amaç:</span>
                        <span class="info-value">{case_data.get('purpose', 'N/A')}</span>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>Vital Bulgular</h2>
                <div class="info-grid">
                    <div class="info-item">
                        <span class="info-label">Kan Basıncı:</span>
                        <span class="info-value">{patient_data.get('vitals', {}).get('bloodPressure', 'N/A')}</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Kalp Atışı:</span>
                        <span class="info-value">{patient_data.get('vitals', {}).get('heartRate', 'N/A')} bpm</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Vücut Sıcaklığı:</span>
                        <span class="info-value">{patient_data.get('vitals', {}).get('temperature', 'N/A')}°C</span>
                    </div>
                    <div class="info-item">
                        <span class="info-label">Oksijen Satürasyonu:</span>
                        <span class="info-value">{patient_data.get('vitals', {}).get('oxygenSaturation', 'N/A')}%</span>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>AI Analiz Sonuçları</h2>
                <div class="analysis-result">
                    <h3>Özet</h3>
                    <p>{analysis.get('summary', 'Analiz sonucu bulunamadı.')}</p>
                </div>
                
                <div class="summary">
                    <h3>Diferansiyel Tanı</h3>
                    <ul>
                        {self._format_differential_diagnosis(analysis.get('differentialDiagnosis', []))}
                    </ul>
                </div>
                
                <div class="analysis-result">
                    <h3>Öneriler</h3>
                    <ul>
                        {self._format_suggestions(analysis.get('suggestions', []))}
                    </ul>
                </div>
            </div>
            
            <div class="section">
                <h2>Güvenlik ve Doğrulama</h2>
                <div class="qr-code">
                    <p>Rapor Doğrulama Kodu:</p>
                    <p style="font-family: monospace; font-size: 1.2em; color: #667eea;">
                        {report_id.upper()}
                    </p>
                </div>
                <p style="text-align: center; color: #666; font-size: 0.9em;">
                    Bu rapor NeuroPETRIX AI sistemi tarafından oluşturulmuştur.<br>
                    Rapor tarihi: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
                </p>
            </div>
            
            <div class="footer">
                <p>NeuroPETRIX v1.5.0 - AI Destekli Tıbbi Analiz Sistemi</p>
                <p>Bu rapor sadece bilgilendirme amaçlıdır ve profesyonel tıbbi görüş yerine geçmez.</p>
            </div>
        </body>
        </html>
        """
        
        return html
    
    def _format_differential_diagnosis(self, diagnoses: list) -> str:
        """Diferansiyel tanı formatla"""
        if not diagnoses:
            return "<li>Diferansiyel tanı bulunamadı.</li>"
        
        return "".join([f"<li>{diag}</li>" for diag in diagnoses])
    
    def _format_suggestions(self, suggestions: list) -> str:
        """Öneriler formatla"""
        if not suggestions:
            return "<li>Öneri bulunamadı.</li>"
        
        return "".join([f"<li>{suggestion}</li>" for suggestion in suggestions])
    
    def create_shareable_link(self, report_id: str, expires_hours: int = 24) -> Dict[str, Any]:
        """Paylaşılabilir link oluştur"""
        try:
            # Link oluştur
            share_id = f"share_{report_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            expires_at = datetime.now().timestamp() + (expires_hours * 3600)
            
            share_data = {
                "share_id": share_id,
                "report_id": report_id,
                "expires_at": expires_at,
                "max_views": 10,
                "current_views": 0,
                "created_at": datetime.now().isoformat()
            }
            
            # Share data'yı kaydet
            share_file = self.reports_dir / f"{share_id}.json"
            with open(share_file, 'w', encoding='utf-8') as f:
                json.dump(share_data, f, indent=2, ensure_ascii=False)
            
            # Paylaşılabilir URL
            share_url = f"http://localhost:8000/reports/share/{share_id}"
            
            logger.info(f"Paylaşılabilir link oluşturuldu: {share_id}")
            
            return {
                "share_id": share_id,
                "share_url": share_url,
                "expires_at": datetime.fromtimestamp(expires_at).isoformat(),
                "max_views": 10
            }
            
        except Exception as e:
            logger.error(f"Paylaşılabilir link oluşturulamadı: {e}")
            raise

# Singleton instance
pdf_service = PDFReportService()
