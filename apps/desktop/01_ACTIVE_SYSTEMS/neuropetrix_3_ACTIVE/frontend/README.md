# NeuroPETRIX Frontend

Modern React tabanlı klinik karar destek sistemi frontend uygulaması.

## Özellikler

- **Modern UI/UX**: React + TypeScript + Tailwind CSS
- **AI Entegrasyonu**: Gemini 2.5 Flash ile akıllı analiz
- **Real-time**: WebSocket ile canlı güncellemeler
- **DICOM Desteği**: Tıbbi görüntü yükleme ve görüntüleme
- **Chat Sistemi**: AI ile sohbet edebilme
- **Responsive**: Mobil ve desktop uyumlu

## Kurulum

1. **Bağımlılıkları yükleyin:**
```bash
npm install
```

2. **Environment dosyasını oluşturun:**
```bash
cp env.example .env.local
```

3. **Environment değişkenlerini ayarlayın:**
```bash
# .env.local dosyasını düzenleyin
VITE_GEMINI_API_KEY=your_gemini_api_key_here
VITE_API_URL=http://localhost:8000
```

4. **Uygulamayı başlatın:**
```bash
npm run dev
```

## Geliştirme

```bash
# Development server
npm run dev

# Build
npm run build

# Preview
npm run preview

# Lint
npm run lint
```

## API Entegrasyonu

Frontend, backend API'si ile şu endpoint'ler üzerinden iletişim kurar:

- `POST /api/security/login` - Kullanıcı girişi
- `GET /api/cases` - Vaka listesi
- `POST /api/cases` - Yeni vaka oluşturma
- `GET /api/cases/{id}` - Vaka detayı
- `PATCH /api/cases/{id}` - Vaka güncelleme
- `POST /api/advanced-ai/analyze` - AI analizi
- `POST /api/cases/{id}/chat` - Sohbet mesajı
- `POST /api/cases/{id}/dicom` - DICOM yükleme

## WebSocket

Real-time güncellemeler için WebSocket bağlantısı:
- `ws://localhost:8000/ws/connect/{token}`

## Bileşenler

- **App.tsx**: Ana uygulama bileşeni
- **LoginScreen.tsx**: Giriş ekranı
- **CaseList.tsx**: Vaka listesi
- **CaseDetail.tsx**: Vaka detay sayfası
- **AnalysisResult.tsx**: AI analiz sonuçları
- **ChatInterface.tsx**: AI sohbet arayüzü
- **DicomViewer.tsx**: DICOM görüntüleyici
- **PatientDataForm.tsx**: Hasta veri formu

## Teknolojiler

- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool
- **Tailwind CSS**: Styling
- **Axios**: HTTP client
- **Lucide React**: Icons
- **Google Generative AI**: AI entegrasyonu

## Lisans

MIT
