#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
API_DIR="$ROOT/backend"
FRONT_DIR="$ROOT/04_Uygulama_Gelistirme_ve_UIUX/Frontend_Kod"
VENV="$ROOT/.venv"   # tek venv kullan

# Venv'i aktifleştir
[ -d "$VENV" ] || python3 -m venv "$VENV"
source "$VENV/bin/activate"

start() {
  echo "🚀 NeuroPETrix sistemi başlatılıyor..."
  
  # venv
  pip install --upgrade pip
  pip install -r "$API_DIR/requirements.txt" streamlit || true

  # arka uç (nohup + pid)
  pkill -f "uvicorn.*main:app" 2>/dev/null || true
  cd "$API_DIR"
  nohup "$VENV/bin/python" -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload > "$API_DIR/uvicorn.out" 2>&1 &
  echo $! > "$API_DIR/uvicorn.pid"

  # streamlit
  cd "$FRONT_DIR"
  pkill -f "streamlit run streamlit_app.py" 2>/dev/null || true
  nohup "$VENV/bin/streamlit" run streamlit_app.py --server.port 8501 --server.address 127.0.0.1 > "$FRONT_DIR/streamlit.out" 2>&1 &
  echo $! > "$FRONT_DIR/streamlit.pid"

  echo "✅ Backend: http://127.0.0.1:8000/health"
  echo "✅ Streamlit: http://127.0.0.1:8501"
  echo "✅ Sistem başlatıldı!"
}

start_backend() {
  echo "🔧 Backend başlatılıyor..."
  
  # arka uç (nohup + pid)
  pkill -f "uvicorn.*main:app" 2>/dev/null || true
  cd "$API_DIR"
  nohup "$VENV/bin/python" -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload > "$API_DIR/uvicorn.out" 2>&1 &
  echo $! > "$API_DIR/uvicorn.pid"
  
  echo "✅ Backend başlatıldı: http://127.0.0.1:8000/health"
}

start_frontend() {
  echo "📱 Frontend başlatılıyor..."
  
  # streamlit
  cd "$FRONT_DIR"
  pkill -f "streamlit run streamlit_app.py" 2>/dev/null || true
  nohup "$VENV/bin/streamlit" run streamlit_app.py --server.port 8501 --server.address 127.0.0.1 > "$FRONT_DIR/streamlit.out" 2>&1 &
  echo $! > "$FRONT_DIR/streamlit.pid"
  
  echo "✅ Frontend başlatıldı: http://127.0.0.1:8501"
}

stop() {
  echo "🛑 Sistem durduruluyor..."
  for p in "$API_DIR/uvicorn.pid" "$FRONT_DIR/streamlit.pid"; do
    [ -f "$p" ] && kill "$(cat "$p")" 2>/dev/null || true
    rm -f "$p"
  done
  pkill -f "uvicorn.*main:app" 2>/dev/null || true
  pkill -f "streamlit run streamlit_app.py" 2>/dev/null || true
  echo "🛑 Sistem durduruldu"
}

status() {
  echo "📊 Sistem durumu kontrol ediliyor..."
  
  # Backend kontrol
  if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
    echo "✅ Backend çalışıyor (http://127.0.0.1:8000)"
  else
    echo "❌ Backend çalışmıyor"
  fi
  
  # Frontend kontrol
  if curl -s -I http://127.0.0.1:8501 > /dev/null 2>&1; then
    echo "✅ Frontend çalışıyor (http://127.0.0.1:8501)"
  else
    echo "❌ Frontend çalışmıyor"
  fi
  
  # PID dosyaları
  if [ -f "$API_DIR/uvicorn.pid" ]; then
    echo "📋 Backend PID: $(cat "$API_DIR/uvicorn.pid")"
  fi
  if [ -f "$FRONT_DIR/streamlit.pid" ]; then
    echo "📋 Frontend PID: $(cat "$FRONT_DIR/streamlit.pid")"
  fi
}

logs() {
  echo "📋 Log dosyaları:"
  
  if [ -f "$API_DIR/uvicorn.out" ]; then
    echo "📄 Backend Log (son 10 satır):"
    tail -10 "$API_DIR/uvicorn.out"
  else
    echo "⚠️  Backend log dosyası bulunamadı"
  fi
  
  echo ""
  
  if [ -f "$FRONT_DIR/streamlit.out" ]; then
    echo "📄 Frontend Log (son 10 satır):"
    tail -10 "$FRONT_DIR/streamlit.out"
  else
    echo "⚠️  Frontend log dosyası bulunamadı"
  fi
}

show_menu() {
  echo "🧠 NeuroPETrix Sistemi"
  echo "======================"
  echo ""
  echo "🎯 Seçenekler:"
  echo "1) Sistemi başlat (Backend + Frontend)"
  echo "2) Sadece Backend başlat"
  echo "3) Sadece Frontend başlat"
  echo "4) Sistem durumunu kontrol et"
  echo "5) Sistemi durdur"
  echo "6) Log dosyalarını göster"
  echo "7) Çıkış"
  echo ""
  read -p "Seçiminiz (1-7): " choice
  
  case $choice in
    1) start ;;
    2) start_backend ;;
    3) start_frontend ;;
    4) status ;;
    5) stop ;;
    6) logs ;;
    7) echo "👋 Görüşürüz!"; exit 0 ;;
    *) echo "❌ Geçersiz seçim" ;;
  esac
}

# ==== CLI Modu ====
if [[ $# -gt 0 ]]; then
  case "$1" in
    start)     start_backend; start_frontend; exit 0;;
    stop)      stop; exit 0;;
    status)    status; exit 0;;
    logs)      logs; exit 0;;
    backend)   start_backend; exit 0;;
    frontend)  start_frontend; exit 0;;
    restart)   stop; start_backend; start_frontend; exit 0;;
    *)
      echo "Kullanım: $0 [start|stop|status|logs|backend|frontend|restart]"
      exit 1;;
  esac
fi
# ==== /CLI Modu ====

# Eski interaktif menü (CLI parametre yoksa)
show_menu
