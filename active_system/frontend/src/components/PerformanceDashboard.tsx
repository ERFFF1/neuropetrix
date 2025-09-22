import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Activity, 
  Cpu, 
  HardDrive, 
  Network, 
  Zap, 
  TrendingUp, 
  TrendingDown,
  RefreshCw,
  Settings
} from 'lucide-react';

interface PerformanceMetrics {
  timestamp: string;
  cpu_percent: number;
  memory_percent: number;
  memory_used_mb: number;
  memory_available_mb: number;
  disk_usage_percent: number;
  network_io: {
    bytes_sent: number;
    bytes_recv: number;
    packets_sent: number;
    packets_recv: number;
  };
  active_connections: number;
  response_time_ms: number;
  requests_per_second: number;
  cache_hit_rate: number;
  gc_collections: number;
}

interface PerformanceSummary {
  status: string;
  current: {
    cpu_percent: number;
    memory_percent: number;
    response_time_ms: number;
    requests_per_second: number;
    cache_hit_rate: number;
  };
  averages: {
    cpu_percent: number;
    memory_percent: number;
    response_time_ms: number;
  };
  optimization_enabled: boolean;
  last_optimization: number;
}

const PerformanceDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [summary, setSummary] = useState<PerformanceSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchMetrics = async () => {
    try {
      const response = await fetch('http://localhost:8000/performance/metrics');
      if (response.ok) {
        const data = await response.json();
        setMetrics(data);
      }
    } catch (error) {
      console.error('Metrics fetch error:', error);
    }
  };

  const fetchSummary = async () => {
    try {
      const response = await fetch('http://localhost:8000/performance/summary');
      if (response.ok) {
        const data = await response.json();
        setSummary(data);
      }
    } catch (error) {
      console.error('Summary fetch error:', error);
    }
  };

  const optimizeMemory = async () => {
    try {
      await fetch('http://localhost:8000/performance/optimize/memory', {
        method: 'POST'
      });
      setTimeout(fetchMetrics, 1000);
    } catch (error) {
      console.error('Memory optimization error:', error);
    }
  };

  const optimizeCPU = async () => {
    try {
      await fetch('http://localhost:8000/performance/optimize/cpu', {
        method: 'POST'
      });
      setTimeout(fetchMetrics, 1000);
    } catch (error) {
      console.error('CPU optimization error:', error);
    }
  };

  const autoOptimize = async () => {
    try {
      await fetch('http://localhost:8000/performance/optimize/auto', {
        method: 'POST'
      });
      setTimeout(fetchMetrics, 1000);
    } catch (error) {
      console.error('Auto optimization error:', error);
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchMetrics(), fetchSummary()]);
      setLoading(false);
    };

    loadData();

    if (autoRefresh) {
      const interval = setInterval(loadData, 5000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-500';
      case 'warning': return 'bg-yellow-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'healthy': return 'Sağlıklı';
      case 'warning': return 'Uyarı';
      case 'error': return 'Hata';
      default: return 'Bilinmiyor';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin" />
        <span className="ml-2">Performans verileri yükleniyor...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Performans Dashboard</h1>
          <p className="text-gray-600">Sistem performansı ve optimizasyon</p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => setAutoRefresh(!autoRefresh)}
            className={autoRefresh ? 'bg-green-50' : ''}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${autoRefresh ? 'animate-spin' : ''}`} />
            {autoRefresh ? 'Otomatik Yenileme' : 'Manuel Yenileme'}
          </Button>
          <Button onClick={autoOptimize} className="bg-blue-600 hover:bg-blue-700">
            <Zap className="h-4 w-4 mr-2" />
            Otomatik Optimize Et
          </Button>
        </div>
      </div>

      {/* Status Overview */}
      {summary && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Activity className="h-5 w-5" />
              Sistem Durumu
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <Badge className={`${getStatusColor(summary.status)} text-white`}>
                {getStatusText(summary.status)}
              </Badge>
              <span className="text-sm text-gray-600">
                Son optimizasyon: {new Date(summary.last_optimization * 1000).toLocaleString()}
              </span>
              <Badge variant="outline">
                {summary.optimization_enabled ? 'Optimizasyon Aktif' : 'Optimizasyon Pasif'}
              </Badge>
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Genel Bakış</TabsTrigger>
          <TabsTrigger value="resources">Kaynak Kullanımı</TabsTrigger>
          <TabsTrigger value="network">Ağ ve Bağlantılar</TabsTrigger>
          <TabsTrigger value="optimization">Optimizasyon</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {/* CPU */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">CPU Kullanımı</CardTitle>
                <Cpu className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {metrics?.cpu_percent.toFixed(1)}%
                </div>
                <Progress value={metrics?.cpu_percent || 0} className="mt-2" />
                <p className="text-xs text-muted-foreground mt-1">
                  Ortalama: {summary?.averages.cpu_percent.toFixed(1)}%
                </p>
              </CardContent>
            </Card>

            {/* Memory */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Bellek Kullanımı</CardTitle>
                <HardDrive className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {metrics?.memory_percent.toFixed(1)}%
                </div>
                <Progress value={metrics?.memory_percent || 0} className="mt-2" />
                <p className="text-xs text-muted-foreground mt-1">
                  {metrics?.memory_used_mb.toFixed(0)} MB / {metrics?.memory_available_mb.toFixed(0)} MB
                </p>
              </CardContent>
            </Card>

            {/* Response Time */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Yanıt Süresi</CardTitle>
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {metrics?.response_time_ms.toFixed(0)}ms
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Ortalama: {summary?.averages.response_time_ms.toFixed(0)}ms
                </p>
              </CardContent>
            </Card>

            {/* Requests per Second */}
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">İstek/Saniye</CardTitle>
                <Network className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {metrics?.requests_per_second.toFixed(1)}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  Aktif bağlantı: {metrics?.active_connections}
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="resources" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Disk Usage */}
            <Card>
              <CardHeader>
                <CardTitle>Disk Kullanımı</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold mb-2">
                  {metrics?.disk_usage_percent.toFixed(1)}%
                </div>
                <Progress value={metrics?.disk_usage_percent || 0} className="mb-2" />
                <p className="text-sm text-gray-600">
                  Sistem disk kullanımı
                </p>
              </CardContent>
            </Card>

            {/* Cache Performance */}
            <Card>
              <CardHeader>
                <CardTitle>Cache Performansı</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="text-3xl font-bold mb-2">
                  {metrics?.cache_hit_rate.toFixed(1)}%
                </div>
                <Progress value={metrics?.cache_hit_rate || 0} className="mb-2" />
                <p className="text-sm text-gray-600">
                  Cache hit rate
                </p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="network" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Ağ İstatistikleri</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <h4 className="font-semibold mb-2">Gönderilen Veri</h4>
                  <p className="text-2xl font-bold">
                    {(metrics?.network_io.bytes_sent || 0 / 1024 / 1024).toFixed(2)} MB
                  </p>
                  <p className="text-sm text-gray-600">
                    {metrics?.network_io.packets_sent} paket
                  </p>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">Alınan Veri</h4>
                  <p className="text-2xl font-bold">
                    {(metrics?.network_io.bytes_recv || 0 / 1024 / 1024).toFixed(2)} MB
                  </p>
                  <p className="text-sm text-gray-600">
                    {metrics?.network_io.packets_recv} paket
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="optimization" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <HardDrive className="h-5 w-5" />
                  Bellek Optimizasyonu
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 mb-4">
                  Garbage collection ve cache temizleme
                </p>
                <Button onClick={optimizeMemory} className="w-full">
                  <Zap className="h-4 w-4 mr-2" />
                  Belleği Optimize Et
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Cpu className="h-5 w-5" />
                  CPU Optimizasyonu
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 mb-4">
                  CPU yoğun işlemleri optimize et
                </p>
                <Button onClick={optimizeCPU} className="w-full">
                  <Zap className="h-4 w-4 mr-2" />
                  CPU'yu Optimize Et
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5" />
                  Sistem Optimizasyonu
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-gray-600 mb-4">
                  Tüm sistem optimizasyonları
                </p>
                <Button onClick={autoOptimize} className="w-full bg-blue-600 hover:bg-blue-700">
                  <Zap className="h-4 w-4 mr-2" />
                  Tümünü Optimize Et
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* GC Statistics */}
          <Card>
            <CardHeader>
              <CardTitle>Garbage Collection İstatistikleri</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">
                {metrics?.gc_collections} koleksiyon
              </div>
              <p className="text-sm text-gray-600">
                Toplam garbage collection sayısı
              </p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default PerformanceDashboard;
