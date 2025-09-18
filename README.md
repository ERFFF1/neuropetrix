# 🧠 NeuroPETRIX v3.0

**AI-Powered Medical Imaging Analysis Platform**

## 📋 Overview

NeuroPETRIX is a comprehensive AI-powered platform for medical imaging analysis, combining modern web technologies with advanced AI models to provide accurate, fast, and reliable diagnostic support.

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js Web   │    │   FastAPI API   │    │   Streamlit     │
│   (Vercel)      │◄──►│   (Render)      │◄──►│   Desktop       │
│   Port 3000     │    │   Port 8080     │    │   Port 8501     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   API Proxy     │    │   Legacy        │    │   Clinical      │
│   /api-proxy/*  │    │   /legacy/*     │    │   Decision      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- 8GB RAM
- 2GB disk space

### Installation

1. **Clone and setup**
```bash
git clone <repository-url>
cd neuropetrix
make install
```

2. **Start all services**
```bash
make dev
```

3. **Access the application**
- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8080/docs
- **Streamlit Desktop**: http://localhost:8501

## 📁 Project Structure

```
neuropetrix/
├── apps/
│   ├── api/                 # FastAPI backend
│   │   ├── app/
│   │   │   ├── main.py      # Main application
│   │   │   └── routers/     # API routes
│   │   └── requirements.txt
│   ├── web/                 # Next.js frontend
│   │   ├── app/
│   │   │   └── page.tsx     # Main page
│   │   ├── next.config.mjs  # Configuration
│   │   └── package.json
│   └── desktop/             # Streamlit legacy system
│       ├── 01_CORE_SYSTEM/
│       └── 01_ACTIVE_SYSTEMS/
├── packages/
│   ├── core/                # Shared components
│   └── legacy/              # Legacy code adapter
├── tools/                   # Development tools
├── docs/                    # Documentation
└── Makefile                 # Development commands
```

## 🔧 Development

### Available Commands

```bash
# Start all services
make dev

# Start individual services
make dev-api      # FastAPI on port 8080
make dev-web      # Next.js on port 3000
make dev-desktop  # Streamlit on port 8501

# Install dependencies
make install

# Run tests
make test

# Clean build artifacts
make clean
```

### API Endpoints

#### Health Checks
- `GET /healthz` - Main API health
- `GET /legacy/health` - Legacy system health
- `GET /v1/health` - V1 API health

#### Legacy System
- `GET /legacy/streamlit-status` - Streamlit status
- `POST /legacy/clinical-decision` - Clinical decision support

#### V1 API
- `GET /v1/features` - Available features
- `POST /v1/analyze` - AI analysis

## 🌐 Deployment

### Vercel (Frontend)
- **Root Directory**: `apps/web`
- **Build Command**: `npm run build`
- **Environment Variables**:
  - `API_BASE=https://neuropetrix.onrender.com`
  - `NEXT_PUBLIC_API_BASE=/api-proxy`

### Render (Backend)
- **Root Directory**: `apps/api`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### GitHub Actions
- **CI/CD**: Automatic deployment on push to main
- **Health Monitoring**: Every 15 minutes
- **Testing**: Automated tests on pull requests

## 📊 System Status

### Current Version: v3.0.0
- ✅ **API**: FastAPI with legacy and v1 routers
- ✅ **Web**: Next.js with API proxy
- ✅ **Desktop**: Streamlit legacy system
- ✅ **Monitoring**: Health checks and status reporting
- ✅ **Deployment**: GitHub + Vercel + Render integration

### Features
- **AI Integration**: Gemini, Whisper, MONAI
- **DICOM Support**: Full DICOM processing
- **Report Generation**: Automated report creation
- **Real-time**: WebSocket support
- **Legacy Support**: Backward compatibility

## 🔍 Monitoring

### Health Checks
```bash
# Local testing
curl http://localhost:8080/healthz
curl http://localhost:3000/api-proxy/healthz
curl http://localhost:8080/legacy/health

# Production testing
curl https://neuropetrix.onrender.com/healthz
curl https://neuropetrix.vercel.app/api-proxy/healthz
```

### Audit Script
```bash
./tools/audit_neuropetrix.sh
```

## 🛠️ Troubleshooting

### Common Issues

1. **Port conflicts**
   - API (8080): `lsof -ti:8080 | xargs kill -9`
   - Web (3000): `lsof -ti:3000 | xargs kill -9`
   - Streamlit (8501): `lsof -ti:8501 | xargs kill -9`

2. **API proxy not working**
   - Check `next.config.mjs` rewrite rules
   - Verify `API_BASE` environment variable
   - Clear Vercel build cache

3. **Legacy system not accessible**
   - Ensure Streamlit is running on port 8501
   - Check `/legacy/streamlit-status` endpoint

## 📈 Performance

- **API Response Time**: ~150ms
- **Web Load Time**: ~2s
- **Streamlit Startup**: ~5s
- **Memory Usage**: ~500MB total

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the documentation in `docs/`
- Review the API documentation at `/docs`

---

**NeuroPETRIX** - Revolutionizing medical imaging analysis through AI
