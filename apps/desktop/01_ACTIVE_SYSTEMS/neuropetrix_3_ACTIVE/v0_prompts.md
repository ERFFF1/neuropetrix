# 🚀 v0.dev Prompts for NeuroPETrix

## 📋 **Kullanım Talimatları:**
1. [v0.dev](https://v0.dev) sitesine git
2. Aşağıdaki prompt'ları kopyala-yapıştır
3. Kodu indir → `components/` klasörüne ekle
4. `services/api.ts` ile backend'e bağla

---

## 🖥️ **1. System Monitor Sayfası**

```
React + TypeScript + Tailwind CSS kullan. Türkçe UI. Koyu/açık tema desteği. 

Üstte "NeuroPETrix — Sistem Durumu" başlığı. İki Card satırı:

**Backend Card:**
- Durum rozeti (Yeşil/Healthy, Sarı/Degraded, Kırmızı/Down)
- Son health zamanı
- "Test Et" butonu (http://127.0.0.1:8000/health'e istek at)

**Frontend Card:**
- Durum rozeti
- http://127.0.0.1:8501 linki
- "Yeniden Başlat" düğmesi

**Alt kısım:**
- Tabs: "Backend Log", "Frontend Log" 
- Log içeriği (table veya pre)
- Sağ üstte "Yenile" ve "Logları İndir" butonları

lucide-react ikonları kullan: Activity, Server, Monitor, Download, Refresh
Bileşenleri küçük parçalara böl (components/ altına)
```

---

## 📊 **2. PET Rapor Stüdyosu**

```
React + TypeScript + Tailwind CSS. Türkçe UI. Sol tarafta Tabs:

**"DICOM Serileri" Tab:**
- Hasta bilgileri tablosu (Hasta, StudyDate, SeriesDescription)
- Her satırda "Seç" butonu
- "Yeni DICOM Yükle" butonu

**"ASR Transkript" Tab:**
- Ses yükleme alanı (drag & drop)
- "Transkribe Et" butonu
- Sonuç textarea (readonly)
- "Metni Kopyala" butonu

**"Rapor" Tab:**
- Form alanları: Ön tanı, Bulgular, Sonuç
- "Rapor Oluştur" butonu
- "HBYS'e Gönder" butonu
- Toast bildirimleri

lucide-react ikonları: FileText, Mic, Upload, Send, Copy
```

---

## 🔬 **3. Evidence Panel / Literatür**

```
React + TypeScript + Tailwind CSS. Türkçe UI.

**Üst kısım:**
- Arama input'u + "Ara" butonu
- "Ağırlıklandır" toggle switch
- "Filtreleri Göster/Gizle" butonu

**Ana içerik:**
- Sonuçları Card grid'de göster
- Her card: başlık, özet, DOI/PMID, kanıt düzeyi
- "Seç" checkbox'ları

**Sağ sidebar (filtreler):**
- Yıl aralığı slider
- Kanıt düzeyi dropdown
- Çalışma tipi checkboxes
- "Filtreleri Temizle" butonu

**Alt kısım:**
- "Seçili Kanıtları Rapor Metnine Ekle" düğmesi
- Seçili sayısı badge

lucide-react ikonları: Search, Filter, BookOpen, FileText, Plus
```

---

## 🎨 **4. SUV Trend Analizi**

```
React + TypeScript + Tailwind CSS. Türkçe UI.

**Üst kısım:**
- "SUV Trend Analizi" başlığı
- Hasta seçimi dropdown
- Tarih aralığı picker
- "Analiz Et" butonu

**Grafik alanı:**
- Line chart (SUV değerleri vs zaman)
- Zoom, pan desteği
- Trend çizgisi overlay
- Anomali işaretleri

**Sağ panel:**
- İstatistikler (ortalama, min, max, trend)
- "Trend Raporu Oluştur" butonu
- "PDF İndir" butonu

**Alt kısım:**
- SUV veri tablosu
- "Yeni Veri Ekle" form
- "Veri Dışa Aktar" butonu

lucide-react ikonları: TrendingUp, BarChart3, Download, Plus, FileText
```

---

## 🔧 **5. Script Management**

```
React + TypeScript + Tailwind CSS. Türkçe UI.

**Üst kısım:**
- "Script Yönetimi" başlığı
- "Yeni Script Ekle" butonu
- Arama input'u

**Ana içerik:**
- Script'leri kategorilere göre grupla
- Her script için card:
  - İsim, açıklama, kategori
  - "Çalıştır", "Düzenle", "Sil" butonları
  - Son çalışma zamanı
  - Durum badge'i

**Kategoriler:**
- AI/ML Script'leri
- Veri İşleme
- Rapor Üretimi
- Sistem Yönetimi

**Sağ sidebar:**
- Kategori filtreleri
- "Toplu İşlem" seçenekleri
- "Log Görüntüle" butonu

lucide-react ikonları: Code, Play, Edit, Trash2, Folder, Clock
```

---

## 🎯 **Entegrasyon Adımları:**

1. **v0.dev'de prompt'u yapıştır**
2. **Kodu indir** → `components/` klasörüne koy
3. **API bağlantılarını ekle:**
   ```tsx
   import { health, generateReport, transcribe } from '../services/api';
   ```
4. **Toast bildirimleri ekle:**
   ```tsx
   // Başarı
   toast.success("İşlem başarılı!");
   // Hata
   toast.error("Hata oluştu: " + error.message);
   ```
5. **Test et:**
   ```bash
   npm run dev  # Frontend
   ./start_system.sh start  # Backend
   ```

---

## 🎨 **Tema Tutarlılığı:**

- **Renkler:** slate-50, slate-800, blue-600, green-500, red-500
- **Font:** Inter (zaten yüklü)
- **Spacing:** p-4, m-2, gap-4
- **Border radius:** rounded-lg
- **Shadow:** shadow-md

---

## 🚀 **Hızlı Başlangıç:**

1. **System Monitor** ile başla (en kolay)
2. **PET Rapor Stüdyosu** ekle
3. **Evidence Panel** ile geliştir
4. **SUV Trend** ile tamamla

**Her sayfayı ayrı component olarak oluştur, sonra birleştir!**















