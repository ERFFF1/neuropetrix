#!/usr/bin/env bash
set -e
PY=03_Teknik_Mimari_ve_Yapay_Zeka_Modelleri/Veri_Isleme_Pipeline/utils/validate_json.py
for f in 08_Scripts_ve_Arsiv/Data/dummy_cases/*.json; do
  python "$PY" "$f"
done
echo "Tüm dummy vakalar şemaya uyumlu görünüyor."
