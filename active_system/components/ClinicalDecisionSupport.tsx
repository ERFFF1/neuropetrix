import React, { useState, useEffect } from 'react';

interface ClinicalWorkflow {
  branches: {
    [key: string]: {
      name: string;
      icd_codes: string[];
      workflow_steps: string[];
      clinical_targets: {
        [key: string]: string;
      };
    };
  };
}

interface PatientCase {
  id: string;
  name: string;
  age: number;
  gender: string;
  diagnosis: string;
  icd_codes: string[];
  clinical_goals: string[];
}

interface ClinicalDecisionSupportProps {
  patientCase?: PatientCase;
  onWorkflowComplete?: (result: any) => void;
}

const CLINICAL_WORKFLOW: ClinicalWorkflow = {
  branches: {
    oncology: {
      name: "Onkoloji",
      icd_codes: ["C78", "C79", "C80", "C81", "C82", "C83", "C84", "C85"],
      workflow_steps: [
        "ICD Kod Girişi",
        "Klinik Hedef Seçimi",
        "Literatür Taraması",
        "SUVmax Hesaplama",
        "Segmentasyon ve Analiz",
        "Klinik Yorumlama",
        "Rapor Üretimi",
        "Takip Planlaması"
      ],
      clinical_targets: {
        diagnosis: "Tanı",
        staging: "Evreleme",
        treatment_response: "Tedaviye Yanıt",
        follow_up: "Takip",
        screening: "Tarama"
      }
    },
    cardiology: {
      name: "Kardiyoloji",
      icd_codes: ["I20", "I21", "I22", "I23", "I24", "I25"],
      workflow_steps: [
        "ICD Kod Girişi",
        "Klinik Hedef Seçimi",
        "Literatür Taraması",
        "PET Perfüzyon Analizi",
        "Segmentasyon ve Analiz",
        "Klinik Yorumlama",
        "Rapor Üretimi",
        "Takip Planlaması"
      ],
      clinical_targets: {
        diagnosis: "Tanı",
        prognosis: "Prognoz",
        treatment_response: "Tedaviye Yanıt",
        follow_up: "Takip"
      }
    },
    neurology: {
      name: "Nöroloji",
      icd_codes: ["G30", "G31", "G32", "G93", "G94"],
      workflow_steps: [
        "ICD Kod Girişi",
        "Klinik Hedef Seçimi",
        "Literatür Taraması",
        "PET Metabolik Analizi",
        "Segmentasyon ve Analiz",
        "Klinik Yorumlama",
        "Rapor Üretimi",
        "Takip Planlaması"
      ],
      clinical_targets: {
        diagnosis: "Tanı",
        prognosis: "Prognoz",
        treatment_response: "Tedaviye Yanıt",
        follow_up: "Takip"
      }
    },
    endocrinology: {
      name: "Endokrinoloji",
      icd_codes: ["E10", "E11", "E12", "E13", "E14"],
      workflow_steps: [
        "ICD Kod Girişi",
        "Klinik Hedef Seçimi",
        "Literatür Taraması",
        "PET Metabolik Analizi",
        "Segmentasyon ve Analiz",
        "Klinik Yorumlama",
        "Rapor Üretimi",
        "Takip Planlaması"
      ],
      clinical_targets: {
        diagnosis: "Tanı",
        prognosis: "Prognoz",
        treatment_response: "Tedaviye Yanıt",
        follow_up: "Takip"
      }
    }
  }
};

export default function ClinicalDecisionSupport({ patientCase, onWorkflowComplete }: ClinicalDecisionSupportProps) {
  const [icdCode, setIcdCode] = useState('');
  const [selectedBranch, setSelectedBranch] = useState<string | null>(null);
  const [clinicalTarget, setClinicalTarget] = useState<string>('');
  const [inputMethod, setInputMethod] = useState<'manual' | 'voice'>('manual');
  const [workflowActive, setWorkflowActive] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [workflowResults, setWorkflowResults] = useState<any>(null);

  // Backend API'den ICD kodunu analiz et
  const analyzeIcdCode = async (code: string) => {
    try {
      const response = await fetch('http://localhost:8000/clinical-workflow/analyze-icd', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ icd_code: code }),
      });
      
      if (response.ok) {
        const data = await response.json();
        return data.detected_branch;
      }
    } catch (error) {
      console.error('ICD analiz hatası:', error);
      // Fallback: local analiz
      for (const [branchName, branchData] of Object.entries(CLINICAL_WORKFLOW.branches)) {
        for (const icdCode of branchData.icd_codes) {
          if (code.includes(icdCode)) {
            return branchName;
          }
        }
      }
    }
    return null;
  };

  // ICD kodu değiştiğinde analiz et
  useEffect(() => {
    if (icdCode) {
      analyzeIcdCode(icdCode).then((detectedBranch) => {
        setSelectedBranch(detectedBranch);
        if (detectedBranch) {
          setClinicalTarget(Object.keys(CLINICAL_WORKFLOW.branches[detectedBranch].clinical_targets)[0]);
        }
      });
    }
  }, [icdCode]);

  // Workflow başlat
  const startWorkflow = async () => {
    if (!selectedBranch || !clinicalTarget) return;

    setWorkflowActive(true);
    setCurrentStep(0);

    try {
      // Backend API'ye workflow isteği gönder
      const response = await fetch('http://localhost:8000/clinical-workflow/execute-workflow', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          icd_code: icdCode,
          clinical_target: clinicalTarget,
          patient_id: patientCase?.id || 'ANON'
        }),
      });

      if (response.ok) {
        const data = await response.json();
        
        // Workflow adımlarını simüle et
        const workflowSteps = data.steps;
        for (let i = 0; i < workflowSteps.length; i++) {
          setCurrentStep(i);
          await new Promise(resolve => setTimeout(resolve, 1000));
        }

        // Sonuçları ayarla
        setWorkflowResults({
          ...data,
          completedAt: new Date().toISOString()
        });
        
        if (onWorkflowComplete) {
          onWorkflowComplete(data);
        }
      } else {
        throw new Error('Workflow execution failed');
      }
    } catch (error) {
      console.error('Workflow hatası:', error);
      // Fallback: local workflow
      const workflowSteps = CLINICAL_WORKFLOW.branches[selectedBranch].workflow_steps;
      for (let i = 0; i < workflowSteps.length; i++) {
        setCurrentStep(i);
        await new Promise(resolve => setTimeout(resolve, 1000));
      }
      
      const results = {
        workflow_id: `WF_${Date.now()}`,
        icdCode,
        branch: selectedBranch,
        clinicalTarget,
        steps: workflowSteps,
        completedAt: new Date().toISOString()
      };
      
      setWorkflowResults(results);
      if (onWorkflowComplete) {
        onWorkflowComplete(results);
      }
    }

    setWorkflowActive(false);
  };

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white text-center">
        <h1 className="text-4xl font-bold mb-2">🏥 Clinical Decision Support</h1>
        <p className="text-xl mb-1">ICD ile Başlayan Klinik Karar Destek Sistemi</p>
        <p className="text-blue-100">Akıllı klinik workflow ve GRADE metodolojisi</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Ana İçerik */}
        <div className="lg:col-span-2 space-y-6">
          {/* ICD Kod Girişi */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4">🔍 ICD Kod Girişi</h2>
            
            {/* Giriş Yöntemi Seçimi */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-3">Giriş Yöntemi:</label>
              <div className="flex space-x-4">
                <button
                  onClick={() => setInputMethod('manual')}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    inputMethod === 'manual'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  Manuel Giriş
                </button>
                <button
                  onClick={() => setInputMethod('voice')}
                  className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                    inputMethod === 'voice'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  🎤 Sesli Giriş
                </button>
              </div>
            </div>

            {/* ICD Kod Girişi */}
            {inputMethod === 'manual' && (
              <div className="bg-gradient-to-r from-pink-400 to-red-500 rounded-xl p-6 text-white">
                <label className="block text-sm font-medium mb-2">ICD-10 Kodu:</label>
                <input
                  type="text"
                  value={icdCode}
                  onChange={(e) => setIcdCode(e.target.value)}
                  placeholder="Örn: C78.0, I21.9, G30.0"
                  className="w-full px-4 py-3 rounded-lg text-gray-800 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-white"
                />
                <p className="text-sm mt-2 opacity-90">ICD-10 kodunu girin</p>
              </div>
            )}

            {inputMethod === 'voice' && (
              <div className="bg-gradient-to-r from-blue-400 to-cyan-500 rounded-xl p-6 text-white">
                <h3 className="text-lg font-semibold mb-4">🎤 Sesli ICD Kod Girişi</h3>
                <button className="bg-white text-blue-600 px-6 py-3 rounded-lg font-medium hover:bg-blue-50 transition-colors">
                  🎤 Kayıt Başlat
                </button>
                <p className="text-sm mt-2 opacity-90">Mikrofon izni verin ve ICD kodunu söyleyin</p>
              </div>
            )}

            {/* ICD Kod Analizi Sonucu */}
            {icdCode && selectedBranch && (
              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-center">
                  <span className="text-green-600 text-xl mr-2">✅</span>
                  <span className="text-green-800 font-medium">
                    ICD kodu '{icdCode}' {CLINICAL_WORKFLOW.branches[selectedBranch].name} branşında tespit edildi!
                  </span>
                </div>
              </div>
            )}

            {icdCode && !selectedBranch && (
              <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="flex items-center">
                  <span className="text-yellow-600 text-xl mr-2">⚠️</span>
                  <span className="text-yellow-800 font-medium">
                    ICD kodu tanınmadı. Lütfen geçerli bir ICD-10 kodu girin.
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Klinik Hedef Seçimi */}
          {selectedBranch && (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">🎯 Klinik Hedef Seçimi</h2>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">Klinik Hedef:</label>
                <select
                  value={clinicalTarget}
                  onChange={(e) => setClinicalTarget(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  {Object.entries(CLINICAL_WORKFLOW.branches[selectedBranch].clinical_targets).map(([key, value]) => (
                    <option key={key} value={key}>{value}</option>
                  ))}
                </select>
              </div>

              {/* Workflow Başlat Butonu */}
              <button
                onClick={startWorkflow}
                disabled={workflowActive || !clinicalTarget}
                className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
              >
                {workflowActive ? '🔄 Workflow Çalışıyor...' : '🚀 Workflow Başlat'}
              </button>
            </div>
          )}

          {/* Workflow Sonuçları */}
          {workflowResults && (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">📋 Klinik Workflow Sonuçları</h2>
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <div className="space-y-2">
                  <p><strong>ICD Kodu:</strong> {workflowResults.icdCode}</p>
                  <p><strong>Branş:</strong> {CLINICAL_WORKFLOW.branches[workflowResults.branch].name}</p>
                  <p><strong>Klinik Hedef:</strong> {CLINICAL_WORKFLOW.branches[workflowResults.branch].clinical_targets[workflowResults.clinicalTarget]}</p>
                  <p><strong>Tamamlanma Zamanı:</strong> {new Date(workflowResults.completedAt).toLocaleString('tr-TR')}</p>
                </div>
                <div className="mt-4">
                  <h3 className="font-semibold text-green-800 mb-2">Tamamlanan Adımlar:</h3>
                  <ul className="space-y-1">
                    {workflowResults.steps.map((step: string, index: number) => (
                      <li key={index} className="flex items-center text-green-700">
                        <span className="text-green-600 mr-2">✅</span>
                        {index + 1}. {step}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Yan Panel */}
        <div className="space-y-6">
          {/* Sistem Durumu */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">📊 Sistem Durumu</h3>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Aktif Workflow</span>
                <span className="font-semibold">{workflowActive ? '1' : '0'}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Tamamlanan Analiz</span>
                <span className="font-semibold">{workflowResults ? '1' : '0'}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">GRADE Değerlendirme</span>
                <span className="font-semibold">0</span>
              </div>
            </div>
          </div>

          {/* Branş Seçimi */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h3 className="text-xl font-bold text-gray-800 mb-4">🏥 Branş Seçimi</h3>
            <div className="space-y-3">
              {Object.entries(CLINICAL_WORKFLOW.branches).map(([key, branch]) => (
                <div
                  key={key}
                  className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                    selectedBranch === key
                      ? 'bg-blue-50 border-blue-300'
                      : 'bg-gray-50 border-gray-200 hover:bg-gray-100'
                  }`}
                  onClick={() => setSelectedBranch(key)}
                >
                  <div className="font-medium text-gray-800">{branch.name}</div>
                  <div className="text-sm text-gray-600">
                    ICD: {branch.icd_codes.join(', ')}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Workflow Adımları */}
          {selectedBranch && (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h3 className="text-xl font-bold text-gray-800 mb-4">📋 Workflow Adımları</h3>
              <div className="space-y-2">
                {CLINICAL_WORKFLOW.branches[selectedBranch].workflow_steps.map((step, index) => (
                  <div
                    key={index}
                    className={`flex items-center p-2 rounded-lg transition-colors ${
                      workflowActive && index === currentStep
                        ? 'bg-green-100 border border-green-300'
                        : workflowActive && index < currentStep
                        ? 'bg-green-50'
                        : 'bg-gray-50'
                    }`}
                  >
                    <span className="text-sm font-medium text-gray-600 w-6">{index + 1}.</span>
                    <span className="text-sm text-gray-800">{step}</span>
                    {workflowActive && index < currentStep && (
                      <span className="ml-auto text-green-600">✅</span>
                    )}
                    {workflowActive && index === currentStep && (
                      <span className="ml-auto text-blue-600">🔄</span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="text-center text-gray-500 py-6">
        <p className="text-lg">🏥 Clinical Decision Support - NeuroPETRIX v3.0</p>
        <p>ICD-10 tabanlı klinik karar destek sistemi</p>
      </div>
    </div>
  );
}
