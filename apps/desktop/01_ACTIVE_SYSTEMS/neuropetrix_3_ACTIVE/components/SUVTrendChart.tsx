import React from 'react';

interface SUVMeasurement {
  id: string;
  patient_id: string;
  case_id: string;
  region: string;
  suv_value: number;
  measurement_date: string;
  region_volume?: number;
  notes?: string;
  created_at: string;
}

interface SUVTrendChartProps {
  measurements: SUVMeasurement[];
  region: string;
  chartType?: 'line' | 'bar' | 'scatter';
  showVolume?: boolean;
}

export default function SUVTrendChart({ 
  measurements, 
  region, 
  chartType = 'line',
  showVolume = false 
}: SUVTrendChartProps) {
  // Veriyi hazırla
  const filteredMeasurements = measurements.filter(m => m.region === region);
  const sortedMeasurements = filteredMeasurements.sort((a, b) => 
    new Date(a.measurement_date).getTime() - new Date(b.measurement_date).getTime()
  );

  const labels = sortedMeasurements.map(m => 
    new Date(m.measurement_date).toLocaleDateString('tr-TR')
  );
  
  const suvValues = sortedMeasurements.map(m => m.suv_value);
  const volumeValues = sortedMeasurements.map(m => m.region_volume || 0);

  // İstatistiksel bilgiler
  const stats = {
    mean: suvValues.length > 0 ? suvValues.reduce((a, b) => a + b, 0) / suvValues.length : 0,
    max: suvValues.length > 0 ? Math.max(...suvValues) : 0,
    min: suvValues.length > 0 ? Math.min(...suvValues) : 0,
    trend: suvValues.length > 1 ? 
      (suvValues[suvValues.length - 1] - suvValues[0]) / suvValues[0] * 100 : 0
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-medical-200 p-6">
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-medical-900 mb-2">
          {region} SUV Trend Analizi
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-medical-50 rounded-lg p-3">
            <div className="text-sm text-medical-600">Ortalama SUV</div>
            <div className="text-xl font-bold text-medical-900">
              {stats.mean.toFixed(2)}
            </div>
          </div>
          <div className="bg-medical-50 rounded-lg p-3">
            <div className="text-sm text-medical-600">Maksimum SUV</div>
            <div className="text-xl font-bold text-medical-900">
              {stats.max.toFixed(2)}
            </div>
          </div>
          <div className="bg-medical-50 rounded-lg p-3">
            <div className="text-sm text-medical-600">Minimum SUV</div>
            <div className="text-xl font-bold text-medical-900">
              {stats.min.toFixed(2)}
            </div>
          </div>
          <div className="bg-medical-50 rounded-lg p-3">
            <div className="text-sm text-medical-600">Trend (%)</div>
            <div className={`text-xl font-bold ${
              stats.trend > 0 ? 'text-green-600' : 
              stats.trend < 0 ? 'text-red-600' : 'text-medical-900'
            }`}>
              {stats.trend > 0 ? '+' : ''}{stats.trend.toFixed(1)}%
            </div>
          </div>
        </div>
      </div>

      {/* Chart placeholder - Chart.js entegrasyonu için hazır */}
      <div className="h-80 bg-medical-50 rounded-lg flex items-center justify-center">
        <div className="text-center">
          <div className="text-6xl mb-4">📊</div>
          <h4 className="text-lg font-semibold text-medical-900 mb-2">
            {region} SUV Trend Grafiği
          </h4>
          <p className="text-medical-600 mb-4">
            {chartType === 'line' ? 'Çizgi Grafik' : 
             chartType === 'bar' ? 'Sütun Grafik' : 'Dağılım Grafik'}
          </p>
          <div className="space-y-2 text-sm text-medical-500">
            <div>Toplam Ölçüm: {measurements.length}</div>
            <div>Grafik Tipi: {chartType}</div>
            {showVolume && <div>Hacim Gösterimi: Aktif</div>}
          </div>
        </div>
      </div>

      <div className="mt-4 flex justify-between items-center">
        <div className="text-sm text-medical-600">
          Toplam {measurements.length} ölçüm • Son güncelleme: {
            measurements.length > 0 ? 
            new Date(measurements[measurements.length - 1].created_at).toLocaleString('tr-TR') : 
            'Veri yok'
          }
        </div>
        <div className="flex space-x-2">
          <button 
            onClick={() => window.print()}
            className="px-3 py-1 bg-medical-600 text-white rounded-md text-sm hover:bg-medical-700 transition-colors"
          >
            Yazdır
          </button>
          <button 
            onClick={() => {
              // Simulate chart download
              const dataStr = JSON.stringify({
                region,
                measurements: sortedMeasurements,
                stats
              }, null, 2);
              const dataBlob = new Blob([dataStr], {type: 'application/json'});
              const url = URL.createObjectURL(dataBlob);
              const link = document.createElement('a');
              link.href = url;
              link.download = `${region}_SUV_Trend.json`;
              link.click();
            }}
            className="px-3 py-1 bg-green-600 text-white rounded-md text-sm hover:bg-green-700 transition-colors"
          >
            İndir
          </button>
        </div>
      </div>
    </div>
  );
}
