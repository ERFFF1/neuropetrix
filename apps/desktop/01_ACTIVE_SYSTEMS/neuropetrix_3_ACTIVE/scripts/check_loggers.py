#!/usr/bin/env python3
"""
Logger usage checker for NeuroPETRIX
Otomatik logger kullanımı kontrolü ve standartlaştırma
"""

import ast
import sys
import os
from pathlib import Path
from typing import List, Dict, Set, Tuple
import re

class LoggerChecker:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_path = self.project_root / "backend"
        self.errors = []
        self.warnings = []
        self.suggestions = []
        
        # Logger standartları
        self.standard_logger_name = "logger"
        self.required_logger_imports = [
            "import logging",
            "from logging import getLogger",
            "from backend.core.logging_config import get_logger"
        ]
        
        # Logger seviyeleri
        self.log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
        # Logger kullanımı olması gereken dosyalar
        self.logger_required_files = [
            "routers/",
            "services/",
            "core/",
            "ai_scripts/"
        ]

    def check_file_loggers(self, file_path: Path) -> bool:
        """Tek bir dosyadaki logger kullanımını kontrol et"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # AST parse et
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                self.errors.append(f"❌ {file_path}: Syntax hatası - {e}")
                return False
            
            # Logger kullanımını kontrol et
            self._check_logger_imports(file_path, content)
            self._check_logger_usage(file_path, tree)
            self._check_logger_standards(file_path, content)
            
            return len(self.errors) == 0
            
        except Exception as e:
            self.errors.append(f"❌ {file_path}: Dosya okuma hatası - {e}")
            return False

    def _check_logger_imports(self, file_path: Path, content: str):
        """Logger import'larını kontrol et"""
        lines = content.split('\n')
        
        # Logger import'u var mı?
        has_logger_import = False
        for line in lines:
            if any(import_stmt in line for import_stmt in self.required_logger_imports):
                has_logger_import = True
                break
        
        # Logger kullanımı var mı?
        has_logger_usage = any(level.lower() in content.lower() for level in self.log_levels)
        
        # Logger kullanımı varsa import da olmalı
        if has_logger_usage and not has_logger_import:
            self.errors.append(f"❌ {file_path}: Logger kullanımı var ama import eksik")
            self.suggestions.append(f"💡 {file_path}: 'import logging' veya 'from logging import getLogger' ekleyin")
        
        # Logger import'u varsa kullanım da olmalı
        if has_logger_import and not has_logger_usage:
            self.warnings.append(f"⚠️  {file_path}: Logger import'u var ama kullanılmıyor")

    def _check_logger_usage(self, file_path: Path, tree: ast.AST):
        """Logger kullanımını kontrol et"""
        for node in ast.walk(tree):
            # Function call'ları kontrol et
            if isinstance(node, ast.Call):
                self._check_logger_call(file_path, node)
            
            # Variable assignment'ları kontrol et
            elif isinstance(node, ast.Assign):
                self._check_logger_assignment(file_path, node)

    def _check_logger_call(self, file_path: Path, node: ast.Call):
        """Logger call'ını kontrol et"""
        # Attribute access kontrolü (logger.info, logger.error, etc.)
        if isinstance(node.func, ast.Attribute):
            if hasattr(node.func.value, 'id'):
                var_name = node.func.value.id
                method_name = node.func.attr
                
                # Logger method'u mu?
                if method_name.lower() in [level.lower() for level in self.log_levels]:
                    # Standart logger ismi kullanılıyor mu?
                    if var_name != self.standard_logger_name:
                        self.warnings.append(
                            f"⚠️  {file_path}:{node.lineno} Standart olmayan logger ismi: {var_name}"
                        )
                        self.suggestions.append(
                            f"💡 {file_path}:{node.lineno} '{var_name}' yerine 'logger' kullanın"
                        )
                    
                    # Log mesajı kontrolü
                    if node.args:
                        self._check_log_message(file_path, node)

    def _check_logger_assignment(self, file_path: Path, node: ast.Assign):
        """Logger assignment'ını kontrol et"""
        for target in node.targets:
            if isinstance(target, ast.Name):
                var_name = target.id
                
                # Logger assignment'ı mı?
                if isinstance(node.value, ast.Call):
                    if isinstance(node.value.func, ast.Name):
                        func_name = node.value.func.id
                        if func_name in ['getLogger', 'logging.getLogger']:
                            # Standart logger ismi kullanılıyor mu?
                            if var_name != self.standard_logger_name:
                                self.warnings.append(
                                    f"⚠️  {file_path}:{node.lineno} Standart olmayan logger ismi: {var_name}"
                                )
                                self.suggestions.append(
                                    f"💡 {file_path}:{node.lineno} '{var_name}' yerine 'logger' kullanın"
                                )

    def _check_log_message(self, file_path: Path, node: ast.Call):
        """Log mesajını kontrol et"""
        if not node.args:
            self.warnings.append(f"⚠️  {file_path}:{node.lineno} Boş log mesajı")
            return
        
        # İlk argüman mesaj
        message_arg = node.args[0]
        
        # String literal kontrolü
        if isinstance(message_arg, ast.Constant) and isinstance(message_arg.value, str):
            message = message_arg.value
            
            # Mesaj formatı kontrolü
            if not message.strip():
                self.warnings.append(f"⚠️  {file_path}:{node.lineno} Boş log mesajı")
            
            # Türkçe karakter kontrolü
            if any(ord(char) > 127 for char in message):
                self.warnings.append(f"⚠️  {file_path}:{node.lineno} Türkçe karakter içeren log mesajı")
        
        # F-string kullanımı öner
        elif isinstance(message_arg, ast.BinOp) and isinstance(message_arg.op, ast.Mod):
            self.suggestions.append(
                f"💡 {file_path}:{node.lineno} % formatting yerine f-string kullanmayı düşünün"
            )

    def _check_logger_standards(self, file_path: Path, content: str):
        """Logger standartlarını kontrol et"""
        lines = content.split('\n')
        
        # Print statement kontrolü
        for i, line in enumerate(lines, 1):
            if 'print(' in line and not line.strip().startswith('#'):
                self.warnings.append(f"⚠️  {file_path}:{i} print() kullanımı - logger kullanmayı düşünün")
                self.suggestions.append(f"💡 {file_path}:{i} print() yerine logger.info() kullanın")
        
        # Exception handling kontrolü
        if 'except' in content and 'logger.error' not in content:
            self.warnings.append(f"⚠️  {file_path}: Exception handling var ama logger.error kullanılmıyor")
            self.suggestions.append(f"💡 {file_path}: Exception'larda logger.error() kullanın")

    def check_all_backend_files(self) -> bool:
        """Tüm backend dosyalarını kontrol et"""
        print("🔍 Backend logger kullanımı kontrol ediliyor...")
        
        if not self.backend_path.exists():
            self.errors.append(f"❌ Backend dizini bulunamadı: {self.backend_path}")
            return False
        
        # Tüm Python dosyalarını bul
        python_files = list(self.backend_path.rglob("*.py"))
        
        print(f"📁 {len(python_files)} Python dosyası bulundu")
        
        success_count = 0
        for py_file in python_files:
            if self.check_file_loggers(py_file):
                success_count += 1
        
        print(f"✅ {success_count}/{len(python_files)} dosya başarıyla kontrol edildi")
        
        return len(self.errors) == 0

    def generate_logger_template(self) -> str:
        """Standart logger template'i oluştur"""
        template = '''
# Standart Logger Template
import logging
from typing import Optional

# Logger oluştur
logger = logging.getLogger(__name__)

# Logger kullanım örnekleri
def example_function():
    """Örnek fonksiyon"""
    try:
        logger.info("Fonksiyon başlatıldı")
        
        # İşlem yap
        result = some_operation()
        
        logger.info(f"İşlem tamamlandı: {result}")
        return result
        
    except Exception as e:
        logger.error(f"İşlem hatası: {e}", exc_info=True)
        raise

# Logger seviyeleri
logger.debug("Debug mesajı")
logger.info("Bilgi mesajı")
logger.warning("Uyarı mesajı")
logger.error("Hata mesajı")
logger.critical("Kritik hata mesajı")
'''
        return template

    def generate_report(self) -> str:
        """Kontrol raporu oluştur"""
        report = []
        report.append("=" * 60)
        report.append("🔍 NEUROPETRIX LOGGER CHECKER RAPORU")
        report.append("=" * 60)
        
        if self.errors:
            report.append(f"\n❌ HATALAR ({len(self.errors)}):")
            for error in self.errors:
                report.append(f"  {error}")
        
        if self.warnings:
            report.append(f"\n⚠️  UYARILAR ({len(self.warnings)}):")
            for warning in self.warnings:
                report.append(f"  {warning}")
        
        if self.suggestions:
            report.append(f"\n💡 ÖNERİLER ({len(self.suggestions)}):")
            for suggestion in self.suggestions:
                report.append(f"  {suggestion}")
        
        if not self.errors and not self.warnings:
            report.append("\n✅ Tüm logger kullanımları standartlara uygun!")
        
        report.append(f"\n📊 ÖZET:")
        report.append(f"  - Hata: {len(self.errors)}")
        report.append(f"  - Uyarı: {len(self.warnings)}")
        report.append(f"  - Öneri: {len(self.suggestions)}")
        report.append(f"  - Durum: {'✅ BAŞARILI' if len(self.errors) == 0 else '❌ BAŞARISIZ'}")
        
        # Logger template'i ekle
        if self.errors or self.warnings:
            report.append(f"\n📝 STANDART LOGGER TEMPLATE:")
            report.append(self.generate_logger_template())
        
        return "\n".join(report)

def main():
    """Ana fonksiyon"""
    checker = LoggerChecker()
    
    # Backend dosyalarını kontrol et
    backend_ok = checker.check_all_backend_files()
    
    # Rapor oluştur
    report = checker.generate_report()
    print(report)
    
    # Exit code
    if backend_ok:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
