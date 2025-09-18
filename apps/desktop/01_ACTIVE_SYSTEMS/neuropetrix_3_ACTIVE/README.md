# NeuroPETRIX - AI-Powered Neurological Diagnosis Platform

## 🧠 Overview

NeuroPETRIX is a comprehensive AI-powered platform for neurological disease diagnosis using PET imaging analysis. The system combines advanced AI models with modern web technologies to provide accurate, fast, and reliable diagnostic support.

## ✨ Key Features

- **AI-Powered Analysis**: Gemini 2.5 Flash integration for intelligent image analysis
- **Real-time Processing**: WebSocket-based real-time updates and notifications
- **DICOM Support**: Full DICOM image upload, processing, and viewing
- **PDF Reports**: Automated report generation with secure sharing
- **Modern UI/UX**: React + TypeScript frontend with responsive design
- **Comprehensive API**: FastAPI backend with 14+ specialized routers
- **Monitoring**: Prometheus metrics and Grafana dashboards

## 🚀 Quick Start

### Prerequisites
- Python 3.13+
- Node.js 18+
- 8GB RAM
- 2GB disk space

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd neuropetrix
```

2. **Setup Backend**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

3. **Setup Frontend**
```bash
cd frontend
npm install
```

4. **Start the System**
```bash
# Terminal 1 - Backend
source .venv/bin/activate
cd backend
python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

5. **Access the Application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🏗️ Architecture

### Backend (FastAPI)
- **Core API**: FastAPI with 14 specialized routers
- **AI Integration**: Gemini AI Studio for image analysis
- **Database**: SQLite (development) / PostgreSQL (production)
- **Real-time**: WebSocket for live updates
- **Monitoring**: Prometheus metrics

### Frontend (React + TypeScript)
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for fast development
- **Styling**: Tailwind CSS
- **State Management**: React hooks
- **Real-time**: WebSocket integration

### AI & ML
- **Primary AI**: Gemini 2.5 Flash
- **Image Processing**: DICOM metadata extraction
- **Analysis**: Automated neurological pattern recognition
- **Reporting**: AI-generated diagnostic summaries

## 📊 System Status

### Current Version: v1.5.0
- ✅ Backend: 14 routers active
- ✅ Frontend: React + TypeScript
- ✅ AI Integration: Gemini AI Studio
- ✅ Real-time: WebSocket notifications
- ✅ PDF: Report generation
- ✅ Monitoring: Prometheus + Grafana

### Performance Metrics
- **API Response Time**: ~150ms
- **AI Analysis Time**: ~30s
- **PDF Generation**: ~5s
- **DICOM Upload**: ~10s

## 🎯 Demo

### Demo Data
- Sample cases with neurological conditions
- Mock users (doctors, radiologists)
- Pre-loaded DICOM images
- AI analysis examples

### Demo Script
See `docs/DEMO_SCRIPT_20250905.md` for a complete 15-minute demo flow.

## 📁 Project Structure

```
neuropetrix/
├── backend/                 # FastAPI backend
│   ├── routers/            # API endpoints
│   ├── services/           # Business logic
│   ├── models/             # Data models
│   └── main.py            # Application entry point
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── services/       # API services
│   │   └── types/          # TypeScript types
│   └── package.json
├── docs/                   # Documentation
│   ├── archive/           # Historical reports
│   ├── plans/             # Project plans
│   └── reports/           # System reports
├── monitoring/            # Prometheus & Grafana
└── docker-compose.yml     # Production deployment
```

## 🔧 Development

### Backend Development
```bash
source .venv/bin/activate
cd backend
python main.py
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Testing
```bash
# Backend tests
cd backend
python -m pytest

# Frontend tests
cd frontend
npm test
```

## 🚀 Production Deployment

### Docker Deployment
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Manual Deployment
```bash
./deploy.sh
```

## 📈 Monitoring

- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001
- **API Metrics**: http://localhost:8000/metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the documentation in `docs/`
- Review the API documentation at `/docs`

## 🎯 Roadmap

### Phase 1 (Current)
- ✅ Core system implementation
- ✅ AI integration
- ✅ Basic UI/UX
- ✅ Real-time features

### Phase 2 (Next)
- 🔄 Advanced AI models
- 🔄 Multi-user support
- 🔄 Advanced reporting
- 🔄 Mobile app

### Phase 3 (Future)
- 📋 Cloud deployment
- 📋 Enterprise features
- 📋 Integration APIs
- 📋 Advanced analytics

---

**NeuroPETRIX** - Revolutionizing neurological diagnosis through AI