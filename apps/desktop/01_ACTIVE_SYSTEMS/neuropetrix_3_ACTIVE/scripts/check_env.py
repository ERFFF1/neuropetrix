#!/usr/bin/env python3
"""
Environment files checker for NeuroPETRIX
Otomatik .env dosyaları kontrolü ve hata yakalama
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import re

class EnvironmentChecker:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.env_files = [
            ".env",
            ".env.local", 
            ".env.development.local",
            ".env.production"
        ]
        self.required_vars = {
            "backend": [
                "APP_ENV",
                "JWT_SECRET", 
                "DATABASE_URL",
                "VITE_API_BASE"
            ],
            "frontend": [
                "VITE_API_BASE",
                "VITE_GEMINI_API_KEY"
            ]
        }
        self.errors = []
        self.warnings = []

    def check_env_files(self) -> bool:
        """Tüm .env dosyalarını kontrol et"""
        print("🔍 Environment dosyaları kontrol ediliyor...")
        
        for env_file in self.env_files:
            env_path = self.project_root / env_file
            if env_path.exists():
                self._check_single_env_file(env_path)
            else:
                self.warnings.append(f"⚠️  {env_file} dosyası bulunamadı")
        
        return len(self.errors) == 0

    def _check_single_env_file(self, env_path: Path):
        """Tek bir .env dosyasını kontrol et"""
        print(f"📄 {env_path.name} kontrol ediliyor...")
        
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Boş satırları ve yorumları temizle
            lines = [line.strip() for line in content.split('\n') 
                    if line.strip() and not line.strip().startswith('#')]
            
            # Değişkenleri parse et
            env_vars = {}
            for line in lines:
                if '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
            
            # Gerekli değişkenleri kontrol et
            self._check_required_vars(env_path.name, env_vars)
            
            # Güvenlik kontrolü
            self._check_security_issues(env_path.name, env_vars)
            
            # Format kontrolü
            self._check_format_issues(env_path.name, content)
            
        except Exception as e:
            self.errors.append(f"❌ {env_path.name}: Dosya okuma hatası - {e}")

    def _check_required_vars(self, filename: str, env_vars: Dict[str, str]):
        """Gerekli değişkenleri kontrol et"""
        # Backend değişkenleri
        for var in self.required_vars["backend"]:
            if var not in env_vars:
                self.errors.append(f"❌ {filename}: Gerekli değişken eksik - {var}")
            elif not env_vars[var] or env_vars[var] == "change_me_in_production":
                self.warnings.append(f"⚠️  {filename}: {var} değeri varsayılan/boş")

    def _check_security_issues(self, filename: str, env_vars: Dict[str, str]):
        """Güvenlik sorunlarını kontrol et"""
        # JWT Secret kontrolü
        if "JWT_SECRET" in env_vars:
            jwt_secret = env_vars["JWT_SECRET"]
            if len(jwt_secret) < 32:
                self.errors.append(f"❌ {filename}: JWT_SECRET çok kısa (min 32 karakter)")
            if jwt_secret == "change_me_in_production":
                self.errors.append(f"❌ {filename}: JWT_SECRET production değeri kullanılıyor")
        
        # API Key kontrolü
        if "VITE_GEMINI_API_KEY" in env_vars:
            api_key = env_vars["VITE_GEMINI_API_KEY"]
            if api_key == "your_gemini_api_key_here":
                self.warnings.append(f"⚠️  {filename}: VITE_GEMINI_API_KEY varsayılan değer")
        
        # Database URL kontrolü
        if "DATABASE_URL" in env_vars:
            db_url = env_vars["DATABASE_URL"]
            if "password" in db_url.lower() and "localhost" not in db_url:
                self.warnings.append(f"⚠️  {filename}: Production database URL tespit edildi")

    def _check_format_issues(self, filename: str, content: str):
        """Format sorunlarını kontrol et"""
        lines = content.split('\n')
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            # Boş değişken kontrolü
            if line and '=' in line and not line.startswith('#'):
                key, value = line.split('=', 1)
                if not value.strip():
                    self.warnings.append(f"⚠️  {filename}:{i} Boş değer - {key}")
            
            # Çift eşittir kontrolü
            if '==' in line and not line.startswith('#'):
                self.errors.append(f"❌ {filename}:{i} Çift eşittir hatası - {line}")
            
            # Trailing space kontrolü
            if line != line.rstrip():
                self.warnings.append(f"⚠️  {filename}:{i} Trailing space")

    def check_duplicate_vars(self) -> bool:
        """Tüm .env dosyalarında tekrarlanan değişkenleri kontrol et"""
        print("🔄 Tekrarlanan değişkenler kontrol ediliyor...")
        
        all_vars = {}
        
        for env_file in self.env_files:
            env_path = self.project_root / env_file
            if env_path.exists():
                try:
                    with open(env_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    lines = [line.strip() for line in content.split('\n') 
                            if line.strip() and not line.strip().startswith('#')]
                    
                    for line in lines:
                        if '=' in line:
                            key, value = line.split('=', 1)
                            key = key.strip()
                            
                            if key in all_vars:
                                if all_vars[key] != value.strip():
                                    self.warnings.append(
                                        f"⚠️  {key} farklı değerlerle tanımlanmış: "
                                        f"{env_file} vs {all_vars[key]['file']}"
                                    )
                            else:
                                all_vars[key] = {
                                    'value': value.strip(),
                                    'file': env_file
                                }
                                
                except Exception as e:
                    self.errors.append(f"❌ {env_file}: Okuma hatası - {e}")
        
        return len(self.errors) == 0

    def generate_report(self) -> str:
        """Kontrol raporu oluştur"""
        report = []
        report.append("=" * 60)
        report.append("🔍 NEUROPETRIX ENVIRONMENT CHECKER RAPORU")
        report.append("=" * 60)
        
        if self.errors:
            report.append(f"\n❌ HATALAR ({len(self.errors)}):")
            for error in self.errors:
                report.append(f"  {error}")
        
        if self.warnings:
            report.append(f"\n⚠️  UYARILAR ({len(self.warnings)}):")
            for warning in self.warnings:
                report.append(f"  {warning}")
        
        if not self.errors and not self.warnings:
            report.append("\n✅ Tüm environment dosyaları başarıyla kontrol edildi!")
        
        report.append(f"\n📊 ÖZET:")
        report.append(f"  - Hata: {len(self.errors)}")
        report.append(f"  - Uyarı: {len(self.warnings)}")
        report.append(f"  - Durum: {'✅ BAŞARILI' if len(self.errors) == 0 else '❌ BAŞARISIZ'}")
        
        return "\n".join(report)

def main():
    """Ana fonksiyon"""
    checker = EnvironmentChecker()
    
    # Environment dosyalarını kontrol et
    env_ok = checker.check_env_files()
    
    # Tekrarlanan değişkenleri kontrol et
    duplicate_ok = checker.check_duplicate_vars()
    
    # Rapor oluştur
    report = checker.generate_report()
    print(report)
    
    # Exit code
    if env_ok and duplicate_ok:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
