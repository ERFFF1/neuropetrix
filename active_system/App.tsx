import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import PETReportStudio from './components/PETReportStudio';
import EvidencePanel from './components/EvidencePanel';
import SUVTrend from './components/SUVTrend';
import PICOAutomation from './components/PICOAutomation';
import MultimodalFusion from './components/MultimodalFusion';
import ClinicalFeedback from './components/ClinicalFeedback';
import CompliancePanel from './components/CompliancePanel';
import SystemMonitor from './components/SystemMonitor';
import ScriptManagement from './components/ScriptManagement';
import PatientManagement from './components/PatientManagement';
import AdvancedSUVTrend from './components/AdvancedSUVTrend';
import DICOMViewer from './components/DICOMViewer';
import EnhancedPICOAutomation from './components/EnhancedPICOAutomation';
import DesktopRunner from './components/DesktopRunner';
import ClinicalDecisionSupport from './components/ClinicalDecisionSupport';
import SystemMonitoring from './components/SystemMonitoring';
import PerformanceDashboard from './components/PerformanceDashboard';
import EnhancedDashboard from './components/EnhancedDashboard';
import EnhancedForms from './components/EnhancedForms';
import EnhancedCharts from './components/EnhancedCharts';
import DatabaseManagement from './components/DatabaseManagement';

type Page = 'dashboard' | 'pet-report' | 'evidence' | 'suv-trend' | 'pico' | 'multimodal' | 'feedback' | 'compliance' | 'monitor' | 'scripts' | 'patients' | 'desktop-runner' | 'clinical-decision' | 'system-monitoring' | 'performance' | 'enhanced-dashboard' | 'enhanced-forms' | 'enhanced-charts' | 'database-management';

interface PatientCase {
  id: string;
  name: string;
  age: number;
  gender: string;
  diagnosis: string;
  comorbidities: string[];
  medications: string[];
  icdCodes: string[];
  clinicalGoals: string[];
  patient?: any; // Added for PatientManagement
  case?: any; // Added for PatientManagement
}

export default function App() {
  const [currentPage, setCurrentPage] = useState<Page>('dashboard');
  const [selectedCase, setSelectedCase] = useState<PatientCase | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  // Mock patient case for testing
  useEffect(() => {
    setSelectedCase({
      id: 'case-001',
      name: 'Ahmet Yılmaz',
      age: 65,
      gender: 'M',
      diagnosis: 'Akciğer kanseri şüphesi',
      comorbidities: ['Hipertansiyon', 'Diyabet'],
      medications: ['Metformin', 'Lisinopril'],
      icdCodes: ['C34.90', 'I10'],
      clinicalGoals: ['Tanı doğrulama', 'Tedavi planı oluşturma']
    });
  }, []);

  const navigationItems = [
    { key: 'dashboard', label: '🏠 Dashboard', icon: '🏠', description: 'Ana Kontrol Paneli' },
    { key: 'enhanced-dashboard', label: '🎯 Gelişmiş Dashboard', icon: '🎯', description: 'Gelişmiş analitik ve görselleştirme' },
    { key: 'enhanced-forms', label: '📝 Gelişmiş Formlar', icon: '📝', description: 'Hasta kayıtları ve rapor formları' },
    { key: 'enhanced-charts', label: '📊 Gelişmiş Grafikler', icon: '📊', description: 'Veri analizi ve görselleştirme' },
    { key: 'database-management', label: '🗄️ Veritabanı Yönetimi', icon: '🗄️', description: 'Veritabanı işlemleri ve yönetimi' },
    { key: 'clinical-decision', label: '🏥 Klinik Karar Destek', icon: '🏥', description: 'ICD-10 Workflow ve GRADE' },
    { key: 'system-monitoring', label: '📊 Sistem Monitörü', icon: '📊', description: 'Real-time sistem performansı' },
    { key: 'performance', label: '⚡ Performans Dashboard', icon: '⚡', description: 'Sistem optimizasyonu ve performans' },
    { key: 'patients', label: '👥 Hasta Yönetimi', icon: '👥', description: 'Hasta Kayıtları ve Vakalar' },
    { key: 'dicom-viewer', label: '🖼️ DICOM Görüntüleyici', icon: '🖼️', description: 'DICOM Yükleme ve Analiz' },
    { key: 'suv-trend', label: '📊 SUV Trend Analizi', icon: '📊', description: 'SUV Ölçümleri ve Trendler' },
    { key: 'advanced-suv', label: '🔬 Gelişmiş SUV Analizi', icon: '🔬', description: 'PERCIST ve Deauville Kriterleri' },
    { key: 'enhanced-pico', label: '🔍 Gelişmiş PICO', icon: '🔍', description: 'Kanıta Dayalı Tıp Otomasyonu' },
    { key: 'pet-report', label: '📋 PET Rapor Stüdyosu', icon: '📋', description: 'TSNM Standart Raporlar' },
    { key: 'evidence', label: '📚 Kanıt Paneli', icon: '📚', description: 'Literatür ve Kanıt Arama' },
    { key: 'multimodal', label: '🔄 Multimodal Füzyon', icon: '🔄', description: 'Çoklu Veri Entegrasyonu' },
    { key: 'feedback', label: '💬 Klinik Geri Bildirim', icon: '💬', description: 'Hekim Onayı ve Öğrenme' },
    { key: 'compliance', label: '⚖️ Uyum Paneli', icon: '⚖️', description: 'KVKK & HIPAA Uyumluluğu' },
    { key: 'monitor', label: '📊 Sistem Monitörü', icon: '📊', description: 'Performans ve Sağlık Takibi' },
    { key: 'scripts', label: '⚙️ Script Yönetimi', icon: '⚙️', description: 'Otomasyon ve Makro Araçları' },
    { key: 'desktop-runner', label: '🖥️ Desktop Runner', icon: '🖥️', description: 'MONAI + PyRadiomics Pipeline' }
  ];

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard selectedCase={selectedCase} />;
      case 'patients':
        return <PatientManagement 
          onPatientSelect={(patient) => setSelectedCase({ ...selectedCase, patient })}
          onCaseSelect={(caseData) => setSelectedCase({ ...selectedCase, case: caseData })}
        />;
      case 'pet-report':
        return <PETReportStudio patientCase={selectedCase} />;
      case 'evidence':
        return <EvidencePanel patientCase={selectedCase} />;
      case 'suv-trend':
        return <SUVTrend patientCase={selectedCase} />;
      case 'pico':
        return <PICOAutomation 
          patientCase={selectedCase} 
          onAnalysisComplete={(result) => console.log('PICO analizi tamamlandı:', result)} 
        />;
      case 'multimodal':
        return <MultimodalFusion 
          patientCase={selectedCase} 
          onFusionComplete={(result) => console.log('Multimodal füzyon tamamlandı:', result)} 
        />;
      case 'feedback':
        return <ClinicalFeedback 
          caseId={selectedCase.case?.id || 'default'}
          physicianId="physician_001"
          currentRecommendation={selectedCase.currentRecommendation || {}}
          onFeedbackSubmitted={(feedback) => console.log('Geri bildirim gönderildi:', feedback)} 
        />;
      case 'compliance':
        return <CompliancePanel patientCase={selectedCase} />;
      case 'monitor':
        return <SystemMonitor />;
      case 'scripts':
        return <ScriptManagement />;
      case 'dicom-viewer':
        return <DICOMViewer onAnalysisComplete={(result) => console.log('DICOM Analysis:', result)} />;
      case 'advanced-suv':
        return <AdvancedSUVTrend patientCase={selectedCase} />;
      case 'enhanced-pico':
        return <EnhancedPICOAutomation />;
      case 'desktop-runner':
        return <DesktopRunner />;
          case 'clinical-decision':
            return <ClinicalDecisionSupport
              patientCase={selectedCase}
              onWorkflowComplete={(result) => console.log('Clinical workflow completed:', result)}
            />;
          case 'system-monitoring':
            return <SystemMonitoring />;
          case 'performance':
            return <PerformanceDashboard />;
          case 'enhanced-dashboard':
            return <EnhancedDashboard />;
          case 'enhanced-forms':
            return <EnhancedForms />;
          case 'enhanced-charts':
            return <EnhancedCharts />;
          case 'database-management':
            return <DatabaseManagement />;
          default:
            return <Dashboard selectedCase={selectedCase} />;
    }
  };

  return (
    <div className="min-h-screen bg-medical-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 z-50 w-64 bg-white shadow-xl border-r border-medical-200 transform transition-transform duration-300 ease-in-out">
        {/* Logo */}
        <div className="flex items-center justify-center h-16 bg-gradient-to-r from-medical-600 to-medical-700 text-white">
          <div className="text-2xl font-bold">🧠</div>
          <div className="ml-3">
            <div className="text-lg font-bold">NeuroPETrix</div>
            <div className="text-xs opacity-90">AI Clinical Decision</div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="mt-6 px-4">
          <div className="space-y-2">
            {navigationItems.map((item) => (
              <button
                key={item.key}
                onClick={() => setCurrentPage(item.key)}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-xl text-left transition-all duration-200 group ${
                  currentPage === item.key
                    ? 'bg-medical-100 text-medical-900 shadow-sm border border-medical-200'
                    : 'text-medical-600 hover:bg-medical-50 hover:text-medical-800'
                }`}
              >
                <span className="text-xl">{item.icon}</span>
                <div className="flex-1 min-w-0">
                  <div className="font-medium text-sm truncate">{item.label}</div>
                  <div className="text-xs opacity-75 truncate">{item.description}</div>
                </div>
                {currentPage === item.key && (
                  <div className="w-2 h-2 bg-medical-600 rounded-full"></div>
                )}
              </button>
            ))}
          </div>
        </nav>

        {/* User Info & System Status */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-medical-200 bg-medical-50">
          <div className="flex items-center space-x-3 mb-3">
            <div className="w-8 h-8 bg-medical-200 rounded-full flex items-center justify-center">
              <span className="text-medical-600 font-medium text-sm">👨‍⚕️</span>
            </div>
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-medical-900 truncate">Dr. Kullanıcı</div>
              <div className="text-xs text-medical-600">Radyolog</div>
            </div>
          </div>
          
          <div className="flex items-center justify-between text-xs">
            <span className="text-medical-600">Sistem:</span>
            <span className="text-green-600 font-medium">✅ Aktif</span>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="ml-64">
        {/* Top Bar */}
        <div className="bg-white shadow-sm border-b border-medical-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <h1 className="text-2xl font-bold text-medical-900">
                {navigationItems.find(item => item.key === currentPage)?.label || 'Dashboard'}
              </h1>
              <div className="text-medical-500">
                {navigationItems.find(item => item.key === currentPage)?.description}
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              {/* Search */}
              <div className="relative">
                <input
                  type="text"
                  placeholder="Hızlı arama..."
                  className="w-64 pl-10 pr-4 py-2 border border-medical-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-medical-500 focus:border-transparent"
                />
                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                  <span className="text-medical-400">🔍</span>
                </div>
              </div>

              {/* Notifications */}
              <button className="relative p-2 text-medical-600 hover:text-medical-800 hover:bg-medical-100 rounded-lg transition-colors">
                <span className="text-xl">🔔</span>
                <span className="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full"></span>
              </button>

              {/* Settings */}
              <button className="p-2 text-medical-600 hover:text-medical-800 hover:bg-medical-100 rounded-lg transition-colors">
                <span className="text-xl">⚙️</span>
              </button>
            </div>
          </div>
        </div>

        {/* Page Content */}
        <div className="p-6">
          {renderCurrentPage()}
        </div>
      </div>
    </div>
  );
}