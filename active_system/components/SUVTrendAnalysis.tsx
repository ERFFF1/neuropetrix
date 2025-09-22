import React, { useState } from 'react';

interface SUVData {
  id: string;
  date: string;
  suvValue: number;
  location: string;
  lesionType: 'primary' | 'metastasis' | 'benign';
}

interface Patient {
  id: string;
  name: string;
  age: number;
  diagnosis: string;
}

const SUVTrendAnalysis: React.FC = () => {
  const [selectedPatient, setSelectedPatient] = useState<string>('');
  const [dateRange, setDateRange] = useState<[string, string]>(['2024-01-01', '2024-08-24']);
  const [suvData, setSuvData] = useState<SUVData[]>([
    { id: '1', date: '2024-01-15', suvValue: 3.2, location: 'Karaciğer', lesionType: 'primary' },
    { id: '2', date: '2024-02-15', suvValue: 2.8, location: 'Karaciğer', lesionType: 'primary' },
    { id: '3', date: '2024-03-15', suvValue: 2.1, location: 'Karaciğer', lesionType: 'primary' },
    { id: '4', date: '2024-04-15', suvValue: 1.9, location: 'Karaciğer', lesionType: 'primary' },
    { id: '5', date: '2024-05-15', suvValue: 1.5, location: 'Karaciğer', lesionType: 'primary' },
    { id: '6', date: '2024-06-15', suvValue: 1.2, location: 'Karaciğer', lesionType: 'primary' },
    { id: '7', date: '2024-07-15', suvValue: 0.9, location: 'Karaciğer', lesionType: 'primary' },
    { id: '8', date: '2024-08-15', suvValue: 0.7, location: 'Karaciğer', lesionType: 'primary' }
  ]);

  const [patients] = useState<Patient[]>([
    { id: '1', name: 'Ahmet Yılmaz', age: 45, diagnosis: 'Karaciğer Kanseri' },
    { id: '2', name: 'Fatma Demir', age: 52, diagnosis: 'Akciğer Kanseri' },
    { id: '3', name: 'Mehmet Kaya', age: 38, diagnosis: 'Lenfoma' }
  ]);

  const [newSuvData, setNewSuvData] = useState<Omit<SUVData, 'id'>>({
    date: '',
    suvValue: 0,
    location: '',
    lesionType: 'primary'
  });

  // İstatistikler hesapla
  const calculateStats = () => {
    if (suvData.length === 0) return null;

    const values = suvData.map(d => d.suvValue);
    const avg = values.reduce((a, b) => a + b, 0) / values.length;
    const min = Math.min(...values);
    const max = Math.max(...values);
    
    // Trend hesapla (son 3 değer vs ilk 3 değer)
    const recentAvg = values.slice(-3).reduce((a, b) => a + b, 0) / 3;
    const initialAvg = values.slice(0, 3).reduce((a, b) => a + b, 0) / 3;
    const trend = recentAvg - initialAvg;
    const trendPercent = ((trend / initialAvg) * 100);

    return { avg, min, max, trend, trendPercent };
  };

  const stats = calculateStats();

  // Yeni SUV verisi ekle
  const addSuvData = () => {
    if (!newSuvData.date || !newSuvData.location || newSuvData.suvValue <= 0) {
      alert('Lütfen tüm alanları doldurun');
      return;
    }

    const newData: SUVData = {
      ...newSuvData,
      id: Date.now().toString()
    };

    setSuvData(prev => [...prev, newData]);
    setNewSuvData({ date: '', suvValue: 0, location: '', lesionType: 'primary' });
  };

  // Trend raporu oluştur
  const generateTrendReport = () => {
    if (!stats) return;
    
    const report = `
SUV Trend Raporu
================
Hasta: ${patients.find(p => p.id === selectedPatient)?.name || 'Seçilmemiş'}
Tarih Aralığı: ${dateRange[0]} - ${dateRange[1]}
Toplam Ölçüm: ${suvData.length}

İstatistikler:
- Ortalama SUV: ${stats.avg.toFixed(2)}
- Minimum SUV: ${stats.min.toFixed(2)}
- Maksimum SUV: ${stats.max.toFixed(2)}
- Trend: ${stats.trend > 0 ? '+' : ''}${stats.trend.toFixed(2)} (${stats.trendPercent > 0 ? '+' : ''}${stats.trendPercent.toFixed(1)}%)

Sonuç: ${stats.trend < -0.5 ? 'Pozitif yanıt' : stats.trend > 0.5 ? 'Hastalık ilerlemesi' : 'Stabil'}
    `;
    
    console.log(report);
    alert('Trend raporu oluşturuldu! Console\'da görüntüleyin.');
  };

  // PDF indir (mock)
  const downloadPDF = () => {
    alert('PDF indirme özelliği geliştirilecek');
  };

  // Veri dışa aktar
  const exportData = () => {
    const csvContent = [
      'Tarih,SUV Değeri,Konum,Lezyon Tipi',
      ...suvData.map(d => `${d.date},${d.suvValue},${d.location},${d.lesionType}`)
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `suv_data_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const getLesionTypeColor = (type: string) => {
    switch (type) {
      case 'primary': return 'bg-red-100 text-red-800';
      case 'metastasis': return 'bg-orange-100 text-orange-800';
      case 'benign': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Başlık */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-800">
            SUV Trend Analizi
          </h1>
          <p className="text-slate-600 mt-2">
            PET/CT SUV değerlerinin zaman içindeki değişimi
          </p>
        </div>

        {/* Kontrol Paneli */}
        <div className="bg-white rounded-lg shadow-md border border-slate-200 mb-6">
          <div className="p-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Hasta Seçimi */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Hasta
                </label>
                <select
                  value={selectedPatient}
                  onChange={(e) => setSelectedPatient(e.target.value)}
                  className="w-full p-3 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Hasta seçin</option>
                  {patients.map(patient => (
                    <option key={patient.id} value={patient.id}>
                      {patient.name} ({patient.age} yaş) - {patient.diagnosis}
                    </option>
                  ))}
                </select>
              </div>

              {/* Tarih Aralığı */}
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Başlangıç Tarihi
                </label>
                <input
                  type="date"
                  value={dateRange[0]}
                  onChange={(e) => setDateRange([e.target.value, dateRange[1]])}
                  className="w-full p-3 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-slate-700 mb-2">
                  Bitiş Tarihi
                </label>
                <input
                  type="date"
                  value={dateRange[1]}
                  onChange={(e) => setDateRange([dateRange[0], e.target.value])}
                  className="w-full p-3 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>

            <div className="mt-4 flex justify-center">
              <button className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700">
                Analiz Et
              </button>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Grafik Alanı */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow-md border border-slate-200 p-6">
              <h3 className="text-lg font-semibold text-slate-800 mb-4">SUV Trend Grafiği</h3>
              
              {/* Mock Chart */}
              <div className="bg-slate-50 rounded-lg p-8 text-center">
                <div className="text-slate-500 mb-4">
                  <svg className="mx-auto h-16 w-16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                </div>
                <p className="text-slate-600 mb-2">SUV Trend Grafiği</p>
                <p className="text-slate-500 text-sm">Chart.js veya Recharts entegrasyonu geliştirilecek</p>
                
                {/* Basit Trend Göstergesi */}
                {stats && (
                  <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                    <div className="text-sm text-blue-800">
                      <div className="flex items-center justify-center space-x-2">
                        <span>Trend:</span>
                        <span className={`font-bold ${stats.trend < 0 ? 'text-green-600' : 'text-red-600'}`}>
                          {stats.trend < 0 ? '↘️ Azalma' : '↗️ Artış'}
                        </span>
                        <span>({stats.trendPercent > 0 ? '+' : ''}{stats.trendPercent.toFixed(1)}%)</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Sağ Panel - İstatistikler */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-md border border-slate-200 p-6">
              <h3 className="text-lg font-semibold text-slate-800 mb-4">İstatistikler</h3>
              
              {stats ? (
                <div className="space-y-4">
                  <div className="bg-slate-50 rounded-lg p-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-blue-600">{stats.avg.toFixed(2)}</div>
                      <div className="text-sm text-slate-600">Ortalama SUV</div>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-green-50 rounded-lg p-3 text-center">
                      <div className="text-lg font-bold text-green-600">{stats.min.toFixed(2)}</div>
                      <div className="text-xs text-green-700">Min SUV</div>
                    </div>
                    <div className="bg-red-50 rounded-lg p-3 text-center">
                      <div className="text-lg font-bold text-red-600">{stats.max.toFixed(2)}</div>
                      <div className="text-xs text-red-700">Max SUV</div>
                    </div>
                  </div>
                  
                  <div className="bg-blue-50 rounded-lg p-3 text-center">
                    <div className="text-sm text-blue-800">
                      <div className="font-medium">Trend</div>
                      <div className={`text-lg font-bold ${stats.trend < 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {stats.trend > 0 ? '+' : ''}{stats.trend.toFixed(2)}
                      </div>
                      <div className="text-xs">
                        ({stats.trendPercent > 0 ? '+' : ''}{stats.trendPercent.toFixed(1)}%)
                      </div>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="text-center text-slate-500 py-8">
                  Veri bulunamadı
                </div>
              )}

              <div className="mt-6 space-y-3">
                <button
                  onClick={generateTrendReport}
                  disabled={!stats}
                  className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Trend Raporu Oluştur
                </button>
                <button
                  onClick={downloadPDF}
                  className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700"
                >
                  PDF İndir
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Alt Kısım - Veri Yönetimi */}
        <div className="bg-white rounded-lg shadow-md border border-slate-200 mt-6">
          <div className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-slate-800">SUV Veri Yönetimi</h3>
              <button
                onClick={exportData}
                className="bg-slate-600 text-white px-4 py-2 rounded-md hover:bg-slate-700"
              >
                Veri Dışa Aktar
              </button>
            </div>

            {/* Yeni Veri Ekleme Formu */}
            <div className="bg-slate-50 rounded-lg p-4 mb-6">
              <h4 className="font-medium text-slate-800 mb-3">Yeni SUV Verisi Ekle</h4>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <input
                  type="date"
                  value={newSuvData.date}
                  onChange={(e) => setNewSuvData(prev => ({ ...prev, date: e.target.value }))}
                  className="p-2 border border-slate-300 rounded-md"
                  placeholder="Tarih"
                />
                <input
                  type="number"
                  step="0.1"
                  value={newSuvData.suvValue}
                  onChange={(e) => setNewSuvData(prev => ({ ...prev, suvValue: parseFloat(e.target.value) || 0 }))}
                  className="p-2 border border-slate-300 rounded-md"
                  placeholder="SUV Değeri"
                />
                <input
                  type="text"
                  value={newSuvData.location}
                  onChange={(e) => setNewSuvData(prev => ({ ...prev, location: e.target.value }))}
                  className="p-2 border border-slate-300 rounded-md"
                  placeholder="Konum"
                />
                <select
                  value={newSuvData.lesionType}
                  onChange={(e) => setNewSuvData(prev => ({ ...prev, lesionType: e.target.value as any }))}
                  className="p-2 border border-slate-300 rounded-md"
                >
                  <option value="primary">Primer</option>
                  <option value="metastasis">Metastaz</option>
                  <option value="benign">Benign</option>
                </select>
              </div>
              <div className="mt-3">
                <button
                  onClick={addSuvData}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                >
                  Veri Ekle
                </button>
              </div>
            </div>

            {/* SUV Veri Tablosu */}
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-200">
                    <th className="text-left py-2 px-2 text-slate-600">Tarih</th>
                    <th className="text-left py-2 px-2 text-slate-600">SUV</th>
                    <th className="text-left py-2 px-2 text-slate-600">Konum</th>
                    <th className="text-left py-2 px-2 text-slate-600">Tip</th>
                    <th className="text-left py-2 px-2 text-slate-600">İşlem</th>
                  </tr>
                </thead>
                <tbody>
                  {suvData.map((item) => (
                    <tr key={item.id} className="border-b border-slate-100">
                      <td className="py-2 px-2 text-slate-800">{item.date}</td>
                      <td className="py-2 px-2 text-slate-800 font-medium">{item.suvValue}</td>
                      <td className="py-2 px-2 text-slate-600">{item.location}</td>
                      <td className="py-2 px-2">
                        <span className={`px-2 py-1 rounded text-xs font-medium ${getLesionTypeColor(item.lesionType)}`}>
                          {item.lesionType === 'primary' ? 'Primer' : 
                           item.lesionType === 'metastasis' ? 'Metastaz' : 'Benign'}
                        </span>
                      </td>
                      <td className="py-2 px-2">
                        <button className="text-red-600 hover:text-red-800 text-sm">
                          Sil
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SUVTrendAnalysis;















