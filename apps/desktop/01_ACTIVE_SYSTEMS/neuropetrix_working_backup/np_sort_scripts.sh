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
  printf "→ %s  ==>  %s\n" "$src" "$dst"
  if [ "$DRY" = "1" ]; then
    mkdir -p "$(dirname "$dst")"; git mv -k "$src" "$dst" 2>/dev/null || mv "$src" "$dst"
  fi
}

# GUI / Tkinter
grep -EilR 'tkinter|Tk\(|ttk\.|mainloop\(' -- */*.py */*/*.py 2>/dev/null | while read -r f; do
  move "$f" "$LEGACY/GUI_Legacy/$(basename "$f")"
done

# Whisper / Ses
find "$ROOT" -type f -name "whisper_transkript*.py" -o -name "whisper_transcribe_auto.py" -o -name "ses_kayit*.py" -o -name "transkript_*.py" \
  | while read -r f; do move "$f" "$LEGACY/Whisper_Legacy/$(basename "$f")"; done

# DICOM / QC
find "$ROOT" -type f \( -name "qc_*.py" -o -name "safe_dicom_saver.py" -o -name "qc_dicom_reader.py" -o -name "qc_filter.py" -o -name "organize_patients.py" \) \
  | while read -r f; do move "$f" "$ROOT/backend/services/dicom/$(basename "$f")"; done

# Radiomics / Segmentasyon
find "$ROOT" -type f \( -name "pyradiomics-*.py" -o -name "run_radiomics.py" -o -name "ngtdm.py" -o -name "shape*.py" -o -name "segment*.py" -o -name "voxel.py" -o -name "resampleMask.py" \) \
  | while read -r f; do move "$f" "$ROOT/backend/services/radiomics/$(basename "$f")"; done

# Raporlama / SUV / Evidence
find "$ROOT" -type f \( -name "pet_rapor_*.py" -o -name "rapor_*.py" -o -name "pico_ureticisi*.py" -o -name "suvmax_*.py" -o -name "textural_*.py" -o -name "toplu_pet_rapor.py" -o -name "raporla_ve_olustur*.py" \) \
  | while read -r f; do move "$f" "$ROOT/backend/services/reporting/$(basename "$f")"; done

# Tools / Batch
find "$ROOT" -type f \( -name "yas_ekle_anon_batch.py" -o -name "topla_ve_tasi_neuro_verileri.py" -o -name "pdf_birlestirici_*.py" \) \
  | while read -r f; do move "$f" "$LEGACY/Tools/$(basename "$f")"; done

# Testler
find "$ROOT" -type f -name "test_*.py" -o -name "testParams.py" -o -name "testUtils.py" \
  | while read -r f; do move "$f" "$ROOT/tests/$(basename "$f")"; done

# Kopyalar / ' 2.py' / 'kopyası'
find "$ROOT" -type f \( -name "* 2.py" -o -name "*kopyası.py" \) \
  | while read -r f; do move "$f" "$LEGACY/Duplicates/$(basename "$f")"; done

echo
if [ "$DRY" = "1" ]; then
  echo "✅ Uygulandı."
else
  echo "ℹ️  Şu an sadece plan yazdırıldı. Uygulamak için: APPLY=1 ./np_sort_scripts.sh \"$ROOT\""
fi
