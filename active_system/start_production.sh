#!/bin/bash

echo "🚀 NeuroPETRIX Production Başlatılıyor..."

# Process'leri temizle
pkill -f uvicorn
pkill -f "npm run dev"
sleep 2

# Backend'i başlat
echo "📡 Backend başlatılıyor..."
cd /Users/serefkarabulut/Desktop/NeuroPETRIX_MASTER_ORGANIZED/01_ACTIVE_SYSTEMS/neuropetrix_3_ACTIVE
uvicorn backend.main_working:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Frontend'i başlat
echo "🎨 Frontend başlatılıyor..."
cd frontend
npm run dev &
FRONTEND_PID=$!

# Test et
sleep 5
echo "🧪 Sistem test ediliyor..."
curl -s http://localhost:8000/health > /dev/null && echo "✅ Backend çalışıyor" || echo "❌ Backend hatası"
curl -s http://localhost:5173 > /dev/null && echo "✅ Frontend çalışıyor" || echo "❌ Frontend hatası"

echo "🎉 NeuroPETRIX Production Hazır!"
echo "📡 Backend: http://localhost:8000"
echo "🎨 Frontend: http://localhost:5173"
echo "📚 API Docs: http://localhost:8000/docs"

# Process'leri takip et
wait $BACKEND_PID $FRONTEND_PID
