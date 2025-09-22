import React, { useState, useEffect } from 'react';
import { PICOQuestion, EvidenceSearch, CriticalAppraisal, ApplicabilityAnalysis } from '../types';

interface PICOAutomationProps {
  patientCase: any;
  onAnalysisComplete: (result: any) => void;
}

export default function PICOAutomation({ patientCase, onAnalysisComplete }: PICOAutomationProps) {
  const [currentStep, setCurrentStep] = useState<'pico' | 'search' | 'appraisal' | 'applicability'>('pico');
  const [picoQuestion, setPicoQuestion] = useState<PICOQuestion>({
    population: '',
    intervention: '',
    comparison: '',
    outcome: '',
    clinicalContext: ''
  });
  const [evidenceSearch, setEvidenceSearch] = useState<EvidenceSearch | null>(null);
  const [criticalAppraisal, setCriticalAppraisal] = useState<CriticalAppraisal | null>(null);
  const [applicabilityAnalysis, setApplicabilityAnalysis] = useState<ApplicabilityAnalysis | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // PICO Soru Oluşturma
  const generatePICOQuestion = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/pico/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patientData: patientCase,
          clinicalContext: patientCase.diagnosis
        })
      });
      
      const result = await response.json();
      setPicoQuestion(result.picoQuestion);
      setCurrentStep('search');
    } catch (error) {
      console.error('PICO soru oluşturma hatası:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Literatür Arama
  const performEvidenceSearch = async () => {
    setIsLoading(true);
    try {
      const searchParams = {
        picoQuestion,
        databases: ['PubMed', 'Cochrane', 'Embase'],
        dateRange: { start: '2020-01-01', end: new Date().toISOString().split('T')[0] }
      };

      const response = await fetch('/api/evidence/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(searchParams)
      });

      const result = await response.json();
      setEvidenceSearch(result);
      setCurrentStep('appraisal');
    } catch (error) {
      console.error('Literatür arama hatası:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Eleştirel Değerlendirme
  const performCriticalAppraisal = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/evidence/appraise', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          evidenceSearch,
          patientData: patientCase
        })
      });

      const result = await response.json();
      setCriticalAppraisal(result);
      setCurrentStep('applicability');
    } catch (error) {
      console.error('Eleştirel değerlendirme hatası:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Uygulanabilirlik Analizi
  const performApplicabilityAnalysis = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/evidence/applicability', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          criticalAppraisal,
          patientData: patientCase,
          comorbidities: patientCase.comorbidities || [],
          medications: patientCase.medications || []
        })
      });

      const result = await response.json();
      setApplicabilityAnalysis(result);
      
      onAnalysisComplete({
        picoQuestion,
        evidenceSearch,
        criticalAppraisal,
        applicabilityAnalysis: result
      });
    } catch (error) {
      console.error('Uygulanabilirlik analizi hatası:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Başlık */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-800">
            🔍 PICO Otomatikleştirme
          </h1>
          <p className="text-slate-600 mt-2">
            AI destekli PICO soru oluşturma ve kanıta dayalı tıp araçları
          </p>
        </div>

        {/* Ana İçerik */}
        <div className="bg-white rounded-lg shadow-md border border-slate-200 p-6">
          <h2 className="text-2xl font-bold text-slate-800 mb-6">PICO Otomatikleştirme Algoritması</h2>
          
          {/* Adım Göstergesi */}
          <div className="mb-8">
            <div className="flex items-center justify-center space-x-4">
              {[
                { key: 'pico', label: 'PICO Soru', icon: '🔍' },
                { key: 'search', label: 'Literatür Arama', icon: '📚' },
                { key: 'appraisal', label: 'Eleştirel Değerlendirme', icon: '🔬' },
                { key: 'applicability', label: 'Uygulanabilirlik', icon: '✅' }
              ].map((step, index) => (
                <div key={step.key} className="flex items-center">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium ${
                    currentStep === step.key 
                      ? 'bg-blue-500 text-white' 
                      : index < ['pico', 'search', 'appraisal', 'applicability'].indexOf(currentStep)
                      ? 'bg-green-500 text-white'
                      : 'bg-slate-200 text-slate-600'
                  }`}>
                    {step.icon}
                  </div>
                  <span className={`ml-2 text-sm font-medium ${
                    currentStep === step.key ? 'text-blue-600' : 'text-slate-600'
                  }`}>
                    {step.label}
                  </span>
                  {index < 3 && (
                    <div className="w-8 h-0.5 bg-slate-200 mx-2"></div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Step Content */}
          <div className="mt-8">
            {/* Step 1: PICO Question */}
            {currentStep === 'pico' && (
              <div className="space-y-6">
                <h3 className="text-xl font-semibold text-slate-800">1. PICO Soru Oluşturma</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Population (Popülasyon)</label>
                    <textarea
                      value={picoQuestion.population}
                      onChange={(e) => setPicoQuestion({...picoQuestion, population: e.target.value})}
                      className="w-full p-3 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Hasta popülasyonu tanımı..."
                      rows={3}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Intervention (Müdahale)</label>
                    <textarea
                      value={picoQuestion.intervention}
                      onChange={(e) => setPicoQuestion({...picoQuestion, intervention: e.target.value})}
                      className="w-full p-3 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Tedavi/müdahale tanımı..."
                      rows={3}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Comparison (Karşılaştırma)</label>
                    <textarea
                      value={picoQuestion.comparison}
                      onChange={(e) => setPicoQuestion({...picoQuestion, comparison: e.target.value})}
                      className="w-full p-3 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Karşılaştırma grubu..."
                      rows={3}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Outcome (Sonuç)</label>
                    <textarea
                      value={picoQuestion.outcome}
                      onChange={(e) => setPicoQuestion({...picoQuestion, outcome: e.target.value})}
                      className="w-full p-3 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                      placeholder="Beklenen sonuç..."
                      rows={3}
                    />
                  </div>
                </div>
                <div className="flex justify-between">
                  <button
                    onClick={generatePICOQuestion}
                    disabled={isLoading}
                    className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors duration-200 font-medium"
                  >
                    {isLoading ? 'Oluşturuluyor...' : 'AI ile PICO Oluştur'}
                  </button>
                  <button
                    onClick={() => setCurrentStep('search')}
                    className="bg-slate-600 text-white px-6 py-3 rounded-md hover:bg-slate-700 transition-colors duration-200 font-medium"
                  >
                    Sonraki Adım
                  </button>
                </div>
              </div>
            )}

            {/* Step 2: Evidence Search */}
            {currentStep === 'search' && (
              <div className="space-y-6">
                <h3 className="text-xl font-semibold text-slate-800">2. Literatür Arama</h3>
                {evidenceSearch && (
                  <div className="bg-slate-50 p-4 rounded-md border border-slate-200">
                    <h4 className="font-medium mb-2 text-slate-800">Arama Sonuçları:</h4>
                    <p className="text-sm text-slate-600">
                      {evidenceSearch.databases.join(', ')} veritabanlarında {evidenceSearch.inclusionCriteria.length} kriter ile arama yapıldı.
                    </p>
                  </div>
                )}
                <div className="flex justify-between">
                  <button
                    onClick={() => setCurrentStep('pico')}
                    className="bg-slate-600 text-white px-6 py-3 rounded-md hover:bg-slate-700 transition-colors duration-200 font-medium"
                  >
                    Geri
                  </button>
                  <button
                    onClick={performEvidenceSearch}
                    disabled={isLoading}
                    className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors duration-200 font-medium"
                  >
                    {isLoading ? 'Aranıyor...' : 'Literatür Ara'}
                  </button>
                </div>
              </div>
            )}

            {/* Step 3: Critical Appraisal */}
            {currentStep === 'appraisal' && (
              <div className="space-y-6">
                <h3 className="text-xl font-semibold text-slate-800">3. Eleştirel Değerlendirme</h3>
                {criticalAppraisal && (
                  <div className="bg-slate-50 p-4 rounded-md border border-slate-200">
                    <h4 className="font-medium mb-2 text-slate-800">Değerlendirme Sonuçları:</h4>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="font-medium text-slate-700">Metodoloji Kalitesi:</span> {criticalAppraisal.methodologyQuality}/10
                      </div>
                      <div>
                        <span className="font-medium text-slate-700">Yanlılık Riski:</span> {criticalAppraisal.biasRisk}
                      </div>
                    </div>
                  </div>
                )}
                <div className="flex justify-between">
                  <button
                    onClick={() => setCurrentStep('search')}
                    className="bg-slate-600 text-white px-6 py-3 rounded-md hover:bg-slate-700 transition-colors duration-200 font-medium"
                  >
                    Geri
                  </button>
                  <button
                    onClick={performCriticalAppraisal}
                    disabled={isLoading}
                    className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors duration-200 font-medium"
                  >
                    {isLoading ? 'Değerlendiriliyor...' : 'Değerlendir'}
                  </button>
                </div>
              </div>
            )}

            {/* Step 4: Applicability Analysis */}
            {currentStep === 'applicability' && (
              <div className="space-y-6">
                <h3 className="text-xl font-semibold text-slate-800">4. Uygulanabilirlik Analizi</h3>
                {applicabilityAnalysis && (
                  <div className="bg-slate-50 p-4 rounded-md border border-slate-200">
                    <h4 className="font-medium mb-2 text-slate-800">Uygulanabilirlik Sonuçları:</h4>
                    <div className="space-y-2 text-sm">
                      <div>
                        <span className="font-medium text-slate-700">Uygulanabilirlik Skoru:</span> {applicabilityAnalysis.applicabilityScore}/10
                      </div>
                      <div>
                        <span className="font-medium text-slate-700">Öneri:</span> {applicabilityAnalysis.recommendation}
                      </div>
                      <div>
                        <span className="font-medium text-slate-700">Gerekçe:</span> {applicabilityAnalysis.reasoning}
                      </div>
                    </div>
                  </div>
                )}
                <div className="flex justify-between">
                  <button
                    onClick={() => setCurrentStep('appraisal')}
                    className="bg-slate-600 text-white px-6 py-3 rounded-md hover:bg-slate-700 transition-colors duration-200 font-medium"
                  >
                    Geri
                  </button>
                  <button
                    onClick={performApplicabilityAnalysis}
                    disabled={isLoading}
                    className="bg-green-600 text-white px-6 py-3 rounded-md hover:bg-green-700 disabled:opacity-50 transition-colors duration-200 font-medium"
                  >
                    {isLoading ? 'Analiz Ediliyor...' : 'Analizi Tamamla'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}


