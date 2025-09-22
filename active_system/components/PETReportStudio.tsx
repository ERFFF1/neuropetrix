import React, { useState } from 'react';

interface PatientCase {
  id: string;
  name: string;
  age: number;
  gender: string;
  diagnosis: string;
}

interface PETReportStudioProps {
  patientCase: PatientCase | null;
}

export default function PETReportStudio({ patientCase }: PETReportStudioProps) {
  const [activeTab, setActiveTab] = useState<'dicom' | 'asr' | 'report'>('dicom');
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [transcription, setTranscription] = useState('');
  const [reportContent, setReportContent] = useState('');

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    setUploadedFiles(prev => [...prev, ...files]);
  };

  const handleTranscription = () => {
    // Mock transcription
    setTranscription('Hasta 65 yaşında erkek, akciğer kanseri şüphesi ile başvurdu. PET/CT incelemesinde sağ üst lob anterior segmentte 2.5 cm çapında hipermetabolik lezyon izlendi. SUVmax değeri 8.5 olarak ölçüldü.');
  };

  const generateReport = () => {
    const mockReport = `
# PET/CT Raporu

**Hasta Bilgileri:**
- Ad Soyad: ${patientCase?.name || 'Belirtilmemiş'}
- Yaş: ${patientCase?.age || 'Belirtilmemiş'}
- Cinsiyet: ${patientCase?.gender === 'M' ? 'Erkek' : 'Kadın'}

**Klinik Bilgi:**
${patientCase?.diagnosis || 'Belirtilmemiş'}

**Teknik Bilgiler:**
- İnceleme Tarihi: ${new Date().toLocaleDateString('tr-TR')}
- Cihaz: GE Discovery 710
- Kontrast: İyotlu kontrast madde

**Bulgular:**
${transcription || 'Transkripsiyon yapılmamış'}

**Sonuç:**
Akciğer kanseri şüphesi ile uyumlu bulgular mevcuttur. Histopatolojik doğrulama önerilir.

**Öneriler:**
1. Biyopsi ile histopatolojik doğrulama
2. 3 ay sonra kontrol PET/CT
3. Onkoloji konsültasyonu
    `;
    setReportContent(mockReport);
  };

  return (
    <div className="p-6 bg-medical-50 min-h-full">
      <div className="max-w-7xl mx-auto">
        {/* Başlık */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-800 mb-2">
            📋 PET Rapor Stüdyosu
          </h1>
          <p className="text-slate-600">
            DICOM yükleme, ASR transkripsiyon ve rapor oluşturma
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-md border border-medical-200 mb-6">
          <div className="border-b border-medical-200">
            <nav className="flex space-x-8 px-6">
              {[
                { key: 'dicom', label: 'DICOM Upload', icon: '📁' },
                { key: 'asr', label: 'ASR Transkripsiyon', icon: '🎤' },
                { key: 'report', label: 'Rapor Oluşturma', icon: '📄' }
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key as any)}
                  className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.key
                      ? 'border-medical-500 text-medical-600'
                      : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {/* DICOM Upload Tab */}
            {activeTab === 'dicom' && (
              <div className="space-y-6">
                <h3 className="text-xl font-semibold text-slate-800">📁 DICOM Dosya Yükleme</h3>
                
                <div className="border-2 border-dashed border-medical-300 rounded-lg p-8 text-center">
                  <div className="text-4xl mb-4">📁</div>
                  <h4 className="text-lg font-medium text-slate-700 mb-2">DICOM Dosyalarını Sürükleyin</h4>
                  <p className="text-slate-600 mb-4">veya dosya seçmek için tıklayın</p>
                  <input
                    type="file"
                    multiple
                    accept=".dcm,.dicom"
                    onChange={handleFileUpload}
                    className="hidden"
                    id="dicom-upload"
                  />
                  <label
                    htmlFor="dicom-upload"
                    className="bg-medical-600 text-white px-6 py-3 rounded-md hover:bg-medical-700 cursor-pointer transition-colors duration-200"
                  >
                    Dosya Seç
                  </label>
                </div>

                {uploadedFiles.length > 0 && (
                  <div className="bg-medical-50 p-4 rounded-lg">
                    <h4 className="font-medium text-slate-700 mb-2">Yüklenen Dosyalar:</h4>
                    <div className="space-y-2">
                      {uploadedFiles.map((file, index) => (
                        <div key={index} className="flex items-center justify-between p-2 bg-white rounded">
                          <span className="text-sm text-slate-600">{file.name}</span>
                          <span className="text-xs text-slate-500">{(file.size / 1024 / 1024).toFixed(2)} MB</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* ASR Transkripsiyon Tab */}
            {activeTab === 'asr' && (
              <div className="space-y-6">
                <h3 className="text-xl font-semibold text-slate-800">🎤 ASR Transkripsiyon</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-medium text-slate-700 mb-2">Ses Kaydı</h4>
                    <div className="border-2 border-dashed border-medical-300 rounded-lg p-6 text-center">
                      <div className="text-3xl mb-2">🎤</div>
                      <p className="text-slate-600 mb-4">Ses dosyası yükleyin veya kayıt yapın</p>
                      <button className="bg-medical-600 text-white px-4 py-2 rounded-md hover:bg-medical-700 transition-colors duration-200">
                        Kayıt Başlat
                      </button>
                    </div>
                  </div>

                  <div>
                    <h4 className="font-medium text-slate-700 mb-2">Transkripsiyon</h4>
                    <textarea
                      value={transcription}
                      onChange={(e) => setTranscription(e.target.value)}
                      placeholder="Transkripsiyon burada görünecek..."
                      className="w-full h-32 p-3 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500 focus:border-medical-500"
                    />
                    <button
                      onClick={handleTranscription}
                      className="mt-2 bg-success-600 text-white px-4 py-2 rounded-md hover:bg-success-700 transition-colors duration-200"
                    >
                      Transkripsiyon Yap
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Rapor Oluşturma Tab */}
            {activeTab === 'report' && (
              <div className="space-y-6">
                <h3 className="text-xl font-semibold text-slate-800">📄 Rapor Oluşturma</h3>
                
                <div className="flex space-x-4 mb-4">
                  <button
                    onClick={generateReport}
                    className="bg-medical-600 text-white px-4 py-2 rounded-md hover:bg-medical-700 transition-colors duration-200"
                  >
                    Rapor Oluştur
                  </button>
                  <button className="bg-success-600 text-white px-4 py-2 rounded-md hover:bg-success-700 transition-colors duration-200">
                    PDF İndir
                  </button>
                  <button className="bg-warning-600 text-white px-4 py-2 rounded-md hover:bg-warning-700 transition-colors duration-200">
                    HBYS'e Gönder
                  </button>
                </div>

                <div className="bg-white border border-medical-200 rounded-lg p-4">
                  <textarea
                    value={reportContent}
                    onChange={(e) => setReportContent(e.target.value)}
                    placeholder="Rapor içeriği burada görünecek..."
                    className="w-full h-96 p-4 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500 focus:border-medical-500 font-mono text-sm"
                  />
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Hızlı Eylemler */}
        <div className="bg-white rounded-lg shadow-md border border-medical-200 p-6">
          <h3 className="text-lg font-semibold text-slate-800 mb-4">⚡ Hızlı Eylemler</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button className="bg-medical-600 text-white p-4 rounded-lg hover:bg-medical-700 transition-colors duration-200">
              <div className="text-2xl mb-2">📁</div>
              <div className="font-medium">DICOM Yükle</div>
              <div className="text-sm opacity-90">Görüntü dosyaları</div>
            </button>
            
            <button className="bg-success-600 text-white p-4 rounded-lg hover:bg-success-700 transition-colors duration-200">
              <div className="text-2xl mb-2">🎤</div>
              <div className="font-medium">Ses Kaydı</div>
              <div className="text-sm opacity-90">ASR transkripsiyon</div>
            </button>
            
            <button className="bg-warning-600 text-white p-4 rounded-lg hover:bg-warning-700 transition-colors duration-200">
              <div className="text-2xl mb-2">📄</div>
              <div className="font-medium">Rapor Oluştur</div>
              <div className="text-sm opacity-90">Otomatik rapor</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}




