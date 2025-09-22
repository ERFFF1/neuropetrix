# 🚀 NeuroPETRIX Deployment Guide

## 📋 Overview

Bu rehber, tamamlanan NeuroPETRIX sisteminizi GitHub, Vercel ve Render platformlarında nasıl deploy edeceğinizi açıklar.

## 🏗️ Sistem Mimarisi

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Vercel        │    │   Render        │    │   GitHub        │
│   (Frontend)    │◄──►│   (Backend)     │◄──►│   (Repository)  │
│   React App     │    │   FastAPI       │    │   Source Code   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Proxy     │    │   Health Check  │    │   CI/CD         │
│   /api-proxy/*  │    │   /health       │    │   GitHub Actions│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🎯 Deployment Adımları

### 1. GitHub Repository Hazırlığı

```bash
# Repository'yi GitHub'a push edin
git add .
git commit -m "feat: Add GitHub + Vercel + Render integration"
git push origin main
```

### 2. Render Backend Deployment

1. **Render.com'a gidin** ve hesap oluşturun
2. **"New Web Service"** seçin
3. **GitHub repository'nizi bağlayın**
4. **Ayarlar:**
   - **Name**: `neuropetrix-api`
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Python Version**: `3.11`

5. **Environment Variables:**
   ```
   APP_ENV=production
   DATABASE_URL=sqlite:///neuropetrix.db
   JWT_SECRET=your_secure_jwt_secret
   CORS_ORIGINS=https://neuropetrix.vercel.app
   GEMINI_API_KEY=your_gemini_api_key
   ```

6. **Deploy** butonuna tıklayın

### 3. Vercel Frontend Deployment

1. **Vercel.com'a gidin** ve hesap oluşturun
2. **"New Project"** seçin
3. **GitHub repository'nizi bağlayın**
4. **Ayarlar:**
   - **Framework Preset**: `Vite`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

5. **Environment Variables:**
   ```
   VITE_API_BASE_URL=https://neuropetrix.onrender.com
   VITE_API_PROXY_URL=/api-proxy
   VITE_APP_NAME=NeuroPETRIX
   VITE_APP_VERSION=1.5.0
   ```

6. **Deploy** butonuna tıklayın

### 4. GitHub Actions CI/CD

GitHub Actions otomatik olarak çalışacak:

- **Test**: Her push'ta testler çalışır
- **Deploy**: Main branch'e push'ta otomatik deploy
- **Monitor**: Her 15 dakikada health check

## 🔧 Konfigürasyon Dosyaları

### GitHub Actions (`.github/workflows/deploy.yml`)
- ✅ Test aşaması (Python + Node.js)
- ✅ Backend deployment (Render)
- ✅ Frontend deployment (Vercel)
- ✅ Health check ve monitoring

### Vercel Konfigürasyonu (`vercel.json`)
- ✅ API proxy routing
- ✅ Environment variables
- ✅ Security headers
- ✅ Redirects

### Render Konfigürasyonu (`render.yaml`)
- ✅ Python 3.11 web service
- ✅ Health check endpoint
- ✅ Auto-deploy from main branch
- ✅ Environment variables

## 📊 Monitoring ve Health Checks

### Otomatik Monitoring
- **GitHub Actions**: Her 15 dakikada health check
- **Render**: Built-in health monitoring
- **Vercel**: Automatic uptime monitoring

### Health Check Endpoints
- **Backend**: `https://neuropetrix.onrender.com/health`
- **Frontend**: `https://neuropetrix.vercel.app`
- **API Proxy**: `https://neuropetrix.vercel.app/api-proxy/health`

## 🚀 Deployment Sonrası

### URL'ler
- **Frontend**: `https://neuropetrix.vercel.app`
- **Backend API**: `https://neuropetrix.onrender.com`
- **API Docs**: `https://neuropetrix.onrender.com/docs`

### Test Etme
```bash
# Backend health check
curl https://neuropetrix.onrender.com/health

# Frontend test
curl https://neuropetrix.vercel.app

# API proxy test
curl https://neuropetrix.vercel.app/api-proxy/health
```

## 🔄 Güncelleme Süreci

1. **Kod değişikliği yapın**
2. **GitHub'a push edin**:
   ```bash
   git add .
   git commit -m "feat: Update feature"
   git push origin main
   ```
3. **Otomatik deploy** başlar
4. **Health check** çalışır
5. **Monitoring** güncellenir

## 🛠️ Troubleshooting

### Backend Sorunları
- Render logs kontrol edin
- Environment variables kontrol edin
- Health endpoint test edin

### Frontend Sorunları
- Vercel logs kontrol edin
- Build logs kontrol edin
- Environment variables kontrol edin

### API Proxy Sorunları
- CORS ayarları kontrol edin
- Vercel.json routing kontrol edin
- Backend URL kontrol edin

## 📈 Performance Optimization

### Backend (Render)
- **Plan**: Starter → Standard (daha fazla RAM)
- **Workers**: 2-4 worker process
- **Caching**: Redis cache ekleyin

### Frontend (Vercel)
- **CDN**: Otomatik global CDN
- **Caching**: Static asset caching
- **Compression**: Gzip compression

## 🔐 Security

### Environment Variables
- **JWT_SECRET**: Güçlü secret key
- **CORS_ORIGINS**: Sadece gerekli domainler
- **API_KEYS**: Güvenli API key yönetimi

### Headers
- **Security headers**: XSS, CSRF koruması
- **CORS**: Sadece gerekli originler
- **HTTPS**: Otomatik SSL sertifikası

## 📞 Support

### Logs ve Monitoring
- **GitHub Actions**: Workflow logs
- **Render**: Application logs
- **Vercel**: Function logs

### Health Monitoring
- **GitHub Actions**: Otomatik health check
- **Render**: Built-in monitoring
- **Vercel**: Uptime monitoring

---

**🎉 Deployment tamamlandı!** Sisteminiz artık production'da çalışıyor.

**📱 Erişim URL'leri:**
- Frontend: https://neuropetrix.vercel.app
- Backend: https://neuropetrix.onrender.com
- API Docs: https://neuropetrix.onrender.com/docs
