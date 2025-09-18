import React, { useState } from 'react';
import Dashboard from './components/Dashboard';
import CaseDetailView from './components/CaseDetailView';
import NewCaseModal from './components/NewCaseModal';
import ReportStudio from './components/ReportStudio';
import ASRPanel from './components/ASRPanel';
import SUVTrend from './components/SUVTrend';
import LesionMatch from './components/LesionMatch';
import EvidencePanel from './components/EvidencePanel';
import DictationMic from './components/DictationMic';
import { PatientCase } from './types';

export default function App() {
  const [activeTab, setActiveTab] = useState<'dashboard' | 'case-detail' | 'report' | 'asr' | 'suv' | 'lesion' | 'evidence'>('dashboard');
  const [patientCases, setPatientCases] = useState<PatientCase[]>([
    // Demo data - mevcut sisteminizdeki örnek vakalar
    {
      id: "CASE-001",
      patientInfo: {
        name: "Ahmet Yılmaz",
        age: 45,
        gender: 'Male',
        admissionDate: "2025-01-15"
      },
      diagnosis: "Lung Cancer - TSNM Evaluation",
      status: 'Analysis Complete',
      qualityControl: 'PASSED',
      clinicalTemplate: 'lung_cancer',
      previousMeasurements: [
        { dateISO: "2024-10-15", suvMax: 8.2 },
        { dateISO: "2025-01-15", suvMax: 12.5 }
      ],
      currentSUVmax: 12.5
    },
    {
      id: "CASE-002", 
      patientInfo: {
        name: "Fatma Demir",
        age: 52,
        gender: 'Female',
        admissionDate: "2025-01-20"
      },
      diagnosis: "Lymphoma - Follow-up TSNM",
      status: 'Awaiting Review',
      qualityControl: 'BORDERLINE',
      clinicalTemplate: 'lymphoma',
      previousMeasurements: [
        { dateISO: "2024-12-01", suvMax: 5.8 }
      ],
      currentSUVmax: 4.2
    }
  ]);
  
  const [selectedCaseId, setSelectedCaseId] = useState<string | null>(null);
  const [showNewCaseModal, setShowNewCaseModal] = useState(false);
  const [dictate, setDictate] = useState("");

  const handleSelectCase = (caseId: string) => {
    setSelectedCaseId(caseId);
    setActiveTab('case-detail');
  };

  const handleAddNewCase = () => {
    setShowNewCaseModal(true);
  };

  const selectedCase = patientCases.find(p => p.id === selectedCaseId);

  return (
    <div className="min-h-screen bg-slate-100">
      <header className="bg-white shadow-sm sticky top-0 z-10">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="h-10 w-10 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center text-white font-bold text-lg">
                N
              </div>
              <h1 className="text-2xl font-bold text-slate-800">
                NeuroPETrix
              </h1>
            </div>
            <div className="flex items-center space-x-4">
              <DictationMic onText={setDictate} />
              {dictate && (
                <span className="text-sm text-gray-600 max-w-xs truncate">
                  🎤 {dictate.slice(0, 40)}...
                </span>
              )}
              <span className="text-sm text-slate-500">Dr. Şeref Karabulut</span>
              <img className="h-8 w-8 rounded-full" src="https://picsum.photos/seed/user/100/100" alt="User" />
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="flex flex-wrap gap-1 bg-white p-1 rounded-lg shadow-sm mb-8">
          <button
            onClick={() => setActiveTab('dashboard')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'dashboard'
                ? 'bg-blue-500 text-white shadow-sm'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            📊 Dashboard
          </button>
          <button
            onClick={() => setActiveTab('report')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'report'
                ? 'bg-blue-500 text-white shadow-sm'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            📝 TSNM Report Studio
          </button>
          <button
            onClick={() => setActiveTab('suv')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'suv'
                ? 'bg-blue-500 text-white shadow-sm'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            📈 SUV Trend
          </button>
          <button
            onClick={() => setActiveTab('lesion')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'lesion'
                ? 'bg-blue-500 text-white shadow-sm'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            🔍 Lezyon Eşleşme
          </button>
          <button
            onClick={() => setActiveTab('evidence')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'evidence'
                ? 'bg-blue-500 text-white shadow-sm'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            📚 Evidence/PICO
          </button>
          <button
            onClick={() => setActiveTab('asr')}
            className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'asr'
                ? 'bg-blue-500 text-white shadow-sm'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            🎤 ASR Panel
          </button>
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-lg shadow-sm">
          {activeTab === 'dashboard' && (
            <Dashboard 
              patientCases={patientCases} 
              onSelectCase={handleSelectCase}
              onAddNewCase={handleAddNewCase}
            />
          )}
          {activeTab === 'case-detail' && selectedCase && (
            <CaseDetailView 
              patientCase={selectedCase}
              onBack={() => setActiveTab('dashboard')}
            />
          )}
          {activeTab === 'report' && <ReportStudio />}
          {activeTab === 'suv' && <SUVTrend />}
          {activeTab === 'lesion' && <LesionMatch />}
          {activeTab === 'evidence' && <EvidencePanel />}
          {activeTab === 'asr' && <ASRPanel />}
        </div>
      </main>

      {/* New Case Modal */}
      {showNewCaseModal && (
        <NewCaseModal
          onClose={() => setShowNewCaseModal(false)}
          onSave={(newCase) => {
            setPatientCases([...patientCases, newCase]);
            setShowNewCaseModal(false);
          }}
        />
      )}
    </div>
  );
}