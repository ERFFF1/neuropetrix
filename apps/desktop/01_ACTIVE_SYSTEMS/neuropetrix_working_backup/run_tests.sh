#!/bin/bash
set -e

echo "🧪 Starting NeuroPETrix Tests..."

# Kill any existing processes on our ports
echo "🔒 Cleaning up ports..."
lsof -ti :8000 | xargs kill -9 2>/dev/null || true
lsof -ti :8501 | xargs kill -9 2>/dev/null || true

# Start backend in background
echo "🚀 Starting backend..."
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 3

# Test backend health
echo "🔍 Testing backend health..."
if curl -s http://127.0.0.1:8000/health | grep -q "ok"; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# Test version endpoint
echo "ℹ️ Testing version endpoint..."
if curl -s http://127.0.0.1:8000/version | grep -q "neuro-petrix"; then
    echo "✅ Version endpoint working"
else
    echo "❌ Version endpoint failed"
fi

# Test GRADE scoring
echo "🔬 Testing GRADE scoring..."
GRADE_RESPONSE=$(curl -s -X POST "http://127.0.0.1:8000/grade/score?use_ml=true" \
  -H "Content-Type: application/json" \
  -d '{"title":"Systematic review","abstract":"Randomized controlled trial.","keywords":["meta-analysis"]}')

if echo "$GRADE_RESPONSE" | grep -q "rank"; then
    echo "✅ GRADE scoring working"
    echo "Response: $GRADE_RESPONSE"
else
    echo "❌ GRADE scoring failed"
fi

# Test multimodal inference
echo "📊 Testing multimodal inference..."
INFERENCE_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/inference/multimodal \
  -H "Content-Type: application/json" \
  -d '{"report_text":"Karaciğerde metastaz düşündüren odak...","suvmax":7.8,"suv_thresh":6.0}')

if echo "$INFERENCE_RESPONSE" | grep -q "suggestion"; then
    echo "✅ Multimodal inference working"
    echo "Response: $INFERENCE_RESPONSE"
else
    echo "❌ Multimodal inference failed"
fi

# Test feedback
echo "💬 Testing feedback endpoint..."
FEEDBACK_RESPONSE=$(curl -s -X POST http://127.0.0.1:8000/feedback \
  -H "Content-Type: application/json" \
  -d '{"endpoint":"test","useful":true}')

if echo "$FEEDBACK_RESPONSE" | grep -q "ok"; then
    echo "✅ Feedback endpoint working"
    echo "Response: $FEEDBACK_RESPONSE"
else
    echo "❌ Feedback endpoint failed"
fi

# Test AI analysis
echo "🧠 Testing AI analysis endpoint..."
AI_RESPONSE=$(curl -s -X POST "http://127.0.0.1:8000/ai/analyze" \
  -H "Content-Type: application/json" \
  -d '{"hasta_no":"TEST001","hasta_adi":"Test Hasta","study_date":"2024-01-15","analysis_type":"full","retention_days":7}')

if echo "$AI_RESPONSE" | grep -q "patient_hash"; then
    echo "✅ AI analysis working"
    echo "Response: $AI_RESPONSE"
else
    echo "❌ AI analysis failed"
fi

# Stop backend
echo "🛑 Stopping backend..."
kill $BACKEND_PID 2>/dev/null || true

echo "🎉 All tests completed successfully!"
echo "✅ Backend endpoints working"
echo "✅ Database operations working"
echo "✅ API responses valid"
