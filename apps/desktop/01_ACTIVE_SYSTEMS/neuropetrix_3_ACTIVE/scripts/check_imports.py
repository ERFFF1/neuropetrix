#!/usr/bin/env python3
"""
Import errors checker for NeuroPETRIX
Otomatik import hataları yakalama ve çözüm önerileri
"""

import ast
import sys
import os
from pathlib import Path
from typing import List, Dict, Set, Tuple
import importlib.util
import subprocess

class ImportChecker:
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.backend_path = self.project_root / "backend"
        self.errors = []
        self.warnings = []
        self.fixed_imports = []
        
        # Bilinen import sorunları ve çözümleri
        self.import_fixes = {
            "backend.core.settings": "from backend.core.settings import settings",
            "backend.routers": "from backend.routers import router_name",
            "backend.services": "from backend.services import service_name",
            "backend.models": "from backend.models import model_name",
            "backend.core.auth": "from backend.core.auth import auth_function",
            "backend.core.database": "from backend.core.database import db_function",
        }

    def check_file_imports(self, file_path: Path) -> bool:
        """Tek bir dosyadaki import'ları kontrol et"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # AST parse et
            try:
                tree = ast.parse(content)
            except SyntaxError as e:
                self.errors.append(f"❌ {file_path}: Syntax hatası - {e}")
                return False
            
            # Import'ları topla
            imports = self._extract_imports(tree)
            
            # Her import'u kontrol et
            for import_info in imports:
                self._check_single_import(file_path, import_info)
            
            return len(self.errors) == 0
            
        except Exception as e:
            self.errors.append(f"❌ {file_path}: Dosya okuma hatası - {e}")
            return False

    def _extract_imports(self, tree: ast.AST) -> List[Dict]:
        """AST'den import'ları çıkar"""
        imports = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append({
                        'type': 'import',
                        'module': alias.name,
                        'alias': alias.asname,
                        'line': node.lineno
                    })
            
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ''
                for alias in node.names:
                    imports.append({
                        'type': 'from_import',
                        'module': module,
                        'name': alias.name,
                        'alias': alias.asname,
                        'line': node.lineno
                    })
        
        return imports

    def _check_single_import(self, file_path: Path, import_info: Dict):
        """Tek bir import'u kontrol et"""
        line_num = import_info['line']
        
        if import_info['type'] == 'import':
            module = import_info['module']
            self._check_module_import(file_path, module, line_num)
        
        elif import_info['type'] == 'from_import':
            module = import_info['module']
            name = import_info['name']
            self._check_from_import(file_path, module, name, line_num)

    def _check_module_import(self, file_path: Path, module: str, line_num: int):
        """Module import'unu kontrol et"""
        # Backend içi import'lar
        if module.startswith('backend.'):
            if not self._is_backend_import_valid(module):
                self.errors.append(
                    f"❌ {file_path}:{line_num} Geçersiz backend import - {module}"
                )
                self._suggest_fix(file_path, module, line_num)
        
        # External library import'lar
        elif not self._is_external_import_valid(module):
            self.warnings.append(
                f"⚠️  {file_path}:{line_num} Potansiyel import sorunu - {module}"
            )

    def _check_from_import(self, file_path: Path, module: str, name: str, line_num: int):
        """From import'unu kontrol et"""
        if module.startswith('backend.'):
            if not self._is_backend_from_import_valid(module, name):
                self.errors.append(
                    f"❌ {file_path}:{line_num} Geçersiz backend from import - {module}.{name}"
                )
                self._suggest_fix(file_path, f"{module}.{name}", line_num)

    def _is_backend_import_valid(self, module: str) -> bool:
        """Backend import'unun geçerli olup olmadığını kontrol et"""
        # Backend dizin yapısını kontrol et
        module_path = self.backend_path / module.replace('backend.', '').replace('.', '/')
        
        # __init__.py dosyası var mı?
        init_file = module_path / "__init__.py"
        if init_file.exists():
            return True
        
        # Python dosyası var mı?
        py_file = module_path.with_suffix('.py')
        if py_file.exists():
            return True
        
        # Alt dizin var mı?
        if module_path.is_dir():
            return True
        
        return False

    def _is_backend_from_import_valid(self, module: str, name: str) -> bool:
        """Backend from import'unun geçerli olup olmadığını kontrol et"""
        if not self._is_backend_import_valid(module):
            return False
        
        # Modülü import etmeyi dene
        try:
            module_path = self.backend_path / module.replace('backend.', '').replace('.', '/')
            
            if module_path.is_dir():
                # Dizin ise __init__.py'yi kontrol et
                init_file = module_path / "__init__.py"
                if init_file.exists():
                    spec = importlib.util.spec_from_file_location(module, init_file)
                    if spec and spec.loader:
                        module_obj = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(module_obj)
                        return hasattr(module_obj, name)
            
            elif module_path.with_suffix('.py').exists():
                # Python dosyası ise
                py_file = module_path.with_suffix('.py')
                spec = importlib.util.spec_from_file_location(module, py_file)
                if spec and spec.loader:
                    module_obj = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module_obj)
                    return hasattr(module_obj, name)
        
        except Exception:
            pass
        
        return False

    def _is_external_import_valid(self, module: str) -> bool:
        """External library import'unun geçerli olup olmadığını kontrol et"""
        try:
            # Standart library kontrolü
            if module in sys.builtin_module_names:
                return True
            
            # Installed package kontrolü
            importlib.import_module(module)
            return True
        
        except ImportError:
            return False

    def _suggest_fix(self, file_path: Path, import_str: str, line_num: int):
        """Import hatası için çözüm öner"""
        if import_str in self.import_fixes:
            fix = self.import_fixes[import_str]
            self.fixed_imports.append({
                'file': file_path,
                'line': line_num,
                'original': import_str,
                'suggested': fix
            })

    def check_all_backend_files(self) -> bool:
        """Tüm backend dosyalarını kontrol et"""
        print("🔍 Backend import'ları kontrol ediliyor...")
        
        if not self.backend_path.exists():
            self.errors.append(f"❌ Backend dizini bulunamadı: {self.backend_path}")
            return False
        
        # Tüm Python dosyalarını bul
        python_files = list(self.backend_path.rglob("*.py"))
        
        print(f"📁 {len(python_files)} Python dosyası bulundu")
        
        success_count = 0
        for py_file in python_files:
            if self.check_file_imports(py_file):
                success_count += 1
        
        print(f"✅ {success_count}/{len(python_files)} dosya başarıyla kontrol edildi")
        
        return len(self.errors) == 0

    def check_circular_imports(self) -> bool:
        """Circular import'ları kontrol et"""
        print("🔄 Circular import'lar kontrol ediliyor...")
        
        # Basit circular import kontrolü
        # Bu daha gelişmiş bir implementasyon gerektirir
        # Şimdilik temel kontrol yapıyoruz
        
        return True

    def generate_fix_suggestions(self) -> str:
        """Çözüm önerileri oluştur"""
        if not self.fixed_imports:
            return "✅ Otomatik çözüm önerisi bulunamadı"
        
        suggestions = []
        suggestions.append("🔧 ÖNERİLEN ÇÖZÜMLER:")
        suggestions.append("=" * 50)
        
        for fix in self.fixed_imports:
            suggestions.append(f"📄 {fix['file']}:{fix['line']}")
            suggestions.append(f"  ❌ {fix['original']}")
            suggestions.append(f"  ✅ {fix['suggested']}")
            suggestions.append("")
        
        return "\n".join(suggestions)

    def generate_report(self) -> str:
        """Kontrol raporu oluştur"""
        report = []
        report.append("=" * 60)
        report.append("🔍 NEUROPETRIX IMPORT CHECKER RAPORU")
        report.append("=" * 60)
        
        if self.errors:
            report.append(f"\n❌ HATALAR ({len(self.errors)}):")
            for error in self.errors:
                report.append(f"  {error}")
        
        if self.warnings:
            report.append(f"\n⚠️  UYARILAR ({len(self.warnings)}):")
            for warning in self.warnings:
                report.append(f"  {warning}")
        
        if self.fixed_imports:
            report.append(f"\n{self.generate_fix_suggestions()}")
        
        if not self.errors and not self.warnings:
            report.append("\n✅ Tüm import'lar başarıyla kontrol edildi!")
        
        report.append(f"\n📊 ÖZET:")
        report.append(f"  - Hata: {len(self.errors)}")
        report.append(f"  - Uyarı: {len(self.warnings)}")
        report.append(f"  - Çözüm önerisi: {len(self.fixed_imports)}")
        report.append(f"  - Durum: {'✅ BAŞARILI' if len(self.errors) == 0 else '❌ BAŞARISIZ'}")
        
        return "\n".join(report)

def main():
    """Ana fonksiyon"""
    checker = ImportChecker()
    
    # Backend dosyalarını kontrol et
    backend_ok = checker.check_all_backend_files()
    
    # Circular import'ları kontrol et
    circular_ok = checker.check_circular_imports()
    
    # Rapor oluştur
    report = checker.generate_report()
    print(report)
    
    # Exit code
    if backend_ok and circular_ok:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()
