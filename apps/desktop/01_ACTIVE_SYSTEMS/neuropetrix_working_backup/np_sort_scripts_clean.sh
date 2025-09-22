#!/usr/bin/env bash
set -euo pipefail
ROOT="${1:-$PWD}"
LEGACY="$ROOT/08_Scripts_ve_Arsiv"
DRY="${APPLY:-0}"

mkdir -p "$LEGACY/GUI_Legacy" "$LEGACY/Whisper_Legacy" "$LEGACY/Tools" "$LEGACY/Duplicates"
mkdir -p "$ROOT/backend/services/reporting" "$ROOT/backend/services/dicom" "$ROOT/backend/services/radiomics" "$ROOT/backend/utils/dicom"

move() {
  src="$1"; dst="$2"
  [ -e "$src" ] || return 0
  # Sadece proje kökündeki dosyaları taşı (venv içindekileri değil)
  if [[ "$src" == "$ROOT"* ]] && [[ "$src" != *".venv"* ]] && [[ "$src" != *"node_modules"* ]]; then
    printf "→ %s  ==>  %s\n" "$src" "$dst"
    if [ "$DRY" = "1" ]; then
      mkdir -p "$(dirname "$dst")"; git mv -k "$src" "$dst" 2>/dev/null || mv "$src" "$dst"
    fi
  fi
}

echo "�� Sadece proje dosyaları taranıyor (venv/node_modules hariç)..."

# GUI / Tkinter (sadece proje dosyaları)
find "$ROOT" -maxdepth 3 -type f -name "*.py" -exec grep -l "tkinter\|Tk(\|ttk\.\|mainloop(" {} \; 2>/dev/null | while read -r f; do
  if [[ "$f" != *".venv"* ]] && [[ "$f" != *"node_modules"* ]]; then
    move "$f" "$LEGACY/GUI_Legacy/$(basename "$f")"
  fi
done

# Whisper / Ses (sadece proje dosyaları)
find "$ROOT" -maxdepth 3 -type f \( -name "whisper_transkript*.py" -o -name "whisper_transcribe_auto.py" -o -name "ses_kayit*.py" -o -name "transkript_*.py" \) \
  | while read -r f; do 
    if [[ "$f" != *".venv"* ]] && [[ "$f" != *"node_modules"* ]]; then
      move "$f" "$LEGACY/Whisper_Legacy/$(basename "$f")"
    fi
  done

# DICOM / QC (sadece proje dosyaları)
find "$ROOT" -maxdepth 3 -type f \( -name "qc_*.py" -o -name "safe_dicom_saver.py" -o -name "qc_dicom_reader.py" -o -name "qc_filter.py" -o -name "organize_patients.py" \) \
  | while read -r f; do 
    if [[ "$f" != *".venv"* ]] && [[ "$f" != *"node_modules"* ]]; then
      move "$f" "$ROOT/backend/services/dicom/$(basename "$f")"
    fi
  done

# Radiomics / Segmentasyon (sadece proje dosyaları)
find "$ROOT" -maxdepth 3 -type f \( -name "pyradiomics-*.py" -o -name "run_radiomics.py" -o -name "ngtdm.py" -o -name "shape*.py" -o -name "segment*.py" -o -name "voxel.py" -o -name "resampleMask.py" \) \
  | while read -r f; do 
    if [[ "$f" != *".venv"* ]] && [[ "$f" != *"node_modules"* ]]; then
      move "$f" "$ROOT/backend/services/radiomics/$(basename "$f")"
    fi
  done

# Raporlama / SUV / Evidence (sadece proje dosyaları)
find "$ROOT" -maxdepth 3 -type f \( -name "pet_rapor_*.py" -o -name "rapor_*.py" -o -name "pico_ureticisi*.py" -o -name "suvmax_*.py" -o -name "textural_*.py" -o -name "toplu_pet_rapor.py" -o -name "raporla_ve_olustur*.py" \) \
  | while read -r f; do 
    if [[ "$f" != *".venv"* ]] && [[ "$f" != *"node_modules"* ]]; then
      move "$f" "$ROOT/backend/services/reporting/$(basename "$f")"
    fi
  done

# Tools / Batch (sadece proje dosyaları)
find "$ROOT" -maxdepth 3 -type f \( -name "yas_ekle_anon_batch.py" -o -name "topla_ve_tasi_neuro_verileri.py" -o -name "pdf_birlestirici_*.py" \) \
  | while read -r f; do 
    if [[ "$f" != *".venv"* ]] && [[ "$f" != *"node_modules"* ]]; then
      move "$f" "$LEGACY/Tools/$(basename "$f")"
    fi
  done

# Testler (sadece proje dosyaları)
find "$ROOT" -maxdepth 3 -type f -name "test_*.py" -o -name "testParams.py" -o -name "testUtils.py" \
  | while read -r f; do 
    if [[ "$f" != *".venv"* ]] && [[ "$f" != *"node_modules"* ]]; then
      move "$f" "$ROOT/tests/$(basename "$f")"
    fi
  done

# Kopyalar / ' 2.py' / 'kopyası' (sadece proje dosyaları)
find "$ROOT" -maxdepth 3 -type f \( -name "* 2.py" -o -name "*kopyası.py" \) \
  | while read -r f; do 
    if [[ "$f" != *".venv"* ]] && [[ "$f" != *"node_modules"* ]]; then
      move "$f" "$LEGACY/Duplicates/$(basename "$f")"
    fi
  done

echo
if [ "$DRY" = "1" ]; then
  echo "✅ Uygulandı."
else
  echo "ℹ️  Şu an sadece plan yazdırıldı. Uygulamak için: APPLY=1 ./np_sort_scripts_clean.sh \"$ROOT\""
fi
