import React, { useState, useEffect } from 'react';
import { health, version } from '../services/api';

interface SystemStatus {
  backend: 'healthy' | 'degraded' | 'down';
  frontend: 'healthy' | 'degraded' | 'down';
  lastCheck: string;
}

interface LogEntry {
  timestamp: string;
  level: 'INFO' | 'WARN' | 'ERROR';
  message: string;
}

const SystemMonitor: React.FC = () => {
  const [status, setStatus] = useState<SystemStatus>({
    backend: 'down',
    frontend: 'down',
    lastCheck: 'Hiç kontrol edilmedi'
  });
  const [logs, setLogs] = useState<{
    backend: LogEntry[];
    frontend: LogEntry[];
  }>({
    backend: [],
    frontend: []
  });
  const [activeTab, setActiveTab] = useState<'backend' | 'frontend'>('backend');
  const [isLoading, setIsLoading] = useState(false);

  // Durum kontrolü
  const checkSystemStatus = async () => {
    setIsLoading(true);
    try {
      const healthResult = await health();
      const versionResult = await version();
      
      setStatus({
        backend: 'healthy',
        frontend: 'healthy', // Streamlit varsayılan olarak çalışıyor
        lastCheck: new Date().toLocaleString('tr-TR')
      });
    } catch (error) {
      setStatus({
        backend: 'down',
        frontend: 'down',
        lastCheck: new Date().toLocaleString('tr-TR')
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Log'ları yükle
  const loadLogs = async () => {
    // Mock log verileri (gerçek implementasyonda backend'den gelecek)
    const mockBackendLogs: LogEntry[] = [
      { timestamp: '2024-08-24 15:30:00', level: 'INFO', message: 'Backend başlatıldı' },
      { timestamp: '2024-08-24 15:30:01', level: 'INFO', message: 'Port 8000 dinleniyor' },
      { timestamp: '2024-08-24 15:30:02', level: 'INFO', message: 'Health endpoint aktif' }
    ];
    
    const mockFrontendLogs: LogEntry[] = [
      { timestamp: '2024-08-24 15:30:05', level: 'INFO', message: 'Streamlit başlatıldı' },
      { timestamp: '2024-08-24 15:30:06', level: 'INFO', message: 'Port 8501 dinleniyor' },
      { timestamp: '2024-08-24 15:30:07', level: 'INFO', message: 'Ana sayfa yüklendi' }
    ];

    setLogs({
      backend: mockBackendLogs,
      frontend: mockFrontendLogs
    });
  };

  // Log'ları indir
  const downloadLogs = () => {
    const logContent = logs[activeTab]
      .map(log => `[${log.timestamp}] ${log.level}: ${log.message}`)
      .join('\n');
    
    const blob = new Blob([logContent], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${activeTab}_logs_${new Date().toISOString().split('T')[0]}.txt`;
    a.click();
    URL.revokeObjectURL(url);
  };

  useEffect(() => {
    checkSystemStatus();
    loadLogs();
    
    // Her 30 saniyede bir durum kontrolü
    const interval = setInterval(checkSystemStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-500';
      case 'degraded': return 'bg-yellow-500';
      case 'down': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'healthy': return 'Çalışıyor';
      case 'degraded': return 'Sorunlu';
      case 'down': return 'Kapalı';
      default: return 'Bilinmiyor';
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Başlık */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-800">
            NeuroPETrix — Sistem Durumu
          </h1>
          <p className="text-slate-600 mt-2">
            Backend ve Frontend servislerinin durumu
          </p>
        </div>

        {/* Durum Kartları */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Backend Card */}
          <div className="bg-white rounded-lg shadow-md p-6 border border-slate-200">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-800">Backend</h3>
              <div className={`w-3 h-3 rounded-full ${getStatusColor(status.backend)}`}></div>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-slate-600">Durum:</span>
                <span className={`font-medium ${status.backend === 'healthy' ? 'text-green-600' : status.backend === 'degraded' ? 'text-yellow-600' : 'text-red-600'}`}>
                  {getStatusText(status.backend)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Son Kontrol:</span>
                <span className="text-slate-800">{status.lastCheck}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Port:</span>
                <span className="text-slate-800">8000</span>
              </div>
              <button
                onClick={checkSystemStatus}
                disabled={isLoading}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isLoading ? 'Kontrol Ediliyor...' : 'Test Et'}
              </button>
            </div>
          </div>

          {/* Frontend Card */}
          <div className="bg-white rounded-lg shadow-md p-6 border border-slate-200">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-slate-800">Frontend</h3>
              <div className={`w-3 h-3 rounded-full ${getStatusColor(status.frontend)}`}></div>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between">
                <span className="text-slate-600">Durum:</span>
                <span className={`font-medium ${status.frontend === 'healthy' ? 'text-green-600' : status.frontend === 'degraded' ? 'text-yellow-600' : 'text-red-600'}`}>
                  {getStatusText(status.frontend)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">Port:</span>
                <span className="text-slate-800">8501</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-600">URL:</span>
                <a 
                  href="http://127.0.0.1:8501" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  127.0.0.1:8501
                </a>
              </div>
              <button
                onClick={() => window.open('http://127.0.0.1:8501', '_blank')}
                className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700"
              >
                Yeniden Başlat
              </button>
            </div>
          </div>
        </div>

        {/* Log Sekmeleri */}
        <div className="bg-white rounded-lg shadow-md border border-slate-200">
          <div className="border-b border-slate-200">
            <div className="flex items-center justify-between px-6 py-4">
              <div className="flex space-x-1">
                <button
                  onClick={() => setActiveTab('backend')}
                  className={`px-4 py-2 rounded-md font-medium ${
                    activeTab === 'backend'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-slate-600 hover:text-slate-800'
                  }`}
                >
                  Backend Log
                </button>
                <button
                  onClick={() => setActiveTab('frontend')}
                  className={`px-4 py-2 rounded-md font-medium ${
                    activeTab === 'frontend'
                      ? 'bg-blue-100 text-blue-700'
                      : 'text-slate-600 hover:text-slate-800'
                  }`}
                >
                  Frontend Log
                </button>
              </div>
              <div className="flex space-x-2">
                <button
                  onClick={loadLogs}
                  className="bg-slate-100 text-slate-700 px-3 py-2 rounded-md hover:bg-slate-200"
                >
                  Yenile
                </button>
                <button
                  onClick={downloadLogs}
                  className="bg-blue-600 text-white px-3 py-2 rounded-md hover:bg-blue-700"
                >
                  Logları İndir
                </button>
              </div>
            </div>
          </div>

          <div className="p-6">
            <div className="bg-slate-50 rounded-md p-4 max-h-96 overflow-y-auto">
              {logs[activeTab].length === 0 ? (
                <p className="text-slate-500 text-center py-8">Log bulunamadı</p>
              ) : (
                <div className="space-y-2">
                  {logs[activeTab].map((log, index) => (
                    <div key={index} className="flex items-start space-x-3 text-sm">
                      <span className="text-slate-500 min-w-[120px]">{log.timestamp}</span>
                      <span className={`px-2 py-1 rounded text-xs font-medium ${
                        log.level === 'ERROR' ? 'bg-red-100 text-red-700' :
                        log.level === 'WARN' ? 'bg-yellow-100 text-yellow-700' :
                        'bg-green-100 text-green-700'
                      }`}>
                        {log.level}
                      </span>
                      <span className="text-slate-800 flex-1">{log.message}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SystemMonitor;















