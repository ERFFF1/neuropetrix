<div align="center">
<img width="1200" height="475" alt="GHBanner" src="https://github.com/user-attachments/assets/0aa67016-6eaf-458a-adb2-6e31a0763ed6" />
</div>

# NeuroPETrix - AI-Powered PET-CT Analysis Platform

**AI Destekli PET/CT Görüntü Analizi ve Rapor Üretimi Platformu**

## 🚀 Hızlı Başlat

### Backend
```bash
cd backend
python3 -m venv .venv310
source .venv310/bin/activate  # macOS/Linux
# .venv310\Scripts\activate  # Windows
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
npm install
echo "VITE_API_BASE_URL=http://127.0.0.1:8000" > .env.development.local
npm run dev
```

## 🏗️ Proje Yapısı

```
neuropetrix-3/
├── backend/                 # FastAPI backend
│   ├── main.py             # Ana API endpoint'leri
│   ├── requirements.txt    # Temel dependencies
│   ├── requirements-optional.txt  # Opsiyonel dependencies
│   └── ...
├── components/             # React bileşenleri
├── services/               # API servisleri
├── types.ts               # TypeScript tip tanımları
├── vite.config.ts         # Vite konfigürasyonu
└── ...
```

## 🔧 Geliştirme (Dev)

### Backend Çalıştırma
```bash
cd backend
python3 -m venv .venv310
source .venv310/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Port 8000 meşgulse:**
```bash
kill -9 $(lsof -t -i :8000) 2>/dev/null || true
```

### Frontend Çalıştırma
```bash
npm install
echo "VITE_API_BASE_URL=http://127.0.0.1:8000" > .env.development.local
npm run dev
```

**Port 5173 meşgulse:** Vite otomatik olarak 5174'e geçer.

### Build Test
```bash
npm run build  # dist/ klasörü oluşturur
```

## 🌐 Deploy (Netlify)

### Frontend Deploy
1. **Netlify'de "New site from Git"**
2. **GitHub repo:** `neuropetrix-3`
3. **Build command:** `npm run build`
4. **Publish directory:** `dist`
5. **Environment variables:**
   - `VITE_API_BASE_URL` = `https://<PROD_API_URL>`

### Backend Deploy
Backend'i daha sonra Render/Railway/Fly/EC2'ye alabiliriz.

## 🔑 Environment Değişkenleri

### Development
```bash
# .env.development.local
VITE_API_BASE_URL=http://127.0.0.1:8000
VITE_APP_ENV=development
VITE_DEBUG=true
```

### Production
```bash
# .env.production
VITE_API_BASE_URL=https://<PROD_API_URL>
VITE_APP_ENV=production
VITE_DEBUG=false
```

## 📦 Opsiyonel: Radyomik

### PyRadiomics Kurulumu
```bash
cd backend
source .venv310/bin/activate
pip install -r requirements-optional.txt
```

**Not:** PyRadiomics derleme sorunlarına neden olabilir. Kurulum başarısız olursa:
- Kod otomatik olarak mock radyomik özellikler kullanır
- UI'de "Radyomik: Kapalı" rozeti gösterilir
- Temel işlevsellik etkilenmez

### Radyomik Özellikler
- **First Order:** SUV, hacim, yoğunluk
- **Shape:** Boyut, şekil, kompaktlık
- **Texture:** GLCM, GLRLM, GLSZM
- **Clinical:** Metastaz riski, tedavi yanıtı

## 🧪 Test

### Backend Test
```bash
cd backend
source .venv310/bin/activate
python -m pytest tests/  # Eğer test varsa
```

### Frontend Test
```bash
npm test  # Eğer test varsa
npm run build  # Build test
```

## 📚 API Dokümantasyonu

Backend çalıştıktan sonra:
- **Swagger UI:** http://127.0.0.1:8000/docs
- **ReDoc:** http://127.0.0.1:8000/redoc

## 🔍 Özellikler

### AI Analiz
- **Segmentasyon:** MONAI UNet ile lezyon tespiti
- **Radyomik:** PyRadiomics ile özellik çıkarma
- **Klinik Değerlendirme:** Literatür entegrasyonu

### Rapor Üretimi
- **TSNM Uyumlu:** Türk Nükleer Tıp Derneği kılavuzları
- **Çoklu Format:** PDF, JSON, Word, HTML
- **AI Destekli:** Otomatik klinik öneriler

### Entegrasyonlar
- **HBYS:** Hastane bilgi sistemi entegrasyonu
- **DICOM:** Görüntü formatı desteği
- **Whisper:** Ses kaydı transkripsiyonu

## 🚨 Sorun Giderme

### Backend Başlamıyor
```bash
# Port kontrolü
lsof -i :8000
# Process kill
kill -9 $(lsof -t -i :8000)

# Virtual environment kontrolü
which python
source .venv310/bin/activate
```

### Frontend Build Hatası
```bash
# Node modules temizleme
rm -rf node_modules package-lock.json
npm install

# Build cache temizleme
npm run build -- --force
```

### PyRadiomics Hatası
```bash
# Opsiyonel requirements'ı atla
pip install -r requirements.txt  # Sadece temel dependencies
# Kod otomatik olarak mock özellikler kullanır
```

## 📝 Lisans

MIT License

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request açın

## 📞 İletişim

- **Proje:** [GitHub Issues](https://github.com/ERFFF1/neuropetrix-3/issues)
- **Geliştirici:** [GitHub Profile](https://github.com/ERFFF1)

---

**NeuroPETrix** - AI destekli PET/CT analizi ve rapor üretimi platformu 🧠🔬
