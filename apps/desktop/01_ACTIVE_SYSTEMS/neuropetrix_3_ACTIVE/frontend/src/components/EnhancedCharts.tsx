import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { 
  BarChart3, 
  LineChart, 
  PieChart, 
  TrendingUp, 
  TrendingDown,
  Download,
  RefreshCw,
  Filter,
  Calendar,
  Activity,
  Users,
  FileText
} from 'lucide-react';

interface ChartData {
  labels: string[];
  datasets: {
    label: string;
    data: number[];
    backgroundColor?: string | string[];
    borderColor?: string | string[];
    borderWidth?: number;
  }[];
}

interface ChartConfig {
  type: 'line' | 'bar' | 'pie' | 'doughnut';
  title: string;
  description: string;
  data: ChartData;
  options?: any;
}

const EnhancedCharts: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedPeriod, setSelectedPeriod] = useState('month');
  const [loading, setLoading] = useState(false);

  // Mock data
  const [chartsData, setChartsData] = useState<Record<string, ChartConfig>>({
    patientTrend: {
      type: 'line',
      title: 'Hasta Trend Analizi',
      description: 'Aylık hasta sayısı değişimi',
      data: {
        labels: ['Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran'],
        datasets: [{
          label: 'Hasta Sayısı',
          data: [120, 135, 142, 158, 167, 180],
          borderColor: 'rgb(59, 130, 246)',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          borderWidth: 2
        }]
      }
    },
    reportDistribution: {
      type: 'pie',
      title: 'Rapor Dağılımı',
      description: 'Rapor türlerine göre dağılım',
      data: {
        labels: ['PET/CT', 'PET/MRI', 'SPECT', 'Diğer'],
        datasets: [{
          label: 'Rapor Sayısı',
          data: [45, 30, 20, 5],
          backgroundColor: [
            'rgba(59, 130, 246, 0.8)',
            'rgba(16, 185, 129, 0.8)',
            'rgba(245, 158, 11, 0.8)',
            'rgba(239, 68, 68, 0.8)'
          ]
        }]
      }
    },
    performanceMetrics: {
      type: 'bar',
      title: 'Performans Metrikleri',
      description: 'Sistem performans göstergeleri',
      data: {
        labels: ['CPU', 'Memory', 'Disk', 'Network'],
        datasets: [{
          label: 'Kullanım (%)',
          data: [65, 78, 45, 32],
          backgroundColor: [
            'rgba(59, 130, 246, 0.8)',
            'rgba(16, 185, 129, 0.8)',
            'rgba(245, 158, 11, 0.8)',
            'rgba(239, 68, 68, 0.8)'
          ]
        }]
      }
    },
    suvAnalysis: {
      type: 'line',
      title: 'SUV Trend Analizi',
      description: 'SUV değerlerinin zaman içindeki değişimi',
      data: {
        labels: ['1. Hafta', '2. Hafta', '3. Hafta', '4. Hafta', '5. Hafta', '6. Hafta'],
        datasets: [{
          label: 'SUV Max',
          data: [8.5, 7.2, 6.8, 5.9, 4.7, 3.8],
          borderColor: 'rgb(239, 68, 68)',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          borderWidth: 2
        }, {
          label: 'SUV Mean',
          data: [4.2, 3.8, 3.5, 3.1, 2.8, 2.4],
          borderColor: 'rgb(16, 185, 129)',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          borderWidth: 2
        }]
      }
    }
  });

  const [statistics, setStatistics] = useState({
    totalPatients: 1247,
    totalReports: 89,
    avgResponseTime: 2.3,
    systemUptime: 99.8
  });

  const refreshData = async () => {
    setLoading(true);
    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Update data based on selected period
      const multiplier = selectedPeriod === 'week' ? 0.25 : selectedPeriod === 'year' ? 4 : 1;
      
      setStatistics(prev => ({
        ...prev,
        totalPatients: Math.floor(prev.totalPatients * (1 + Math.random() * 0.1 - 0.05)),
        totalReports: Math.floor(prev.totalReports * (1 + Math.random() * 0.1 - 0.05)),
        avgResponseTime: prev.avgResponseTime * (1 + Math.random() * 0.1 - 0.05),
        systemUptime: Math.min(99.9, prev.systemUptime + (Math.random() * 0.2 - 0.1))
      }));

      // Update chart data
      setChartsData(prev => {
        const updated = { ...prev };
        Object.keys(updated).forEach(key => {
          const chart = updated[key];
          chart.data.datasets.forEach(dataset => {
            dataset.data = dataset.data.map(value => 
              Math.floor(value * (1 + Math.random() * 0.2 - 0.1) * multiplier)
            );
          });
        });
        return updated;
      });
    } catch (error) {
      console.error('Data refresh error:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    refreshData();
  }, [selectedPeriod]);

  const renderChart = (chartConfig: ChartConfig) => {
    // Mock chart rendering - gerçek implementasyonda Chart.js veya benzeri kullanılacak
    return (
      <div className="h-64 flex items-center justify-center bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
        <div className="text-center">
          {chartConfig.type === 'line' && <LineChart className="h-12 w-12 mx-auto text-gray-400 mb-2" />}
          {chartConfig.type === 'bar' && <BarChart3 className="h-12 w-12 mx-auto text-gray-400 mb-2" />}
          {chartConfig.type === 'pie' && <PieChart className="h-12 w-12 mx-auto text-gray-400 mb-2" />}
          <p className="text-gray-500 font-medium">{chartConfig.title}</p>
          <p className="text-sm text-gray-400">{chartConfig.description}</p>
          <div className="mt-4 flex justify-center gap-2">
            {chartConfig.data.labels.map((label, index) => (
              <Badge key={index} variant="outline" className="text-xs">
                {label}: {chartConfig.data.datasets[0].data[index]}
              </Badge>
            ))}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Gelişmiş Grafikler</h1>
          <p className="text-gray-600">Veri analizi ve görselleştirme</p>
        </div>
        <div className="flex gap-2">
          <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
            <SelectTrigger className="w-32">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="week">Hafta</SelectItem>
              <SelectItem value="month">Ay</SelectItem>
              <SelectItem value="year">Yıl</SelectItem>
            </SelectContent>
          </Select>
          <Button
            variant="outline"
            onClick={refreshData}
            disabled={loading}
          >
            <RefreshCw className={`h-4 w-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Yenile
          </Button>
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            İndir
          </Button>
        </div>
      </div>

      {/* Statistics Overview */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Toplam Hasta</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{statistics.totalPatients.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              <TrendingUp className="inline h-3 w-3 mr-1" />
              +12% bu {selectedPeriod === 'week' ? 'hafta' : selectedPeriod === 'year' ? 'yıl' : 'ay'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Toplam Rapor</CardTitle>
            <FileText className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{statistics.totalReports}</div>
            <p className="text-xs text-muted-foreground">
              <TrendingUp className="inline h-3 w-3 mr-1" />
              +8% bu {selectedPeriod === 'week' ? 'hafta' : selectedPeriod === 'year' ? 'yıl' : 'ay'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Ort. Yanıt Süresi</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{statistics.avgResponseTime.toFixed(1)}s</div>
            <p className="text-xs text-muted-foreground">
              <TrendingDown className="inline h-3 w-3 mr-1" />
              -5% iyileştirme
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Sistem Uptime</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{statistics.systemUptime.toFixed(1)}%</div>
            <p className="text-xs text-muted-foreground">
              <TrendingUp className="inline h-3 w-3 mr-1" />
              Mükemmel performans
            </p>
          </CardContent>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="overview">Genel Bakış</TabsTrigger>
          <TabsTrigger value="patients">Hasta Analizi</TabsTrigger>
          <TabsTrigger value="reports">Rapor Analizi</TabsTrigger>
          <TabsTrigger value="performance">Performans</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <LineChart className="h-5 w-5" />
                  {chartsData.patientTrend.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {renderChart(chartsData.patientTrend)}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChart className="h-5 w-5" />
                  {chartsData.reportDistribution.title}
                </CardTitle>
              </CardHeader>
              <CardContent>
                {renderChart(chartsData.reportDistribution)}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="patients" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="h-5 w-5" />
                Hasta Trend Analizi
              </CardTitle>
            </CardHeader>
            <CardContent>
              {renderChart(chartsData.patientTrend)}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="reports" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <PieChart className="h-5 w-5" />
                  Rapor Dağılımı
                </CardTitle>
              </CardHeader>
              <CardContent>
                {renderChart(chartsData.reportDistribution)}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <LineChart className="h-5 w-5" />
                  SUV Trend Analizi
                </CardTitle>
              </CardHeader>
              <CardContent>
                {renderChart(chartsData.suvAnalysis)}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="performance" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="h-5 w-5" />
                Sistem Performans Metrikleri
              </CardTitle>
            </CardHeader>
            <CardContent>
              {renderChart(chartsData.performanceMetrics)}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Chart Controls */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Filter className="h-5 w-5" />
            Grafik Kontrolleri
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <label className="text-sm font-medium">Zaman Aralığı</label>
              <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="week">Son 7 Gün</SelectItem>
                  <SelectItem value="month">Son 30 Gün</SelectItem>
                  <SelectItem value="year">Son 12 Ay</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Grafik Türü</label>
              <Select defaultValue="line">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="line">Çizgi Grafik</SelectItem>
                  <SelectItem value="bar">Bar Grafik</SelectItem>
                  <SelectItem value="pie">Pasta Grafik</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <label className="text-sm font-medium">Veri Kaynağı</label>
              <Select defaultValue="all">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">Tüm Veriler</SelectItem>
                  <SelectItem value="patients">Hasta Verileri</SelectItem>
                  <SelectItem value="reports">Rapor Verileri</SelectItem>
                  <SelectItem value="system">Sistem Verileri</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default EnhancedCharts;
