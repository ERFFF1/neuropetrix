import React, { useState, useEffect } from 'react';

interface SystemMetrics {
  timestamp: string;
  cpu_percent: number;
  memory_percent: number;
  disk_percent: number;
  network_io: {
    bytes_sent: number;
    bytes_recv: number;
    packets_sent: number;
    packets_recv: number;
  };
  active_connections: number;
  uptime_seconds: number;
}

interface PerformanceMetrics {
  api_response_times: Record<string, number>;
  request_counts: Record<string, number>;
  error_rates: Record<string, number>;
  throughput_per_second: number;
}

interface HealthStatus {
  status: string;
  services: Record<string, string>;
  last_check: string;
  uptime: string;
}

interface Alert {
  type: 'warning' | 'critical' | 'info';
  message: string;
  timestamp: string;
}

export default function SystemMonitoring() {
  const [systemMetrics, setSystemMetrics] = useState<SystemMetrics | null>(null);
  const [performanceMetrics, setPerformanceMetrics] = useState<PerformanceMetrics | null>(null);
  const [healthStatus, setHealthStatus] = useState<HealthStatus | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchMetrics = async () => {
    try {
      const [systemRes, performanceRes, healthRes, alertsRes] = await Promise.all([
        fetch('http://localhost:8000/monitoring/system-metrics'),
        fetch('http://localhost:8000/monitoring/performance-metrics'),
        fetch('http://localhost:8000/monitoring/health-status'),
        fetch('http://localhost:8000/monitoring/alerts')
      ]);

      if (systemRes.ok) {
        const systemData = await systemRes.json();
        setSystemMetrics(systemData);
      }

      if (performanceRes.ok) {
        const performanceData = await performanceRes.json();
        setPerformanceMetrics(performanceData);
      }

      if (healthRes.ok) {
        const healthData = await healthRes.json();
        setHealthStatus(healthData);
      }

      if (alertsRes.ok) {
        const alertsData = await alertsRes.json();
        setAlerts(alertsData.alerts || []);
      }

      setIsLoading(false);
    } catch (error) {
      console.error('Metrikler alınırken hata:', error);
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchMetrics();
    
    if (autoRefresh) {
      const interval = setInterval(fetchMetrics, 5000); // 5 saniyede bir güncelle
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy': return 'text-green-600 bg-green-100';
      case 'warning': return 'text-yellow-600 bg-yellow-100';
      case 'critical': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getAlertColor = (type: string) => {
    switch (type) {
      case 'critical': return 'border-red-500 bg-red-50';
      case 'warning': return 'border-yellow-500 bg-yellow-50';
      case 'info': return 'border-blue-500 bg-blue-50';
      default: return 'border-gray-500 bg-gray-50';
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-medical-50">
        <div className="text-medical-700 text-xl">Sistem metrikleri yükleniyor...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-medical-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-4xl font-bold text-medical-900 mb-2">
                📊 Sistem Monitörü
              </h1>
              <p className="text-xl text-medical-600">
                Real-time sistem performansı ve sağlık durumu
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={autoRefresh}
                  onChange={(e) => setAutoRefresh(e.target.checked)}
                  className="mr-2"
                />
                <span className="text-medical-700">Otomatik yenile</span>
              </label>
              <button
                onClick={fetchMetrics}
                className="px-4 py-2 bg-medical-600 text-white rounded-lg hover:bg-medical-700"
              >
                🔄 Yenile
              </button>
            </div>
          </div>
        </div>

        {/* Alerts */}
        {alerts.length > 0 && (
          <div className="mb-6">
            <h2 className="text-2xl font-bold text-medical-900 mb-4">🚨 Sistem Uyarıları</h2>
            <div className="grid gap-4">
              {alerts.map((alert, index) => (
                <div
                  key={index}
                  className={`p-4 rounded-lg border-l-4 ${getAlertColor(alert.type)}`}
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="font-semibold">{alert.message}</p>
                      <p className="text-sm text-gray-600">
                        {new Date(alert.timestamp).toLocaleString('tr-TR')}
                      </p>
                    </div>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(alert.type)}`}>
                      {alert.type.toUpperCase()}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* System Metrics */}
        {systemMetrics && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-medical-900 mb-4">💻 Sistem Kaynakları</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-xl shadow-sm border border-medical-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-medical-600">CPU Kullanımı</p>
                    <p className="text-2xl font-bold text-medical-900">{systemMetrics.cpu_percent.toFixed(1)}%</p>
                  </div>
                  <div className="text-3xl">🖥️</div>
                </div>
                <div className="mt-4">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${systemMetrics.cpu_percent > 80 ? 'bg-red-500' : systemMetrics.cpu_percent > 60 ? 'bg-yellow-500' : 'bg-green-500'}`}
                      style={{ width: `${systemMetrics.cpu_percent}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-sm border border-medical-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-medical-600">Bellek Kullanımı</p>
                    <p className="text-2xl font-bold text-medical-900">{systemMetrics.memory_percent.toFixed(1)}%</p>
                  </div>
                  <div className="text-3xl">🧠</div>
                </div>
                <div className="mt-4">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${systemMetrics.memory_percent > 85 ? 'bg-red-500' : systemMetrics.memory_percent > 70 ? 'bg-yellow-500' : 'bg-green-500'}`}
                      style={{ width: `${systemMetrics.memory_percent}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-sm border border-medical-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-medical-600">Disk Kullanımı</p>
                    <p className="text-2xl font-bold text-medical-900">{systemMetrics.disk_percent.toFixed(1)}%</p>
                  </div>
                  <div className="text-3xl">💾</div>
                </div>
                <div className="mt-4">
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${systemMetrics.disk_percent > 90 ? 'bg-red-500' : systemMetrics.disk_percent > 80 ? 'bg-yellow-500' : 'bg-green-500'}`}
                      style={{ width: `${systemMetrics.disk_percent}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-sm border border-medical-200 p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-medical-600">Aktif Bağlantılar</p>
                    <p className="text-2xl font-bold text-medical-900">{systemMetrics.active_connections}</p>
                  </div>
                  <div className="text-3xl">🌐</div>
                </div>
                <div className="mt-4">
                  <p className="text-sm text-gray-600">
                    Uptime: {Math.floor(systemMetrics.uptime_seconds / 3600)}h {Math.floor((systemMetrics.uptime_seconds % 3600) / 60)}m
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Performance Metrics */}
        {performanceMetrics && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-medical-900 mb-4">⚡ API Performansı</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white rounded-xl shadow-sm border border-medical-200 p-6">
                <h3 className="text-lg font-semibold text-medical-900 mb-4">Yanıt Süreleri (ms)</h3>
                <div className="space-y-3">
                  {Object.entries(performanceMetrics.api_response_times).map(([endpoint, time]) => (
                    <div key={endpoint} className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">{endpoint}</span>
                      <span className="font-medium">{time.toFixed(1)}ms</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="bg-white rounded-xl shadow-sm border border-medical-200 p-6">
                <h3 className="text-lg font-semibold text-medical-900 mb-4">İstek Sayıları</h3>
                <div className="space-y-3">
                  {Object.entries(performanceMetrics.request_counts).map(([endpoint, count]) => (
                    <div key={endpoint} className="flex justify-between items-center">
                      <span className="text-sm text-gray-600">{endpoint}</span>
                      <span className="font-medium">{count}</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Health Status */}
        {healthStatus && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold text-medical-900 mb-4">🏥 Servis Sağlığı</h2>
            <div className="bg-white rounded-xl shadow-sm border border-medical-200 p-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {Object.entries(healthStatus.services).map(([service, status]) => (
                  <div key={service} className="flex items-center justify-between p-3 rounded-lg bg-gray-50">
                    <span className="font-medium text-gray-700">{service}</span>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(status)}`}>
                      {status.toUpperCase()}
                    </span>
                  </div>
                ))}
              </div>
              <div className="mt-4 pt-4 border-t border-gray-200">
                <p className="text-sm text-gray-600">
                  Son kontrol: {new Date(healthStatus.last_check).toLocaleString('tr-TR')}
                </p>
                <p className="text-sm text-gray-600">
                  Sistem uptime: {healthStatus.uptime}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
