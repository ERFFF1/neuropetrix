import React, { useState } from 'react';
import { 
  PlayIcon, 
  DocumentTextIcon, 
  FolderIcon,
  CogIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon
} from './icons';

interface DesktopRunnerProps {
  className?: string;
}

interface AnalysisResult {
  caseId: string;
  status: 'running' | 'completed' | 'error';
  message: string;
  reportId?: string;
  timestamp: string;
}

const DesktopRunner: React.FC<DesktopRunnerProps> = ({ className = '' }) => {
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState<AnalysisResult[]>([]);
  const [selectedCase, setSelectedCase] = useState('');

  const handleRunAnalysis = async () => {
    if (!selectedCase) return;
    
    setIsRunning(true);
    const newResult: AnalysisResult = {
      caseId: selectedCase,
      status: 'running',
      message: 'Analiz başlatılıyor...',
      timestamp: new Date().toISOString()
    };
    
    setResults(prev => [...prev, newResult]);
    
    try {
      // Gerçek API çağrısı
      const response = await fetch('/api/desktop-runner/run-analysis', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          case_id: selectedCase,
          purpose: 'staging',
          ICD: 'C34.90',
          notes: 'Lung cancer analysis'
        })
      });
      
      if (!response.ok) {
        throw new Error('API call failed');
      }
      
      const data = await response.json();
      
      // Durumu kontrol et
      let status = 'running';
      let message = 'Analiz çalışıyor...';
      let reportId = undefined;
      
      // Durumu periyodik olarak kontrol et
      const checkStatus = async () => {
        try {
          const statusResponse = await fetch(`/api/desktop-runner/status/${selectedCase}`);
          if (statusResponse.ok) {
            const statusData = await statusResponse.json();
            if (statusData.status === 'completed') {
              status = 'completed';
              message = 'Analiz tamamlandı!';
              reportId = statusData.report_id;
              
              // Sonucu güncelle
              const completedResult: AnalysisResult = {
                caseId: selectedCase,
                status: 'completed',
                message: 'Analiz tamamlandı!',
                reportId: reportId,
                timestamp: new Date().toISOString()
              };
              
              setResults(prev => prev.map(r => 
                r.caseId === selectedCase ? completedResult : r
              ));
              
              return true; // Tamamlandı
            }
          }
        } catch (error) {
          console.error('Status check failed:', error);
        }
        return false; // Hala çalışıyor
      };
      
      // Her 2 saniyede bir durumu kontrol et
      const interval = setInterval(async () => {
        const isCompleted = await checkStatus();
        if (isCompleted) {
          clearInterval(interval);
          setIsRunning(false);
        }
      }, 2000);
      
      // 5 dakika sonra timeout
      setTimeout(() => {
        clearInterval(interval);
        if (status === 'running') {
          const timeoutResult: AnalysisResult = {
            caseId: selectedCase,
            status: 'error',
            message: 'Analiz timeout!',
            timestamp: new Date().toISOString()
          };
          
          setResults(prev => prev.map(r => 
            r.caseId === selectedCase ? timeoutResult : r
          ));
          setIsRunning(false);
        }
      }, 300000); // 5 dakika
      
    } catch (error) {
      const errorResult: AnalysisResult = {
        caseId: selectedCase,
        status: 'error',
        message: 'Analiz hatası!',
        timestamp: new Date().toISOString()
      };
      
      setResults(prev => prev.map(r => 
        r.caseId === selectedCase ? errorResult : r
      ));
      setIsRunning(false);
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon className="w-5 h-5 text-green-500" />;
      case 'error':
        return <ExclamationTriangleIcon className="w-5 h-5 text-red-500" />;
      default:
        return <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-50 border-green-200';
      case 'error':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-blue-50 border-blue-200';
    }
  };

  return (
    <div className={`bg-white rounded-lg shadow-lg p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <PlayIcon className="w-8 h-8 text-blue-600" />
          <div>
            <h2 className="text-2xl font-bold text-gray-900">🧠 NeuroPETRIX Desktop</h2>
            <p className="text-gray-600">MONAI + PyRadiomics Pipeline Runner</p>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <CogIcon className="w-5 h-5 text-gray-400" />
          <span className="text-sm text-gray-500">v1.0</span>
        </div>
      </div>

      {/* Case Selection */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Vaka Seçimi
        </label>
        <div className="flex space-x-3">
          <select
            value={selectedCase}
            onChange={(e) => setSelectedCase(e.target.value)}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            disabled={isRunning}
          >
            <option value="">Vaka seçin...</option>
            <option value="NPX-2025-000123">NPX-2025-000123 - Lung Cancer Staging</option>
            <option value="NPX-2025-000124">NPX-2025-000124 - Follow-up</option>
            <option value="NPX-2025-000125">NPX-2025-000125 - Diagnosis</option>
          </select>
          <button
            onClick={handleRunAnalysis}
            disabled={!selectedCase || isRunning}
            className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
          >
            <PlayIcon className="w-4 h-4" />
            <span>{isRunning ? 'Çalışıyor...' : 'Analizi Başlat'}</span>
          </button>
        </div>
      </div>

      {/* Status Display */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-3">Analiz Durumu</h3>
        <div className="space-y-3">
          {results.map((result, index) => (
            <div
              key={index}
              className={`p-4 rounded-lg border ${getStatusColor(result.status)}`}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  {getStatusIcon(result.status)}
                  <div>
                    <p className="font-medium text-gray-900">
                      {result.caseId}
                    </p>
                    <p className="text-sm text-gray-600">
                      {result.message}
                    </p>
                    {result.reportId && (
                      <p className="text-xs text-blue-600 font-mono">
                        {result.reportId}
                      </p>
                    )}
                  </div>
                </div>
                <span className="text-xs text-gray-500">
                  {new Date(result.timestamp).toLocaleTimeString()}
                </span>
              </div>
            </div>
          ))}
          {results.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              <FolderIcon className="w-12 h-12 mx-auto mb-3 text-gray-300" />
              <p>Henüz analiz çalıştırılmadı</p>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <button className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
          <DocumentTextIcon className="w-6 h-6 text-blue-600 mx-auto mb-2" />
          <span className="text-sm font-medium text-gray-900">Raporları Görüntüle</span>
        </button>
        <button className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
          <FolderIcon className="w-6 h-6 text-green-600 mx-auto mb-2" />
          <span className="text-sm font-medium text-gray-900">Çıktı Klasörü</span>
        </button>
        <button className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
          <CogIcon className="w-6 h-6 text-purple-600 mx-auto mb-2" />
          <span className="text-sm font-medium text-gray-900">Ayarlar</span>
        </button>
      </div>

      {/* Info Panel */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h4 className="font-medium text-blue-900 mb-2">ℹ️ Desktop Runner Hakkında</h4>
        <ul className="text-sm text-blue-800 space-y-1">
          <li>• MONAI ile otomatik segmentasyon</li>
          <li>• PyRadiomics ile özellik çıkarma</li>
          <li>• PERCIST ve Deauville kriterleri</li>
          <li>• TSNM standart raporları</li>
          <li>• Tamamen yerel çalışma</li>
        </ul>
      </div>
    </div>
  );
};

export default DesktopRunner;
