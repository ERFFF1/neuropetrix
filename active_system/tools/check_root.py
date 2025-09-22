#!/usr/bin/env python3
"""
NeuroPETRIX Root Check Tool
Sadece 'neuropetrix (3)' kökünde çalışmayı garanti eder
"""

import os
import sys
import pathlib

def check_root():
    """Workspace root'u kontrol et"""
    # Bu dosyadan 2 seviye yukarı çık (.np_root dosyasını bul)
    current_file = pathlib.Path(__file__).resolve()
    root_file = current_file.parents[1] / ".np_root"
    
    if not root_file.exists():
        print("⛔ Sadece 'neuropetrix (3)' kökünde çalış. .np_root bulunamadı.")
        print(f"📁 Mevcut dizin: {os.getcwd()}")
        print(f"🔍 Aranan dosya: {root_file}")
        sys.exit(1)
    
    # Root dosyasını oku
    with open(root_file, 'r') as f:
        expected_root = f.read().strip()
    
    current_dir = os.getcwd()
    if expected_root not in current_dir:
        print(f"⛔ Yanlış workspace! Beklenen: {expected_root}")
        print(f"📁 Mevcut: {current_dir}")
        sys.exit(1)
    
    print("✅ Workspace root:", root_file.parent)
    print(f"📁 Çalışma dizini: {current_dir}")
    return True

if __name__ == "__main__":
    check_root()


