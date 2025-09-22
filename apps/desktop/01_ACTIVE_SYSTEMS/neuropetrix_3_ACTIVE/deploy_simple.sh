#!/bin/bash

echo "🚀 NeuroPETRIX Basit Deployment"
echo "================================"

# Backend'i başlat
echo "📡 Backend başlatılıyor..."
cd backend
source ../.venv/bin/activate
python main.py &
BACKEND_PID=$!

# 5 saniye bekle
sleep 5

# Frontend'i başlat
echo "🌐 Frontend başlatılıyor..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "✅ Sistem başlatıldı!"
echo "📡 Backend: http://localhost:8000"
echo "🌐 Frontend: http://localhost:3000"
echo "📊 API Docs: http://localhost:8000/docs"

echo ""
echo "🛑 Durdurmak için:"
echo "kill $BACKEND_PID $FRONTEND_PID"

# Process'leri bekle
wait
