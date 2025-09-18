import React, { useState, useEffect } from 'react';
import { Patient, PatientCase } from '../types';
import GeminiAIStudio from './GeminiAIStudio';

interface DashboardProps {
  selectedCase?: PatientCase;
}

interface QuickAction {
  id: string;
  title: string;
  description: string;
  icon: string;
  color: string;
  action: () => void;
}

interface SystemMetric {
  name: string;
  value: string;
  change: string;
  trend: 'up' | 'down' | 'stable';
  color: string;
}

interface GeminiAIStatus {
  status: 'active' | 'inactive' | 'error';
  version: string;
  lastUpdate: string;
  aiConclusions: number;
  accuracy: string;
}

interface AIModuleStatus {
  name: string;
  status: string;
  capabilities: string[];
  last_used: string | null;
  available: boolean;
}

interface AIManagerStatus {
  total_modules: number;
  available_modules: number;
  modules: Record<string, AIModuleStatus>;
  initialized: boolean;
}

export default function Dashboard({ selectedCase }: DashboardProps) {
  const [recentPatients, setRecentPatients] = useState<Patient[]>([]);
  const [systemMetrics, setSystemMetrics] = useState<SystemMetric[]>([]);
  const [geminiAIStatus, setGeminiAIStatus] = useState<GeminiAIStatus>({
    status: 'inactive',
    version: '1.0.0',
    lastUpdate: 'N/A',
    aiConclusions: 0,
    accuracy: 'N/A'
  });
  const [aiManagerStatus, setAiManagerStatus] = useState<AIManagerStatus | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [showGeminiAI, setShowGeminiAI] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Gemini AI Studio status'u fetch et
      await fetchGeminiAIStatus();
      
      // AI Manager durumunu çek
      try {
        const response = await fetch('http://localhost:8000/ai-manager/status');
        if (response.ok) {
          const data = await response.json();
          setAiManagerStatus(data.ai_manager);
        }
      } catch (error) {
        console.warn('AI Manager durumu alınamadı:', error);
      }
      
      // Mock data for demonstration
      const mockPatients = [
        {
          id: 'P20241225001',
          name: 'Ahmet Yılmaz',
          age: 65,
          gender: 'Erkek',
          diagnosis: 'Akciğer Kanseri',
          lastVisit: '2024-12-25',
          status: 'active'
        },
        {
          id: 'P20241225002',
          name: 'Fatma Demir',
          age: 58,
          gender: 'Kadın',
          diagnosis: 'Lenfoma',
          lastVisit: '2024-12-24',
          status: 'active'
        },
        {
          id: 'P20241225003',
          name: 'Mehmet Kaya',
          age: 72,
          gender: 'Erkek',
          diagnosis: 'Prostat Kanseri',
          lastVisit: '2024-12-23',
          status: 'followup'
        }
      ];

      const mockMetrics = [
        {
          name: 'Aktif Hasta',
          value: '156',
          change: '+12',
          trend: 'up',
          color: 'text-green-600'
        },
        {
          name: 'Bugünkü İşlem',
          value: '23',
          change: '+5',
          trend: 'up',
          color: 'text-blue-600'
        },
        {
          name: 'SUV Analizi',
          value: '89',
          change: '+8',
          trend: 'up',
          color: 'text-purple-600'
        },
        {
          name: 'PICO Raporu',
          value: '34',
          change: '+3',
          trend: 'up',
          color: 'text-indigo-600'
        }
      ];

      setRecentPatients(mockPatients);
      setSystemMetrics(mockMetrics);
    } catch (error) {
      console.error('Dashboard data fetch error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchGeminiAIStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/gemini/info');
      if (response.ok) {
        const data = await response.json();
        setGeminiAIStatus({
          status: 'active',
          version: data.data.version || '1.0.0',
          lastUpdate: new Date().toLocaleDateString('tr-TR'),
          aiConclusions: Math.floor(Math.random() * 100) + 50, // Mock data
          accuracy: '95.2%'
        });
      }
    } catch (error) {
      console.error('Gemini AI status fetch error:', error);
      setGeminiAIStatus(prev => ({ ...prev, status: 'error' }));
    }
  };

  const quickActions: QuickAction[] = [
    {
      id: 'new-patient',
      title: 'Yeni Hasta',
      description: 'Yeni hasta kaydı oluştur',
      icon: '👤',
      color: 'bg-blue-500 hover:bg-blue-600',
      action: () => alert('Yeni hasta ekleme özelliği')
    },
    {
      id: 'dicom-upload',
      title: 'DICOM Yükle',
      description: 'Görüntü dosyası yükle',
      icon: '🖼️',
      color: 'bg-green-500 hover:bg-green-600',
      action: () => alert('DICOM yükleme özelliği')
    },
    {
      id: 'suv-analysis',
      title: 'SUV Analizi',
      description: 'SUV trend analizi yap',
      icon: '📊',
      color: 'bg-purple-500 hover:bg-purple-600',
      action: () => alert('SUV analizi özelliği')
    },
    {
      id: 'pico-report',
      title: 'PICO Raporu',
      description: 'Kanıta dayalı rapor oluştur',
      icon: '🔬',
      color: 'bg-indigo-500 hover:bg-indigo-600',
      action: () => alert('PICO raporu özelliği')
    },
    {
      id: 'evidence-search',
      title: 'Kanıt Ara',
      description: 'Literatür taraması yap',
      icon: '📚',
      color: 'bg-orange-500 hover:bg-orange-600',
      action: () => alert('Kanıt arama özelliği')
    },
    {
      id: 'system-monitor',
      title: 'Sistem Durumu',
      description: 'Performans metriklerini gör',
      icon: '⚡',
      color: 'bg-red-500 hover:bg-red-600',
      action: () => alert('Sistem monitörü özelliği')
    },
    {
      id: 'gemini-ai',
      title: 'Gemini AI Studio',
      description: 'AI destekli karar verme',
      icon: '🤖',
      color: 'bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600',
      action: () => setShowGeminiAI(true)
    }
  ];

  if (isLoading) {
    return (
      <div className="min-h-screen bg-medical-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-medical-600 mx-auto mb-4"></div>
          <p className="text-medical-600 text-lg">Dashboard yükleniyor...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-medical-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Welcome Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-medical-900 mb-2">
            🧠 NeuroPETrix Dashboard
          </h1>
          <p className="text-xl text-medical-600">
            Hoş geldiniz! PET/CT görüntüleme ve AI destekli klinik karar süreçlerinizi yönetin
          </p>
          <div className="mt-4 p-4 bg-medical-100 rounded-lg">
            <p className="text-medical-700">
              <strong>Son Giriş:</strong> {new Date().toLocaleDateString('tr-TR')} - 
              <strong> Sistem Durumu:</strong> <span className="text-green-600">✅ Aktif</span>
            </p>
          </div>
        </div>

        {/* System Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {systemMetrics.map((metric) => (
            <div key={metric.name} className="bg-white rounded-xl shadow-sm border border-medical-200 p-6 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-medical-600">{metric.name}</p>
                  <p className="text-2xl font-bold text-medical-900">{metric.value}</p>
                </div>
                <div className={`text-2xl ${metric.color}`}>
                  {metric.trend === 'up' ? '📈' : metric.trend === 'down' ? '📉' : '➡️'}
                </div>
              </div>
              <div className="mt-2">
                <span className={`text-sm font-medium ${metric.color}`}>
                  {metric.change} bu hafta
                </span>
              </div>
            </div>
          ))}
        </div>

        {/* Gemini AI Studio Status */}
        <div className="mb-8">
          <div className="bg-gradient-to-r from-purple-50 to-pink-50 border border-purple-200 rounded-xl p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-2xl font-bold text-purple-900 flex items-center">
                🤖 Gemini AI Studio
                <span className={`ml-3 px-3 py-1 rounded-full text-xs font-medium ${
                  geminiAIStatus.status === 'active' ? 'bg-green-100 text-green-800' :
                  geminiAIStatus.status === 'error' ? 'bg-red-100 text-red-800' :
                  'bg-yellow-100 text-yellow-800'
                }`}>
                  {geminiAIStatus.status === 'active' ? 'Aktif' :
                   geminiAIStatus.status === 'error' ? 'Hata' : 'Pasif'}
                </span>
              </h2>
              <div className="text-right">
                <p className="text-sm text-purple-600">Versiyon: {geminiAIStatus.version}</p>
                <p className="text-sm text-purple-600">Son Güncelleme: {geminiAIStatus.lastUpdate}</p>
              </div>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <p className="text-2xl font-bold text-purple-900">{geminiAIStatus.aiConclusions}</p>
                <p className="text-sm text-purple-600">AI Sonucu</p>
              </div>
              <div className="text-center">
                <p className="text-2xl font-bold text-purple-900">{geminiAIStatus.accuracy}</p>
                <p className="text-sm text-purple-600">Doğruluk</p>
              </div>
              <div className="text-center">
                <button 
                  className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
                  onClick={() => alert('Gemini AI Studio detayları')}
                >
                  Detayları Gör
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* AI Manager Status */}
        {aiManagerStatus && (
          <div className="mb-8">
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-2xl font-bold text-blue-900 flex items-center">
                  🧠 AI Manager
                  <span className="ml-2 text-sm bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                    {aiManagerStatus.available_modules}/{aiManagerStatus.total_modules} Modül Aktif
                  </span>
                </h2>
                <div className="text-sm text-blue-600">
                  Sistem Sağlığı: {Math.round((aiManagerStatus.available_modules / aiManagerStatus.total_modules) * 100)}%
                </div>
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                {Object.entries(aiManagerStatus.modules).map(([moduleName, module]) => (
                  <div key={moduleName} className="bg-white rounded-lg p-4 border border-blue-100">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-semibold text-blue-900 capitalize">
                        {moduleName.replace('_', ' ')}
                      </h3>
                      <span className={`w-3 h-3 rounded-full ${
                        module.available ? 'bg-green-500' : 'bg-red-500'
                      }`}></span>
                    </div>
                    <div className="text-xs text-blue-600 mb-2">
                      {module.capabilities.length} yetenek
                    </div>
                    <div className="text-xs text-gray-500">
                      {module.last_used ? 
                        `Son kullanım: ${new Date(module.last_used).toLocaleDateString('tr-TR')}` : 
                        'Henüz kullanılmadı'
                      }
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="bg-white rounded-xl shadow-sm border border-medical-200 p-6 mb-8">
          <h2 className="text-2xl font-bold text-medical-900 mb-6">🚀 Hızlı İşlemler</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {quickActions.map((action) => (
              <button
                key={action.id}
                onClick={action.action}
                className={`${action.color} text-white p-6 rounded-xl text-left transition-all duration-200 hover:scale-105 hover:shadow-lg`}
              >
                <div className="text-3xl mb-3">{action.icon}</div>
                <h3 className="text-lg font-semibold mb-2">{action.title}</h3>
                <p className="text-sm opacity-90">{action.description}</p>
              </button>
            ))}
          </div>
        </div>

        {/* Recent Patients & Current Case */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Recent Patients */}
          <div className="bg-white rounded-xl shadow-sm border border-medical-200 p-6">
            <h2 className="text-2xl font-bold text-medical-900 mb-6">👥 Son Hastalar</h2>
            <div className="space-y-4">
              {recentPatients.map((patient) => (
                <div key={patient.id} className="flex items-center justify-between p-4 bg-medical-50 rounded-lg hover:bg-medical-100 transition-colors">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 bg-medical-200 rounded-full flex items-center justify-center">
                      <span className="text-medical-600 font-medium">
                        {patient.name.charAt(0)}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium text-medical-900">{patient.name}</p>
                      <p className="text-sm text-medical-600">
                        {patient.age} yaş, {patient.gender} • {patient.diagnosis}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-medical-600">{patient.lastVisit}</p>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      patient.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-blue-100 text-blue-800'
                    }`}>
                      {patient.status === 'active' ? 'Aktif' : 'Takip'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
            <button className="w-full mt-4 bg-medical-100 text-medical-700 py-2 rounded-lg hover:bg-medical-200 transition-colors">
              Tüm Hastaları Gör →
            </button>
          </div>

          {/* Current Case */}
          <div className="bg-white rounded-xl shadow-sm border border-medical-200 p-6">
            <h2 className="text-2xl font-bold text-medical-900 mb-6">📋 Aktif Vaka</h2>
            {selectedCase ? (
              <div className="space-y-4">
                <div className="p-4 bg-medical-50 rounded-lg">
                  <h3 className="font-semibold text-medical-900 mb-2">
                    {selectedCase.patient?.name || 'Bilinmeyen Hasta'}
                  </h3>
                  <div className="grid grid-cols-2 gap-2 text-sm">
                    <div>
                      <span className="text-medical-600">Vaka ID:</span>
                      <p className="font-medium text-medical-900">{selectedCase.id}</p>
                    </div>
                    <div>
                      <span className="text-medical-600">Durum:</span>
                      <p className="font-medium text-medical-900">{selectedCase.status}</p>
                    </div>
                    <div>
                      <span className="text-medical-600">Oluşturulma:</span>
                      <p className="font-medium text-medical-900">
                        {new Date(selectedCase.created_at).toLocaleDateString('tr-TR')}
                      </p>
                    </div>
                    <div>
                      <span className="text-medical-600">Son Güncelleme:</span>
                      <p className="font-medium text-medical-900">
                        {new Date(selectedCase.updated_at).toLocaleDateString('tr-TR')}
                      </p>
                    </div>
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-3">
                  <button className="bg-medical-600 text-white py-2 px-4 rounded-lg hover:bg-medical-700 transition-colors">
                    Vaka Detayı
                  </button>
                  <button className="bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition-colors">
                    Rapor Oluştur
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <div className="text-4xl mb-4">📋</div>
                <p className="text-medical-600 mb-4">Henüz aktif vaka seçilmedi</p>
                <button className="bg-medical-600 text-white py-2 px-6 rounded-lg hover:bg-medical-700 transition-colors">
                  Vaka Seç
                </button>
              </div>
            )}
          </div>
        </div>

        {/* System Status & Quick Tips */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* System Status */}
          <div className="bg-white rounded-xl shadow-sm border border-medical-200 p-6">
            <h2 className="text-2xl font-bold text-medical-900 mb-6">⚡ Sistem Durumu</h2>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <span className="text-green-700">Backend API</span>
                <span className="text-green-600">✅ Çalışıyor</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <span className="text-green-700">Veritabanı</span>
                <span className="text-green-600">✅ Bağlı</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <span className="text-green-700">AI Servisleri</span>
                <span className="text-green-600">✅ Aktif</span>
              </div>
              <div className="flex items-center justify-between p-3 bg-green-50 rounded-lg">
                <span className="text-green-700">DICOM İşleme</span>
                <span className="text-green-600">✅ Hazır</span>
              </div>
            </div>
          </div>

          {/* Quick Tips */}
          <div className="bg-white rounded-xl shadow-sm border border-medical-200 p-6">
            <h2 className="text-2xl font-bold text-medical-900 mb-6">💡 Hızlı İpuçları</h2>
            <div className="space-y-3">
              <div className="flex items-start space-x-3">
                <span className="text-blue-500 text-lg">💡</span>
                <p className="text-sm text-medical-700">
                  <strong>DICOM Yükleme:</strong> .dcm uzantılı dosyaları sürükleyip bırakabilirsiniz
                </p>
              </div>
              <div className="flex items-start space-x-3">
                <span className="text-green-500 text-lg">💡</span>
                <p className="text-sm text-medical-700">
                  <strong>SUV Analizi:</strong> PERCIST kriterleri otomatik olarak uygulanır
                </p>
              </div>
              <div className="flex items-start space-x-3">
                <span className="text-purple-500 text-lg">💡</span>
                <p className="text-sm text-medical-700">
                  <strong>PICO Otomasyonu:</strong> 5 adımlı süreç ile kanıta dayalı raporlar
                </p>
              </div>
              <div className="flex items-start space-x-3">
                <span className="text-orange-500 text-lg">💡</span>
                <p className="text-sm text-medical-700">
                  <strong>Klavye Kısayolları:</strong> Ctrl+K ile hızlı arama yapabilirsiniz
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center">
          <p className="text-medical-500 text-sm">
            NeuroPETrix v1.0.0 • AI Destekli PET/CT Görüntüleme ve Klinik Karar Sistemi
          </p>
          <p className="text-medical-400 text-xs mt-2">
            © 2024 NeuroPETrix. Tüm hakları saklıdır.
          </p>
        </div>
      </div>

      {/* Gemini AI Studio Modal */}
      {showGeminiAI && (
        <GeminiAIStudio onClose={() => setShowGeminiAI(false)} />
      )}
    </div>
  );
}


