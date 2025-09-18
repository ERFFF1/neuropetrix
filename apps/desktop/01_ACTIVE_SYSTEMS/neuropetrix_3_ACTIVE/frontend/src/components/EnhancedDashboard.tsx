import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { 
  Activity, 
  Users, 
  FileText, 
  TrendingUp, 
  Clock, 
  CheckCircle,
  AlertCircle,
  BarChart3,
  PieChart,
  LineChart,
  Calendar,
  Filter,
  Download,
  RefreshCw
} from 'lucide-react';

interface DashboardStats {
  totalPatients: number;
  activeCases: number;
  completedReports: number;
  pendingTasks: number;
  systemHealth: 'healthy' | 'warning' | 'error';
  lastUpdate: string;
}

interface RecentActivity {
  id: string;
  type: 'patient' | 'report' | 'analysis' | 'system';
  title: string;
  description: string;
  timestamp: string;
  status: 'completed' | 'pending' | 'error';
}

interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string;
    borderColor?: string;
  }[];
}

const EnhancedDashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats>({
    totalPatients: 0,
    activeCases: 0,
    completedReports: 0,
    pendingTasks: 0,
    systemHealth: 'healthy',
    lastUpdate: new Date().toISOString()
  });

  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [chartData, setChartData] = useState<ChartData | null>(null);
  const [loading, setLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(true);

  const fetchDashboardData = async () => {
    try {
      // Mock data - gerçek implementasyonda API'den gelecek
      setStats({
        totalPatients: 1247,
        activeCases: 23,
        completedReports: 89,
        pendingTasks: 5,
        systemHealth: 'healthy',
        lastUpdate: new Date().toISOString()
      });

      setRecentActivity([
        {
          id: '1',
          type: 'patient',
          title: 'Yeni Hasta Kaydı',
          description: 'Ahmet Yılmaz - PET/CT Analizi',
          timestamp: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
          status: 'completed'
        },
        {
          id: '2',
          type: 'report',
          title: 'Rapor Tamamlandı',
          description: 'SUV Trend Analizi - Vaka #1234',
          timestamp: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
          status: 'completed'
        },
        {
          id: '3',
          type: 'analysis',
          title: 'AI Analizi',
          description: 'DICOM Görüntü Analizi - %95 güven',
          timestamp: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
          status: 'completed'
        },
        {
          id: '4',
          type: 'system',
          title: 'Sistem Güncellemesi',
          description: 'Performance optimizasyonu tamamlandı',
          timestamp: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
          status: 'completed'
        },
        {
          id: '5',
          type: 'patient',
          title: 'Bekleyen Analiz',
          description: 'Mehmet Kaya - PET/CT Beklemede',
          timestamp: new Date(Date.now() - 1000 * 60 * 60).toISOString(),
          status: 'pending'
        }
      ]);

      // Mock chart data
      setChartData({
        labels: ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran'],
        datasets: [
          {
            label: 'Hasta Sayısı',
            data: [120, 135, 142, 158, 167, 180],
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            borderColor: 'rgba(59, 130, 246, 1)'
          },
          {
            label: 'Tamamlanan Raporlar',
            data: [95, 108, 115, 132, 145, 158],
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            borderColor: 'rgba(16, 185, 129, 1)'
          }
        ]
      });

      setLoading(false);
    } catch (error) {
      console.error('Dashboard data fetch error:', error);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();

    if (autoRefresh) {
      const interval = setInterval(fetchDashboardData, 30000); // 30 saniyede bir
      return () => clearInterval(interval);
    }
  }, [autoRefresh]);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'pending': return <Clock className="h-4 w-4 text-yellow-500" />;
      case 'error': return <AlertCircle className="h-4 w-4 text-red-500" />;
      default: return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-100 text-green-800';
      case 'pending': return 'bg-yellow-100 text-yellow-800';
      case 'error': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'patient': return <Users className="h-4 w-4" />;
      case 'report': return <FileText className="h-4 w-4" />;
      case 'analysis': return <BarChart3 className="h-4 w-4" />;
      case 'system': return <Activity className="h-4 w-4" />;
      default: return <Activity className="h-4 w-4" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin" />
        <span className="ml-2">Dashboard yükleniyor...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Gelişmiş Dashboard</h1>
          <p className="text-gray-600">NeuroPETRIX Sistem Genel Bakış</p>
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
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Rapor İndir
          </Button>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Toplam Hasta</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.totalPatients.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              <TrendingUp className="inline h-3 w-3 mr-1" />
              +12% bu ay
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Aktif Vakalar</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.activeCases}</div>
            <p className="text-xs text-muted-foreground">
              <TrendingUp className="inline h-3 w-3 mr-1" />
              +3 bu hafta
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tamamlanan Raporlar</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.completedReports}</div>
            <p className="text-xs text-muted-foreground">
              <TrendingUp className="inline h-3 w-3 mr-1" />
              +8 bu hafta
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Bekleyen Görevler</CardTitle>
            <Clock className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{stats.pendingTasks}</div>
            <p className="text-xs text-muted-foreground">
              Ortalama 2 saat
            </p>
          </CardContent>
        </Card>
      </div>

      {/* System Health */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            Sistem Sağlığı
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center gap-4">
            <Badge className={`${
              stats.systemHealth === 'healthy' ? 'bg-green-500' : 
              stats.systemHealth === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
            } text-white`}>
              {stats.systemHealth === 'healthy' ? 'Sağlıklı' : 
               stats.systemHealth === 'warning' ? 'Uyarı' : 'Hata'}
            </Badge>
            <span className="text-sm text-gray-600">
              Son güncelleme: {new Date(stats.lastUpdate).toLocaleString()}
            </span>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="overview" className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Genel Bakış</TabsTrigger>
          <TabsTrigger value="activity">Son Aktiviteler</TabsTrigger>
          <TabsTrigger value="analytics">Analitik</TabsTrigger>
          <TabsTrigger value="reports">Raporlar</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Son Aktiviteler
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {recentActivity.slice(0, 5).map((activity) => (
                    <div key={activity.id} className="flex items-start gap-3 p-3 rounded-lg border">
                      <div className="flex-shrink-0 mt-1">
                        {getTypeIcon(activity.type)}
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium truncate">
                            {activity.title}
                          </p>
                          <Badge className={`text-xs ${getStatusColor(activity.status)}`}>
                            {activity.status === 'completed' ? 'Tamamlandı' : 
                             activity.status === 'pending' ? 'Beklemede' : 'Hata'}
                          </Badge>
                        </div>
                        <p className="text-xs text-gray-600 mt-1">
                          {activity.description}
                        </p>
                        <p className="text-xs text-gray-500 mt-1">
                          {new Date(activity.timestamp).toLocaleString()}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Quick Actions */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <BarChart3 className="h-5 w-5" />
                  Hızlı İşlemler
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 gap-3">
                  <Button className="h-20 flex flex-col items-center justify-center">
                    <Users className="h-6 w-6 mb-2" />
                    <span className="text-sm">Yeni Hasta</span>
                  </Button>
                  <Button variant="outline" className="h-20 flex flex-col items-center justify-center">
                    <FileText className="h-6 w-6 mb-2" />
                    <span className="text-sm">Rapor Oluştur</span>
                  </Button>
                  <Button variant="outline" className="h-20 flex flex-col items-center justify-center">
                    <BarChart3 className="h-6 w-6 mb-2" />
                    <span className="text-sm">Analiz Başlat</span>
                  </Button>
                  <Button variant="outline" className="h-20 flex flex-col items-center justify-center">
                    <Calendar className="h-6 w-6 mb-2" />
                    <span className="text-sm">Randevu</span>
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="activity" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center justify-between">
                <span className="flex items-center gap-2">
                  <Activity className="h-5 w-5" />
                  Tüm Aktiviteler
                </span>
                <div className="flex gap-2">
                  <Button variant="outline" size="sm">
                    <Filter className="h-4 w-4 mr-2" />
                    Filtrele
                  </Button>
                  <Button variant="outline" size="sm">
                    <Download className="h-4 w-4 mr-2" />
                    İndir
                  </Button>
                </div>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {recentActivity.map((activity) => (
                  <div key={activity.id} className="flex items-start gap-3 p-4 rounded-lg border hover:bg-gray-50">
                    <div className="flex-shrink-0 mt-1">
                      {getTypeIcon(activity.type)}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium">
                          {activity.title}
                        </p>
                        <div className="flex items-center gap-2">
                          {getStatusIcon(activity.status)}
                          <Badge className={`text-xs ${getStatusColor(activity.status)}`}>
                            {activity.status === 'completed' ? 'Tamamlandı' : 
                             activity.status === 'pending' ? 'Beklemede' : 'Hata'}
                          </Badge>
                        </div>
                      </div>
                      <p className="text-sm text-gray-600 mt-1">
                        {activity.description}
                      </p>
                      <p className="text-xs text-gray-500 mt-2">
                        {new Date(activity.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="analytics" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <LineChart className="h-5 w-5" />
                  Aylık Trend
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
                  <div className="text-center">
                    <BarChart3 className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                    <p className="text-gray-500">Grafik verisi yükleniyor...</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChart className="h-5 w-5" />
                  Dağılım
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg">
                  <div className="text-center">
                    <PieChart className="h-12 w-12 mx-auto text-gray-400 mb-2" />
                    <p className="text-gray-500">Pasta grafik yükleniyor...</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="reports" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Raporlar
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                  <h4 className="font-semibold mb-2">Günlük Rapor</h4>
                  <p className="text-sm text-gray-600 mb-3">Günlük sistem aktiviteleri</p>
                  <Button size="sm" variant="outline">İndir</Button>
                </div>
                <div className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                  <h4 className="font-semibold mb-2">Haftalık Rapor</h4>
                  <p className="text-sm text-gray-600 mb-3">Haftalık performans özeti</p>
                  <Button size="sm" variant="outline">İndir</Button>
                </div>
                <div className="p-4 border rounded-lg hover:bg-gray-50 cursor-pointer">
                  <h4 className="font-semibold mb-2">Aylık Rapor</h4>
                  <p className="text-sm text-gray-600 mb-3">Aylık detaylı analiz</p>
                  <Button size="sm" variant="outline">İndir</Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default EnhancedDashboard;
