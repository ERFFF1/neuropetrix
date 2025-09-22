#!/usr/bin/env bash
set -euo pipefail

# === Girdi & dosya adları ===
ROOT="${1:-$PWD}"
TS="$(date +%Y%m%d_%H%M%S)"
REPORT="$ROOT/NP_SYSTEM_REPORT_${TS}.md"
BUNDLE="$ROOT/NP_SUPPORT_BUNDLE_${TS}.tar.gz"

say() { printf "%s\n" "$*" | tee -a "$REPORT" >/dev/null; }
hr()  { printf "\n---\n" | tee -a "$REPORT" >/dev/null; }

# === Kök doğrulama ===
if [ ! -d "$ROOT/backend" ] || [ ! -d "$ROOT/04_Uygulama_Gelistirme_ve_UIUX" ]; then
  echo "❌ Kök klasör bulunamadı: $ROOT"
  echo "   Script'i projenin kökünde çalıştırın ya da tam yolu argüman verin."
  exit 1
fi

: > "$REPORT"

# === Başlık ===
say "# NeuroPETrix Sistem Raporu"
say "_Oluşturma zamanı: $(date '+%F %T')_"
hr

# === Makine bilgisi ===
say "## Makine"
say "- Hostname: $(hostname)"
say "- macOS: $(sw_vers 2>/dev/null | tr '\t' ' ' | paste -sd'; ' -)"
say "- Kernel: $(uname -a)"
hr

# === İlgili klasörler (Desktop'taki varyantlar) ===
say "## Desktop üzerinde benzer klasörler"
find "$HOME/Desktop" -maxdepth 2 -type d -iname "neuropetrix*" -print | sort | sed 's/^/- /' | tee -a "$REPORT" >/dev/null
hr

# === Git durumu ===
say "## Git"
(
  cd "$ROOT"
  say "- Kök: $ROOT"
  say "- Branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'git değil')"
  say "- Remote: $(git remote -v 2>/dev/null | head -n1 || echo 'yok')"
  say "\n**git status**:"
  git status 2>/dev/null || echo "(git repo değil)"
  echo
  say "**Son 5 commit:**"
  git log --oneline -n 5 2>/dev/null || true
) >>"$REPORT"
hr

# === Proje yapısı (özet) ===
say "## Proje yapısı (ilk 2 seviye)"
( cd "$ROOT" && find . -maxdepth 2 -type d | sort ) | sed 's/^/    /' >>"$REPORT"
hr

# === Backend endpoint'leri ===
say "## Backend (FastAPI) endpoint'leri"
( cd "$ROOT/backend" && \
  grep -RIn --color=never -E '@app\.(get|post|put|delete|patch)\(' . 2>/dev/null \
  | sed -E 's/^\.\/(.+):([0-9]+):/@ \1:\2 -> /' ) >>"$REPORT" || true
hr

# === Frontend (Streamlit) sayfaları ===
say "## Frontend (Streamlit) sayfaları"
( cd "$ROOT/04_Uygulama_Gelistirme_ve_UIUX/Frontend_Kod" && \
  echo "- Ana uygulama: streamlit_app.py" && \
  echo "- Sayfalar:" && \
  find pages -type f -name "*.py" -print | sort | sed 's/^/  - /' && \
  echo && echo "**Başlık satırları (st.title)**:" && \
  grep -RIn --color=never 'st\.title\(' pages 2>/dev/null ) >>"$REPORT" || true
hr

# === Çalışan servisler / portlar ===
say "## Servisler & Portlar"
say "**Dinleyen portlar (8000/8501):**"
lsof -nPiTCP -sTCP:LISTEN | egrep -E ':8000|:8501' || true >>"$REPORT"
echo >>"$REPORT"
say "**Uygulama prosesleri (uvicorn/streamlit):**"
ps aux | egrep -E '(uvicorn|streamlit)' | grep -v grep >>"$REPORT" || true
hr

# === Sağlık kontrolleri ===
say "## Sağlık kontrolleri"
for URL in "http://127.0.0.1:8000/health" "http://127.0.0.1:8501"; do
  RES="$(curl -s -o /dev/null -w '%{http_code}' "$URL" || true)"
  say "- $URL -> HTTP $RES"
done
hr

# === Ortam dosyaları (içerik YAZILMAZ) ===
say "## Ortam dosyaları"
( cd "$ROOT" && ls -1 .env* 2>/dev/null | sed 's/^/- /' ) >>"$REPORT" || say "- (Bulunamadı)"
say "_(Güvenlik için içerikleri rapora eklenmedi.)_"
hr

# === Python ve Node ortamı ===
say "## Python & Node ortamı"
say "- Aktif VENV: ${VIRTUAL_ENV:-'(aktif değil)'}"
say "- which python: $(which python 2>/dev/null || true)"
say "- which python3: $(which python3 2>/dev/null || true)"
say "- Python sürümü: $(python3 --version 2>/dev/null || python --version 2>/dev/null || echo 'yok')"
say "- which uvicorn: $(which uvicorn 2>/dev/null || true)"
say "- which streamlit: $(which streamlit 2>/dev/null || true)"
say "- Node paketleri (ilk 25):"
( cd "$ROOT" && jq -r '.dependencies,.devDependencies|to_entries[]?| "- \(.key)@\(.value)"' package.json 2>/dev/null \
  | head -n 25 ) >>"$REPORT" || echo "  (package.json bulunamadı)" >>"$REPORT"
hr

# === Pip paketleri (özet) ===
say "## Pip paketleri (özet)"
( python3 -m pip freeze 2>/dev/null | sort | head -n 60 ) >>"$REPORT" || echo "(pip yok)" >>"$REPORT"
say "_(Tam liste için: \`python3 -m pip freeze > $ROOT/pip_freeze_${TS}.txt\`)_"
hr

# === Log özeti ===
say "## Log özeti (son 50 satır)"
BACK_LOG="$ROOT/backend/uvicorn.out"
FRONT_LOG="$ROOT/04_Uygulama_Gelistirme_ve_UIUX/Frontend_Kod/streamlit.out"
if [ -f "$BACK_LOG" ]; then
  say "### backend/uvicorn.out (son 50)"
  tail -n 50 "$BACK_LOG" >>"$REPORT"
else say "- backend/uvicorn.out yok"; fi
echo >>"$REPORT"
if [ -d "$FRONT_LOG" ]; then
  say "### streamlit.out (son 50)"
  tail -n 50 "$FRONT_LOG" >>"$REPORT"
else say "- Frontend log yok"; fi
hr

# === Masaüstündeki script kopyaları ===
say "## Masaüstündeki ilgili script'ler"
find "$HOME/Desktop" -type f -name "whisper_transkript.py" -o -name "gpt_log_db_panel_v4_5.py" -o -name "*pet_rapor*" \
  | sed 's/^/- /' | sort >>"$REPORT" || true
hr

# === Boyutlar ===
say "## Klasör boyutları"
( cd "$ROOT" && du -sh backend 04_Uygulama_Gelistirme_ve_UIUX node_modules 2>/dev/null ) >>"$REPORT" || true
hr

# === Destek demeti ===
FILES_TO_BUNDLE=()
[ -f "$BACK_LOG" ] && FILES_TO_BUNDLE+=("$BACK_LOG")
[ -f "$FRONT_LOG" ] && FILES_TO_BUNDLE+=("$FRONT_LOG")
FILES_TO_BUNDLE+=("$REPORT")
tar -czf "$BUNDLE" -C "$ROOT" $(printf "%q " "${FILES_TO_BUNDLE[@]##$ROOT/}") 2>/dev/null || true

echo "✅ Rapor: $REPORT"
[ -f "$BUNDLE" ] && echo "📦 Destek demeti: $BUNDLE"
