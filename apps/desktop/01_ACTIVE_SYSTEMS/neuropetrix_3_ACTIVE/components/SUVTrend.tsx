import React, { useState, useEffect } from 'react';
import SUVTrendChart from './SUVTrendChart';

interface PatientCase {
  id: string;
  patient_id: string;
  case_type: string;
  clinical_context: string;
  imaging_data?: any;
  lab_data?: any;
  notes?: string;
  created_at: string;
}

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

interface SUVTrendProps {
  patientCase: any;
}

export default function SUVTrend({ patientCase }: SUVTrendProps) {
  const [measurements, setMeasurements] = useState<SUVMeasurement[]>([]);
  const [selectedRegion, setSelectedRegion] = useState<string>('');
  const [chartType, setChartType] = useState<'line' | 'bar' | 'scatter'>('line');
  const [showVolume, setShowVolume] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [regions, setRegions] = useState<string[]>([]);

  // Mock data for demonstration
  const mockMeasurements: SUVMeasurement[] = [
    {
      id: "SUV001",
      patient_id: "P20241225001",
      case_id: "C20241225001",
      region: "Primer Lezyon",
      suv_value: 8.5,
      measurement_date: "2024-12-25",
      region_volume: 15.2,
      notes: "Bazal ölçüm",
      created_at: "2024-12-25T10:00:00"
    },
    {
      id: "SUV002",
      patient_id: "P20241225001",
      case_id: "C20241225001",
      region: "Primer Lezyon",
      suv_value: 7.8,
      measurement_date: "2025-01-15",
      region_volume: 14.8,
      notes: "Kemoterapi sonrası",
      created_at: "2025-01-15T10:00:00"
    },
    {
      id: "SUV003",
      patient_id: "P20241225001",
      case_id: "C20241225001",
      region: "Primer Lezyon",
      suv_value: 6.2,
      measurement_date: "2025-02-10",
      region_volume: 13.5,
      notes: "Tedavi yanıtı",
      created_at: "2025-02-10T10:00:00"
    },
    {
      id: "SUV004",
      patient_id: "P20241225001",
      case_id: "C20241225001",
      region: "Lenf Nodu 1",
      suv_value: 4.2,
      measurement_date: "2024-12-25",
      region_volume: 8.5,
      notes: "Mediastinal",
      created_at: "2024-12-25T10:00:00"
    },
    {
      id: "SUV005",
      patient_id: "P20241225001",
      case_id: "C20241225001",
      region: "Lenf Nodu 1",
      suv_value: 3.8,
      measurement_date: "2025-01-15",
      region_volume: 7.2,
      notes: "Kemoterapi sonrası",
      created_at: "2025-01-15T10:00:00"
    }
  ];

  useEffect(() => {
    // Load measurements from API or use mock data
    setMeasurements(mockMeasurements);
    
    // Extract unique regions
    const uniqueRegions = [...new Set(mockMeasurements.map(m => m.region))];
    setRegions(uniqueRegions);
    
    if (uniqueRegions.length > 0) {
      setSelectedRegion(uniqueRegions[0]);
    }
  }, []);

  const loadMeasurements = async () => {
    if (!patientCase?.patient?.id) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(`/api/suv/measurements/${patientCase.patient.id}`);
      if (response.ok) {
        const data = await response.json();
        setMeasurements(data);
        
        const uniqueRegions = [...new Set(data.map((m: SUVMeasurement) => m.region))];
        setRegions(uniqueRegions);
        
        if (uniqueRegions.length > 0 && !selectedRegion) {
          setSelectedRegion(uniqueRegions[0]);
        }
      }
    } catch (error) {
      console.error('SUV ölçümleri yüklenemedi:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const addMeasurement = async (measurement: Omit<SUVMeasurement, 'id' | 'created_at'>) => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/suv/measurements', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(measurement)
      });

      if (response.ok) {
        await loadMeasurements();
      }
    } catch (error) {
      console.error('SUV ölçümü eklenemedi:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const filteredMeasurements = measurements.filter(m => m.region === selectedRegion);

  return (
    <div className="min-h-screen bg-medical-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-medical-900 mb-2">SUV Trend Analizi</h1>
          <p className="text-medical-600">
            {patientCase?.patient?.name ? 
              `${patientCase.patient.name} - SUV değer takibi` : 
              'SUV değer analizi ve trend takibi'
            }
          </p>
        </div>

        {/* Controls */}
        <div className="bg-white rounded-lg shadow-sm border border-medical-200 p-6 mb-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-medical-700 mb-2">
                Bölge Seçimi
              </label>
              <select
                value={selectedRegion}
                onChange={(e) => setSelectedRegion(e.target.value)}
                className="w-full px-3 py-2 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500"
              >
                {regions.map(region => (
                  <option key={region} value={region}>{region}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-medical-700 mb-2">
                Grafik Tipi
              </label>
              <select
                value={chartType}
                onChange={(e) => setChartType(e.target.value as 'line' | 'bar' | 'scatter')}
                className="w-full px-3 py-2 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500"
              >
                <option value="line">Çizgi Grafik</option>
                <option value="bar">Sütun Grafik</option>
                <option value="scatter">Dağılım Grafik</option>
              </select>
            </div>

            <div className="flex items-center">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={showVolume}
                  onChange={(e) => setShowVolume(e.target.checked)}
                  className="mr-2 h-4 w-4 text-medical-600 focus:ring-medical-500 border-medical-300 rounded"
                />
                <span className="text-sm text-medical-700">Hacim Göster</span>
              </label>
            </div>

            <div className="flex items-end">
              <button
                onClick={loadMeasurements}
                disabled={isLoading}
                className="w-full bg-medical-600 text-white py-2 px-4 rounded-md hover:bg-medical-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? 'Yükleniyor...' : 'Yenile'}
              </button>
            </div>
          </div>
        </div>

        {/* Chart */}
        {selectedRegion && (
          <div className="mb-6">
            <SUVTrendChart
              measurements={filteredMeasurements}
              region={selectedRegion}
              chartType={chartType}
              showVolume={showVolume}
            />
          </div>
        )}

        {/* Measurements Table */}
        <div className="bg-white rounded-lg shadow-sm border border-medical-200">
          <div className="p-6 border-b border-medical-200">
            <h2 className="text-xl font-semibold text-medical-900">Ölçüm Geçmişi</h2>
          </div>
          
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-medical-200">
              <thead className="bg-medical-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-medical-500 uppercase tracking-wider">
                    Tarih
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-medical-500 uppercase tracking-wider">
                    Bölge
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-medical-500 uppercase tracking-wider">
                    SUV Max
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-medical-500 uppercase tracking-wider">
                    Hacim (cm³)
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-medical-500 uppercase tracking-wider">
                    Notlar
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-medical-200">
                {filteredMeasurements.map((measurement) => (
                  <tr key={measurement.id} className="hover:bg-medical-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-medical-900">
                      {new Date(measurement.measurement_date).toLocaleDateString('tr-TR')}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-medical-900">
                      {measurement.region}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-medical-900">
                      {measurement.suv_value.toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-medical-900">
                      {measurement.region_volume?.toFixed(1) || '-'}
                    </td>
                    <td className="px-6 py-4 text-sm text-medical-900">
                      {measurement.notes || '-'}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-6 flex space-x-4">
          <button className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors">
            Yeni Ölçüm Ekle
          </button>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors">
            Rapor Oluştur
          </button>
          <button className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 transition-colors">
            Karşılaştır
          </button>
        </div>
      </div>
    </div>
  );
}
