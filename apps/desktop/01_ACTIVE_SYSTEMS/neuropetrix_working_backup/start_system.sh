#!/bin/bash

# 🧠 NeuroPETrix - Sistem Başlatma Script'i
# Bu script ile sistemi tek komutla başlatabilirsiniz

echo "🧠 NeuroPETrix Sistemi Başlatılıyor..."
echo "=================================="

# Renkli çıktı için
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Mevcut dizini kontrol et
if [[ ! -f "backend/main.py" ]]; then
    echo -e "${RED}❌ Hata: Bu script backend klasörü ile aynı dizinde çalıştırılmalıdır${NC}"
    echo "Kullanım: ./start_system.sh"
    exit 1
fi

# Port kontrolü
check_port() {
    local port=$1
    local service=$2
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo -e "${YELLOW}⚠️  Port $port meşgul, $service zaten çalışıyor olabilir${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Port $port boş${NC}"
        return 0
    fi
}

# Backend başlat
start_backend() {
    echo -e "${BLUE}🔧 Backend başlatılıyor...${NC}"
    
    if check_port 8000 "Backend"; then
        cd backend
        nohup python -m uvicorn main:app --host 127.0.0.1 --port 8000 > uvicorn.out 2>&1 &
        BACKEND_PID=$!
        echo $BACKEND_PID > uvicorn.pid
        echo -e "${GREEN}✅ Backend başlatıldı (PID: $BACKEND_PID)${NC}"
        cd ..
    else
        echo -e "${YELLOW}⚠️  Backend zaten çalışıyor${NC}"
    fi
}

# Frontend başlat
start_frontend() {
    echo -e "${BLUE}📱 Frontend başlatılıyor...${NC}"
    
    if check_port 8501 "Frontend"; then
        cd "04_Uygulama_Gelistirme_ve_UIUX/Frontend_Kod"
        nohup streamlit run streamlit_app.py --server.port 8501 --server.address 127.0.0.1 > streamlit.out 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > streamlit.pid
        echo -e "${GREEN}✅ Frontend başlatıldı (PID: $FRONTEND_PID)${NC}"
        cd ../..
    else
        echo -e "${YELLOW}⚠️  Frontend zaten çalışıyor${NC}"
    fi
}

# Sistem durumunu kontrol et
check_system() {
    echo -e "${BLUE}🔍 Sistem durumu kontrol ediliyor...${NC}"
    
    # Backend kontrol
    if curl -s http://127.0.0.1:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend çalışıyor (http://127.0.0.1:8000)${NC}"
    else
        echo -e "${RED}❌ Backend çalışmıyor${NC}"
    fi
    
    # Frontend kontrol
    if curl -s -I http://127.0.0.1:8501 > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Frontend çalışıyor (http://127.0.0.1:8501)${NC}"
    else
        echo -e "${RED}❌ Frontend çalışmıyor${NC}"
    fi
}

# Ana menü
show_menu() {
    echo ""
    echo -e "${BLUE}🎯 Seçenekler:${NC}"
    echo "1) Sistemi başlat (Backend + Frontend)"
    echo "2) Sadece Backend başlat"
    echo "3) Sadece Frontend başlat"
    echo "4) Sistem durumunu kontrol et"
    echo "5) Sistemi durdur"
    echo "6) Log dosyalarını göster"
    echo "7) Çıkış"
    echo ""
    read -p "Seçiminiz (1-7): " choice
}

# Sistemi durdur
stop_system() {
    echo -e "${YELLOW}🛑 Sistem durduruluyor...${NC}"
    
    # PID dosyalarından process'leri durdur
    if [[ -f "backend/uvicorn.pid" ]]; then
        BACKEND_PID=$(cat backend/uvicorn.pid)
        kill $BACKEND_PID 2>/dev/null && echo -e "${GREEN}✅ Backend durduruldu${NC}" || echo -e "${YELLOW}⚠️  Backend zaten durmuş${NC}"
        rm backend/uvicorn.pid 2>/dev/null
    fi
    
    if [[ -f "04_Uygulama_Gelistirme_ve_UIUX/Frontend_Kod/streamlit.pid" ]]; then
        FRONTEND_PID=$(cat "04_Uygulama_Gelistirme_ve_UIUX/Frontend_Kod/streamlit.pid")
        kill $FRONTEND_PID 2>/dev/null && echo -e "${GREEN}✅ Frontend durduruldu${NC}" || echo -e "${YELLOW}⚠️  Frontend zaten durmuş${NC}"
        rm "04_Uygulama_Gelistirme_ve_UIUX/Frontend_Kod/streamlit.pid" 2>/dev/null
    fi
    
    # Port'larda kalan process'leri temizle
    pkill -f "uvicorn.*main:app" 2>/dev/null || true
    pkill -f "streamlit.*streamlit_app.py" 2>/dev/null || true
    
    echo -e "${GREEN}✅ Sistem durduruldu${NC}"
}

# Log dosyalarını göster
show_logs() {
    echo -e "${BLUE}📋 Log dosyaları:${NC}"
    
    if [[ -f "backend/uvicorn.out" ]]; then
        echo -e "${GREEN}📄 Backend Log (son 10 satır):${NC}"
        tail -10 backend/uvicorn.out
    else
        echo -e "${YELLOW}⚠️  Backend log dosyası bulunamadı${NC}"
    fi
    
    echo ""
    
    if [[ -f "04_Uygulama_Gelistirme_ve_UIUX/Frontend_Kod/streamlit.out" ]]; then
        echo -e "${GREEN}📄 Frontend Log (son 10 satır):${NC}"
        tail -10 "04_Uygulama_Gelistirme_ve_UIUX/Frontend_Kod/streamlit.out"
    else
        echo -e "${YELLOW}⚠️  Frontend log dosyası bulunamadı${NC}"
    fi
}

# Ana döngü
while true; do
    show_menu
    
    case $choice in
        1)
            echo -e "${BLUE}🚀 Sistem başlatılıyor...${NC}"
            start_backend
            sleep 3
            start_frontend
            sleep 3
            check_system
            ;;
        2)
            start_backend
            ;;
        3)
            start_frontend
            ;;
        4)
            check_system
            ;;
        5)
            stop_system
            ;;
        6)
            show_logs
            ;;
        7)
            echo -e "${GREEN}👋 Görüşürüz!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Geçersiz seçim${NC}"
            ;;
    esac
    
    echo ""
    read -p "Devam etmek için Enter'a basın..."
done
