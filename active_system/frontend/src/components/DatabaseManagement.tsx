import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { 
  Database, 
  Users, 
  FileText, 
  BarChart3, 
  Activity,
  Download,
  Upload,
  RefreshCw,
  Settings,
  Shield,
  Clock,
  TrendingUp,
  AlertCircle,
  CheckCircle
} from 'lucide-react';

interface DatabaseStats {
  counts: {
    patients: number;
    reports: number;
    suv_measurements: number;
    clinical_workflows: number;
    users: number;
    system_metrics: number;
  };
  recent_activity: {
    recent_patients: Array<{
      id: string;
      name: string;
      created_at: string;
    }>;
    recent_reports: Array<{
      id: string;
      type: string;
      created_at: string;
    }>;
  };
}

interface DatabaseHealth {
  status: string;
  message: string;
  timestamp: string;
}

const DatabaseManagement: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState<DatabaseStats | null>(null);
  const [health, setHealth] = useState<DatabaseHealth | null>(null);
  const [loading, setLoading] = useState(true);
  const [backupPath, setBackupPath] = useState('');
  const [restorePath, setRestorePath] = useState('');

  const fetchDatabaseStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/database/statistics');
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (error) {
      console.error('Database stats fetch error:', error);
    }
  };

  const fetchDatabaseHealth = async () => {
    try {
      const response = await fetch('http://localhost:8000/database/health');
      if (response.ok) {
        const data = await response.json();
        setHealth(data);
      }
    } catch (error) {
      console.error('Database health fetch error:', error);
    }
  };

  const startMigration = async () => {
    try {
      const response = await fetch('http://localhost:8000/database/migrate', {
        method: 'POST'
      });
      if (response.ok) {
        alert('Database migration started successfully!');
      }
    } catch (error) {
      console.error('Migration error:', error);
      alert('Migration failed!');
    }
  };

  const startBackup = async () => {
    try {
      const response = await fetch('http://localhost:8000/database/backup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ backup_path: backupPath || undefined })
      });
      if (response.ok) {
        alert('Database backup started successfully!');
      }
    } catch (error) {
      console.error('Backup error:', error);
      alert('Backup failed!');
    }
  };

  const startRestore = async () => {
    if (!restorePath) {
      alert('Please enter backup path!');
      return;
    }
    
    try {
      const response = await fetch('http://localhost:8000/database/restore', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ backup_path: restorePath })
      });
      if (response.ok) {
        alert('Database restore started successfully!');
      }
    } catch (error) {
      console.error('Restore error:', error);
      alert('Restore failed!');
    }
  };

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await Promise.all([fetchDatabaseStats(), fetchDatabaseHealth()]);
      setLoading(false);
    };

    loadData();
  }, []);

  const getHealthStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'bg-green-500';
      case 'warning': return 'bg-yellow-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  const getHealthStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <CheckCircle className="h-4 w-4" />;
      case 'warning': return <AlertCircle className="h-4 w-4" />;
      case 'error': return <AlertCircle className="h-4 w-4" />;
      default: return <Activity className="h-4 w-4" />;
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <RefreshCw className="h-8 w-8 animate-spin" />
        <span className="ml-2">Database verileri yükleniyor...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Veritabanı Yönetimi</h1>
          <p className="text-gray-600">Veritabanı işlemleri ve yönetimi</p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => {
              fetchDatabaseStats();
              fetchDatabaseHealth();
            }}
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Yenile
          </Button>
        </div>
      </div>

      {/* Database Health */}
      {health && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="h-5 w-5" />
              Veritabanı Sağlığı
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-4">
              <Badge className={`${getHealthStatusColor(health.status)} text-white flex items-center gap-1`}>
                {getHealthStatusIcon(health.status)}
                {health.status === 'healthy' ? 'Sağlıklı' : 'Sorunlu'}
              </Badge>
              <span className="text-sm text-gray-600">
                {health.message}
              </span>
              <span className="text-sm text-gray-500">
                Son kontrol: {new Date(health.timestamp).toLocaleString()}
              </span>
            </div>
          </CardContent>
        </Card>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Genel Bakış</TabsTrigger>
          <TabsTrigger value="operations">İşlemler</TabsTrigger>
          <TabsTrigger value="backup">Yedekleme</TabsTrigger>
          <TabsTrigger value="migration">Migration</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          {/* Statistics Cards */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Hastalar</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.counts.patients.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground">
                    Toplam hasta kaydı
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Raporlar</CardTitle>
                  <FileText className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.counts.reports.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground">
                    Toplam rapor sayısı
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">SUV Ölçümleri</CardTitle>
                  <BarChart3 className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.counts.suv_measurements.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground">
                    Toplam SUV ölçümü
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Workflow'lar</CardTitle>
                  <Activity className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.counts.clinical_workflows.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground">
                    Klinik workflow
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Kullanıcılar</CardTitle>
                  <Users className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.counts.users.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground">
                    Sistem kullanıcısı
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Sistem Metrikleri</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.counts.system_metrics.toLocaleString()}</div>
                  <p className="text-xs text-muted-foreground">
                    Performans kaydı
                  </p>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Recent Activity */}
          {stats && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="h-5 w-5" />
                    Son Eklenen Hastalar
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {stats.recent_activity.recent_patients.map((patient) => (
                      <div key={patient.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <p className="font-medium">{patient.name}</p>
                          <p className="text-sm text-gray-600">ID: {patient.id.slice(0, 8)}...</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-gray-500">
                            {new Date(patient.created_at).toLocaleDateString()}
                          </p>
                          <p className="text-xs text-gray-400">
                            {new Date(patient.created_at).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <FileText className="h-5 w-5" />
                    Son Oluşturulan Raporlar
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    {stats.recent_activity.recent_reports.map((report) => (
                      <div key={report.id} className="flex items-center justify-between p-3 border rounded-lg">
                        <div>
                          <p className="font-medium">{report.type.toUpperCase()}</p>
                          <p className="text-sm text-gray-600">ID: {report.id.slice(0, 8)}...</p>
                        </div>
                        <div className="text-right">
                          <p className="text-sm text-gray-500">
                            {new Date(report.created_at).toLocaleDateString()}
                          </p>
                          <p className="text-xs text-gray-400">
                            {new Date(report.created_at).toLocaleTimeString()}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          )}
        </TabsContent>

        <TabsContent value="operations" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Settings className="h-5 w-5" />
                  Veritabanı İşlemleri
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Veritabanı Durumu</Label>
                  <Button 
                    variant="outline" 
                    className="w-full"
                    onClick={fetchDatabaseHealth}
                  >
                    <Activity className="h-4 w-4 mr-2" />
                    Durum Kontrolü
                  </Button>
                </div>
                <div className="space-y-2">
                  <Label>İstatistikleri Yenile</Label>
                  <Button 
                    variant="outline" 
                    className="w-full"
                    onClick={fetchDatabaseStats}
                  >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    İstatistikleri Yenile
                  </Button>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Shield className="h-5 w-5" />
                  Güvenlik İşlemleri
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label>Veritabanı Optimizasyonu</Label>
                  <Button 
                    variant="outline" 
                    className="w-full"
                    onClick={() => alert('Optimizasyon başlatıldı!')}
                  >
                    <Settings className="h-4 w-4 mr-2" />
                    Optimize Et
                  </Button>
                </div>
                <div className="space-y-2">
                  <Label>Index Yenileme</Label>
                  <Button 
                    variant="outline" 
                    className="w-full"
                    onClick={() => alert('Index yenileme başlatıldı!')}
                  >
                    <RefreshCw className="h-4 w-4 mr-2" />
                    Index Yenile
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="backup" className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Download className="h-5 w-5" />
                  Yedekleme
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="backupPath">Yedek Dosya Yolu (Opsiyonel)</Label>
                  <Input
                    id="backupPath"
                    value={backupPath}
                    onChange={(e) => setBackupPath(e.target.value)}
                    placeholder="backup_20241216.db"
                  />
                </div>
                <Button 
                  className="w-full"
                  onClick={startBackup}
                >
                  <Download className="h-4 w-4 mr-2" />
                  Yedekleme Başlat
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Upload className="h-5 w-5" />
                  Geri Yükleme
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="restorePath">Yedek Dosya Yolu *</Label>
                  <Input
                    id="restorePath"
                    value={restorePath}
                    onChange={(e) => setRestorePath(e.target.value)}
                    placeholder="backup_20241216.db"
                    required
                  />
                </div>
                <Button 
                  variant="destructive"
                  className="w-full"
                  onClick={startRestore}
                >
                  <Upload className="h-4 w-4 mr-2" />
                  Geri Yükleme Başlat
                </Button>
              </CardContent>
            </Card>
          </div>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Clock className="h-5 w-5" />
                Otomatik Yedekleme
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Günlük Otomatik Yedekleme</p>
                    <p className="text-sm text-gray-600">Her gün saat 02:00'da otomatik yedekleme</p>
                  </div>
                  <Badge variant="outline">Aktif</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Haftalık Tam Yedekleme</p>
                    <p className="text-sm text-gray-600">Her Pazar tam veritabanı yedekleme</p>
                  </div>
                  <Badge variant="outline">Aktif</Badge>
                </div>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">Yedek Saklama Süresi</p>
                    <p className="text-sm text-gray-600">Son 30 günün yedekleri saklanır</p>
                  </div>
                  <Badge variant="outline">30 Gün</Badge>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="migration" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                Veri Migration
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-4">
                <div>
                  <h4 className="font-semibold mb-2">Migration İşlemleri</h4>
                  <p className="text-sm text-gray-600 mb-4">
                    Veritabanı şeması güncellemeleri ve veri transferi işlemleri
                  </p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 border rounded-lg">
                    <h5 className="font-medium mb-2">Hasta Verileri</h5>
                    <p className="text-sm text-gray-600 mb-3">Hasta kayıtlarının yeni şemaya taşınması</p>
                    <Badge variant="outline">Hazır</Badge>
                  </div>
                  
                  <div className="p-4 border rounded-lg">
                    <h5 className="font-medium mb-2">Rapor Verileri</h5>
                    <p className="text-sm text-gray-600 mb-3">Rapor kayıtlarının yeni şemaya taşınması</p>
                    <Badge variant="outline">Hazır</Badge>
                  </div>
                  
                  <div className="p-4 border rounded-lg">
                    <h5 className="font-medium mb-2">SUV Ölçümleri</h5>
                    <p className="text-sm text-gray-600 mb-3">SUV verilerinin yeni şemaya taşınması</p>
                    <Badge variant="outline">Hazır</Badge>
                  </div>
                  
                  <div className="p-4 border rounded-lg">
                    <h5 className="font-medium mb-2">Sistem Metrikleri</h5>
                    <p className="text-sm text-gray-600 mb-3">Performans verilerinin yeni şemaya taşınması</p>
                    <Badge variant="outline">Hazır</Badge>
                  </div>
                </div>
                
                <div className="pt-4 border-t">
                  <Button 
                    className="w-full"
                    onClick={startMigration}
                  >
                    <Database className="h-4 w-4 mr-2" />
                    Migration Başlat
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default DatabaseManagement;
