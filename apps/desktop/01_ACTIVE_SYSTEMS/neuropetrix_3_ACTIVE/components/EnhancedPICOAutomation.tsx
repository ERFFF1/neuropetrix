import React, { useState, useEffect } from 'react';
import { getClinicalCriteriaService } from '../services/clinicalCriteriaService';

interface PICOStep {
  id: string;
  title: string;
  description: string;
  completed: boolean;
  data: any;
}

interface PICOQuestion {
  population: string;
  intervention: string;
  comparison: string;
  outcome: string;
  timeFrame: string;
  setting: string;
}

interface EvidenceSearch {
  query: string;
  databases: string[];
  filters: {
    publicationType: string[];
    dateRange: string;
    studyType: string[];
  };
  results: Array<{
    title: string;
    authors: string[];
    journal: string;
    year: number;
    abstract: string;
    relevance: number;
    evidenceLevel: string;
  }>;
}

interface CriticalAppraisal {
  studyDesign: string;
  sampleSize: number;
  biasAssessment: {
    selection: number;
    performance: number;
    detection: number;
    attrition: number;
    reporting: number;
  };
  overallQuality: number;
  limitations: string[];
  strengths: string[];
}

interface ApplicabilityAnalysis {
  patientSimilarity: number;
  settingRelevance: number;
  outcomeRelevance: number;
  interventionFeasibility: number;
  overallApplicability: number;
  recommendations: string[];
}

export default function EnhancedPICOAutomation() {
  const [currentStep, setCurrentStep] = useState(0);
  const [steps, setSteps] = useState<PICOStep[]>([
    {
      id: 'pico',
      title: 'PICO Soru Oluşturma',
      description: 'Klinik problemi PICO formatında yapılandırın',
      completed: false,
      data: {}
    },
    {
      id: 'search',
      title: 'Kanıt Arama',
      description: 'Literatürde en iyi kanıtları bulun',
      completed: false,
      data: {}
    },
    {
      id: 'appraisal',
      title: 'Kritik Değerlendirme',
      description: 'Kanıtın kalitesini ve güvenilirliğini değerlendirin',
      completed: false,
      data: {}
    },
    {
      id: 'applicability',
      title: 'Uygulanabilirlik Analizi',
      description: 'Kanıtın hasta özelinde uygulanabilirliğini analiz edin',
      completed: false,
      data: {}
    },
    {
      id: 'recommendation',
      title: 'Klinik Öneri',
      description: 'Kanıta dayalı klinik öneri oluşturun',
      completed: false,
      data: {}
    }
  ]);

  const [picoData, setPicoData] = useState<PICOQuestion>({
    population: '',
    intervention: '',
    comparison: '',
    outcome: '',
    timeFrame: '',
    setting: ''
  });

  const [evidenceData, setEvidenceData] = useState<EvidenceSearch>({
    query: '',
    databases: ['PubMed', 'Cochrane', 'Embase'],
    filters: {
      publicationType: ['Randomized Controlled Trial', 'Systematic Review'],
      dateRange: '5 years',
      studyType: ['RCT', 'Meta-analysis']
    },
    results: []
  });

  const [appraisalData, setAppraisalData] = useState<CriticalAppraisal>({
    studyDesign: '',
    sampleSize: 0,
    biasAssessment: {
      selection: 0,
      performance: 0,
      detection: 0,
      attrition: 0,
      reporting: 0
    },
    overallQuality: 0,
    limitations: [],
    strengths: []
  });

  const [applicabilityData, setApplicabilityData] = useState<ApplicabilityAnalysis>({
    patientSimilarity: 0,
    settingRelevance: 0,
    outcomeRelevance: 0,
    interventionFeasibility: 0,
    overallApplicability: 0,
    recommendations: []
  });

  const [isLoading, setIsLoading] = useState(false);

  const clinicalService = getClinicalCriteriaService();

  useEffect(() => {
    clinicalService.initialize();
  }, []);

  const generatePICOQuestion = async () => {
    if (!picoData.population || !picoData.intervention || !picoData.outcome) {
      alert('Lütfen en az Population, Intervention ve Outcome alanlarını doldurun');
      return;
    }

    setIsLoading(true);
    try {
      // AI ile PICO sorusu geliştirme simülasyonu
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const enhancedPICO = {
        ...picoData,
        enhancedPopulation: `${picoData.population} (${picoData.setting})`,
        enhancedIntervention: `${picoData.intervention} (${picoData.timeFrame})`,
        enhancedComparison: picoData.comparison || 'Standard treatment',
        enhancedOutcome: `${picoData.outcome} (measured over ${picoData.timeFrame})`
      };

      setPicoData(enhancedPICO);
      completeStep(0, enhancedPICO);
    } catch (error) {
      console.error('PICO generation failed:', error);
      alert('PICO sorusu oluşturulamadı');
    } finally {
      setIsLoading(false);
    }
  };

  const performEvidenceSearch = async () => {
    if (!evidenceData.query) {
      alert('Lütfen arama sorgusu girin');
      return;
    }

    setIsLoading(true);
    try {
      // Kanıt arama simülasyonu
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      const mockResults = [
        {
          title: "Randomized trial of chemotherapy vs. immunotherapy in advanced NSCLC",
          authors: ["Smith J", "Johnson A", "Brown K"],
          journal: "New England Journal of Medicine",
          year: 2023,
          abstract: "This randomized controlled trial compared chemotherapy with immunotherapy in patients with advanced non-small cell lung cancer...",
          relevance: 0.95,
          evidenceLevel: "Level 1"
        },
        {
          title: "Systematic review of targeted therapies in lung cancer",
          authors: ["Davis M", "Wilson R", "Taylor S"],
          journal: "Lancet Oncology",
          year: 2022,
          abstract: "A comprehensive systematic review of targeted therapies for lung cancer treatment...",
          relevance: 0.88,
          evidenceLevel: "Level 1"
        }
      ];

      setEvidenceData(prev => ({
        ...prev,
        results: mockResults
      }));

      completeStep(1, { ...evidenceData, results: mockResults });
    } catch (error) {
      console.error('Evidence search failed:', error);
      alert('Kanıt arama sırasında hata oluştu');
    } finally {
      setIsLoading(false);
    }
  };

  const performCriticalAppraisal = async () => {
    if (evidenceData.results.length === 0) {
      alert('Önce kanıt arama yapın');
      return;
    }

    setIsLoading(true);
    try {
      // Kritik değerlendirme simülasyonu
      await new Promise(resolve => setTimeout(resolve, 2500));
      
      const appraisal = {
        studyDesign: "Randomized Controlled Trial",
        sampleSize: 450,
        biasAssessment: {
          selection: 0.8,
          performance: 0.9,
          detection: 0.85,
          attrition: 0.7,
          reporting: 0.9
        },
        overallQuality: 0.83,
        limitations: [
          "Single-center study",
          "Limited follow-up period",
          "Heterogeneous patient population"
        ],
        strengths: [
          "Randomized design",
          "Blinded outcome assessment",
          "Intention-to-treat analysis"
        ]
      };

      setAppraisalData(appraisal);
      completeStep(2, appraisal);
    } catch (error) {
      console.error('Critical appraisal failed:', error);
      alert('Kritik değerlendirme sırasında hata oluştu');
    } finally {
      setIsLoading(false);
    }
  };

  const performApplicabilityAnalysis = async () => {
    if (!appraisalData.studyDesign) {
      alert('Önce kritik değerlendirme yapın');
      return;
    }

    setIsLoading(true);
    try {
      // Uygulanabilirlik analizi simülasyonu
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const applicability = {
        patientSimilarity: 0.85,
        settingRelevance: 0.90,
        outcomeRelevance: 0.95,
        interventionFeasibility: 0.80,
        overallApplicability: 0.88,
        recommendations: [
          "Intervention is highly applicable to current patient",
          "Consider patient comorbidities before implementation",
          "Monitor response closely during first 2 weeks",
          "Adjust dosage based on patient tolerance"
        ]
      };

      setApplicabilityData(applicability);
      completeStep(3, applicability);
    } catch (error) {
      console.error('Applicability analysis failed:', error);
      alert('Uygulanabilirlik analizi sırasında hata oluştu');
    } finally {
      setIsLoading(false);
    }
  };

  const generateClinicalRecommendation = async () => {
    if (!applicabilityData.overallApplicability) {
      alert('Önce uygulanabilirlik analizi yapın');
      return;
    }

    setIsLoading(true);
    try {
      // Klinik öneri oluşturma simülasyonu
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      const recommendation = {
        strength: "Strong recommendation",
        confidence: "High confidence",
        summary: "Based on high-quality evidence and high applicability, recommend implementing the intervention",
        details: [
          "Start with standard dosage",
          "Monitor response at 2-week intervals",
          "Adjust based on patient response and side effects",
          "Consider discontinuation if no response after 8 weeks"
        ],
        evidenceLevel: "Level 1 evidence",
        applicabilityScore: `${(applicabilityData.overallApplicability * 100).toFixed(0)}%`
      };

      completeStep(4, recommendation);
    } catch (error) {
      console.error('Recommendation generation failed:', error);
      alert('Klinik öneri oluşturulamadı');
    } finally {
      setIsLoading(false);
    }
  };

  const completeStep = (stepIndex: number, data: any) => {
    setSteps(prev => prev.map((step, index) => 
      index === stepIndex ? { ...step, completed: true, data } : step
    ));
    
    if (stepIndex < steps.length - 1) {
      setCurrentStep(stepIndex + 1);
    }
  };

  const goToStep = (stepIndex: number) => {
    if (stepIndex <= currentStep || steps[stepIndex - 1]?.completed) {
      setCurrentStep(stepIndex);
    }
  };

  const renderStepContent = () => {
    switch (currentStep) {
      case 0:
        return (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-medical-900">PICO Soru Oluşturma</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-medical-700 mb-2">
                  Population (Hasta Grubu)
                </label>
                <input
                  type="text"
                  value={picoData.population}
                  onChange={(e) => setPicoData(prev => ({ ...prev, population: e.target.value }))}
                  className="w-full px-3 py-2 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500"
                  placeholder="Örn: 65 yaş üstü, metastatik akciğer kanseri"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-medical-700 mb-2">
                  Intervention (Müdahale)
                </label>
                <input
                  type="text"
                  value={picoData.intervention}
                  onChange={(e) => setPicoData(prev => ({ ...prev, intervention: e.target.value }))}
                  className="w-full px-3 py-2 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500"
                  placeholder="Örn: İmmunoterapi + kemoterapi"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-medical-700 mb-2">
                  Comparison (Karşılaştırma)
                </label>
                <input
                  type="text"
                  value={picoData.comparison}
                  onChange={(e) => setPicoData(prev => ({ ...prev, comparison: e.target.value }))}
                  className="w-full px-3 py-2 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500"
                  placeholder="Örn: Sadece kemoterapi"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-medical-700 mb-2">
                  Outcome (Sonuç)
                </label>
                <input
                  type="text"
                  value={picoData.outcome}
                  onChange={(e) => setPicoData(prev => ({ ...prev, outcome: e.target.value }))}
                  className="w-full px-3 py-2 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500"
                  placeholder="Örn: Genel sağkalım"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-medical-700 mb-2">
                  Time Frame (Zaman Aralığı)
                </label>
                <input
                  type="text"
                  value={picoData.timeFrame}
                  onChange={(e) => setPicoData(prev => ({ ...prev, timeFrame: e.target.value }))}
                  className="w-full px-3 py-2 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500"
                  placeholder="Örn: 12 ay"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-medical-700 mb-2">
                  Setting (Ortam)
                </label>
                <input
                  type="text"
                  value={picoData.setting}
                  onChange={(e) => setPicoData(prev => ({ ...prev, setting: e.target.value }))}
                  className="w-full px-3 py-2 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500"
                  placeholder="Örn: Üçüncü basamak hastane"
                />
              </div>
            </div>

            <button
              onClick={generatePICOQuestion}
              disabled={isLoading}
              className="bg-medical-600 text-white px-6 py-2 rounded-md hover:bg-medical-700 disabled:opacity-50 transition-colors"
            >
              {isLoading ? 'Oluşturuluyor...' : 'PICO Sorusu Oluştur'}
            </button>
          </div>
        );

      case 1:
        return (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-medical-900">Kanıt Arama</h3>
            
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-medical-700 mb-2">
                  Arama Sorgusu
                </label>
                <input
                  type="text"
                  value={evidenceData.query}
                  onChange={(e) => setEvidenceData(prev => ({ ...prev, query: e.target.value }))}
                  className="w-full px-3 py-2 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500"
                  placeholder="Otomatik olarak PICO'dan oluşturulacak"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-medical-700 mb-2">
                  Veritabanları
                </label>
                <div className="flex flex-wrap gap-2">
                  {evidenceData.databases.map((db) => (
                    <span key={db} className="px-3 py-1 bg-medical-100 text-medical-800 rounded-full text-sm">
                      {db}
                    </span>
                  ))}
                </div>
              </div>

              <button
                onClick={performEvidenceSearch}
                disabled={isLoading}
                className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
              >
                {isLoading ? 'Aranıyor...' : 'Kanıt Ara'}
              </button>

              {evidenceData.results.length > 0 && (
                <div className="space-y-4">
                  <h4 className="font-medium text-medical-800">Arama Sonuçları</h4>
                  {evidenceData.results.map((result, index) => (
                    <div key={index} className="p-4 bg-medical-50 rounded-lg">
                      <h5 className="font-medium text-medical-900 mb-2">{result.title}</h5>
                      <p className="text-sm text-medical-600 mb-2">
                        {result.authors.join(', ')} - {result.journal} ({result.year})
                      </p>
                      <p className="text-sm text-medical-700 mb-2">{result.abstract}</p>
                      <div className="flex justify-between items-center">
                        <span className="text-sm text-medical-600">
                          Kanıt Seviyesi: {result.evidenceLevel}
                        </span>
                        <span className="text-sm font-medium text-medical-800">
                          İlgi: {(result.relevance * 100).toFixed(0)}%
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        );

      case 2:
        return (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-medical-900">Kritik Değerlendirme</h3>
            
            {appraisalData.studyDesign ? (
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <span className="text-sm font-medium text-medical-600">Çalışma Tasarımı:</span>
                    <p className="text-medical-900">{appraisalData.studyDesign}</p>
                  </div>
                  <div>
                    <span className="text-sm font-medium text-medical-600">Örneklem Büyüklüğü:</span>
                    <p className="text-medical-900">{appraisalData.sampleSize}</p>
                  </div>
                </div>

                <div>
                  <h4 className="font-medium text-medical-800 mb-3">Bias Değerlendirmesi</h4>
                  <div className="space-y-2">
                    {Object.entries(appraisalData.biasAssessment).map(([key, value]) => (
                      <div key={key} className="flex justify-between items-center">
                        <span className="text-sm text-medical-600 capitalize">{key}:</span>
                        <div className="flex items-center space-x-2">
                          <div className="w-20 bg-medical-200 rounded-full h-2">
                            <div 
                              className="bg-medical-600 h-2 rounded-full"
                              style={{ width: `${value * 100}%` }}
                            ></div>
                          </div>
                          <span className="text-sm font-medium text-medical-800">
                            {(value * 100).toFixed(0)}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <h4 className="font-medium text-medical-800 mb-2">Güçlü Yönler</h4>
                    <ul className="space-y-1">
                      {appraisalData.strengths.map((strength, index) => (
                        <li key={index} className="text-sm text-medical-700 flex items-start">
                          <span className="text-green-500 mr-2">✓</span>
                          {strength}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-medium text-medical-800 mb-2">Sınırlamalar</h4>
                    <ul className="space-y-1">
                      {appraisalData.limitations.map((limitation, index) => (
                        <li key={index} className="text-sm text-medical-700 flex items-start">
                          <span className="text-red-500 mr-2">⚠</span>
                          {limitation}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="p-4 bg-medical-100 rounded-lg">
                  <span className="text-sm font-medium text-medical-700">Genel Kalite Skoru:</span>
                  <span className="ml-2 text-lg font-bold text-medical-900">
                    {(appraisalData.overallQuality * 100).toFixed(0)}%
                  </span>
                </div>
              </div>
            ) : (
              <button
                onClick={performCriticalAppraisal}
                disabled={isLoading}
                className="bg-purple-600 text-white px-6 py-2 rounded-md hover:bg-purple-700 disabled:opacity-50 transition-colors"
              >
                {isLoading ? 'Değerlendiriliyor...' : 'Kritik Değerlendirme Yap'}
              </button>
            )}
          </div>
        );

      case 3:
        return (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-medical-900">Uygulanabilirlik Analizi</h3>
            
            {applicabilityData.overallApplicability > 0 ? (
              <div className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-medical-50 rounded-lg">
                    <span className="text-sm font-medium text-medical-600">Hasta Benzerliği</span>
                    <div className="flex items-center space-x-2 mt-2">
                      <div className="flex-1 bg-medical-200 rounded-full h-3">
                        <div 
                          className="bg-green-600 h-3 rounded-full"
                          style={{ width: `${applicabilityData.patientSimilarity * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium text-medical-900">
                        {(applicabilityData.patientSimilarity * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>

                  <div className="p-4 bg-medical-50 rounded-lg">
                    <span className="text-sm font-medium text-medical-600">Ortam Uygunluğu</span>
                    <div className="flex items-center space-x-2 mt-2">
                      <div className="flex-1 bg-medical-200 rounded-full h-3">
                        <div 
                          className="bg-blue-600 h-3 rounded-full"
                          style={{ width: `${applicabilityData.settingRelevance * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium text-medical-900">
                        {(applicabilityData.settingRelevance * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>

                  <div className="p-4 bg-medical-50 rounded-lg">
                    <span className="text-sm font-medium text-medical-600">Sonuç Uygunluğu</span>
                    <div className="flex items-center space-x-2 mt-2">
                      <div className="flex-1 bg-medical-200 rounded-full h-3">
                        <div 
                          className="bg-indigo-600 h-3 rounded-full"
                          style={{ width: `${applicabilityData.outcomeRelevance * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium text-medical-900">
                        {(applicabilityData.outcomeRelevance * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>

                  <div className="p-4 bg-medical-50 rounded-lg">
                    <span className="text-sm font-medium text-medical-600">Müdahale Uygulanabilirliği</span>
                    <div className="flex items-center space-x-2 mt-2">
                      <div className="flex-1 bg-medical-200 rounded-full h-3">
                        <div 
                          className="bg-yellow-600 h-3 rounded-full"
                          style={{ width: `${applicabilityData.interventionFeasibility * 100}%` }}
                        ></div>
                      </div>
                      <span className="text-sm font-medium text-medical-900">
                        {(applicabilityData.interventionFeasibility * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                </div>

                <div className="p-4 bg-medical-100 rounded-lg">
                  <span className="text-sm font-medium text-medical-700">Genel Uygulanabilirlik:</span>
                  <span className="ml-2 text-lg font-bold text-medical-900">
                    {(applicabilityData.overallApplicability * 100).toFixed(0)}%
                  </span>
                </div>

                <div>
                  <h4 className="font-medium text-medical-800 mb-3">Öneriler</h4>
                  <ul className="space-y-2">
                    {applicabilityData.recommendations.map((rec, index) => (
                      <li key={index} className="text-sm text-medical-700 flex items-start">
                        <span className="text-medical-500 mr-2">•</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            ) : (
              <button
                onClick={performApplicabilityAnalysis}
                disabled={isLoading}
                className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 disabled:opacity-50 transition-colors"
              >
                {isLoading ? 'Analiz Ediliyor...' : 'Uygulanabilirlik Analizi Yap'}
              </button>
            )}
          </div>
        );

      case 4:
        return (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-medical-900">Klinik Öneri</h3>
            
            <button
              onClick={generateClinicalRecommendation}
              disabled={isLoading}
              className="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 disabled:opacity-50 transition-colors"
            >
              {isLoading ? 'Oluşturuluyor...' : 'Klinik Öneri Oluştur'}
            </button>

            {steps[4].data && (
              <div className="space-y-4">
                <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                  <h4 className="font-medium text-green-800 mb-2">Öneri Gücü</h4>
                  <p className="text-green-700">{steps[4].data.strength}</p>
                </div>

                <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <h4 className="font-medium text-blue-800 mb-2">Güven Seviyesi</h4>
                  <p className="text-blue-700">{steps[4].data.confidence}</p>
                </div>

                <div className="p-4 bg-medical-50 border border-medical-200 rounded-lg">
                  <h4 className="font-medium text-medical-800 mb-2">Özet</h4>
                  <p className="text-medical-700">{steps[4].data.summary}</p>
                </div>

                <div>
                  <h4 className="font-medium text-medical-800 mb-3">Detaylar</h4>
                  <ul className="space-y-2">
                    {steps[4].data.details.map((detail, index) => (
                      <li key={index} className="text-sm text-medical-700 flex items-start">
                        <span className="text-medical-500 mr-2">•</span>
                        {detail}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-3 bg-medical-100 rounded-lg">
                    <span className="text-sm font-medium text-medical-600">Kanıt Seviyesi:</span>
                    <p className="text-medical-900 font-medium">{steps[4].data.evidenceLevel}</p>
                  </div>
                  <div className="p-3 bg-medical-100 rounded-lg">
                    <span className="text-sm font-medium text-medical-600">Uygulanabilirlik:</span>
                    <p className="text-medical-900 font-medium">{steps[4].data.applicabilityScore}</p>
                  </div>
                </div>
              </div>
            )}
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="min-h-screen bg-medical-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-medical-900 mb-2">
            Gelişmiş PICO Otomasyonu
          </h1>
          <p className="text-medical-600">
            Kanıta dayalı tıp sürecini otomatikleştirin ve klinik kararları optimize edin
          </p>
        </div>

        {/* Progress Steps */}
        <div className="bg-white rounded-lg shadow-sm border border-medical-200 p-6 mb-6">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <div key={step.id} className="flex items-center">
                <button
                  onClick={() => goToStep(index)}
                  disabled={!step.completed && index > currentStep}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
                    index === currentStep
                      ? 'bg-medical-600 text-white'
                      : step.completed
                      ? 'bg-green-100 text-green-800 hover:bg-green-200'
                      : 'bg-gray-100 text-gray-400 cursor-not-allowed'
                  }`}
                >
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center text-sm font-medium ${
                    step.completed ? 'bg-green-600 text-white' : 'bg-gray-300 text-gray-600'
                  }`}>
                    {step.completed ? '✓' : index + 1}
                  </div>
                  <span className="hidden md:block">{step.title}</span>
                </button>
                
                {index < steps.length - 1 && (
                  <div className={`w-8 h-0.5 mx-2 ${
                    step.completed ? 'bg-green-400' : 'bg-gray-300'
                  }`}></div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Step Content */}
        <div className="bg-white rounded-lg shadow-sm border border-medical-200 p-6">
          {renderStepContent()}
        </div>

        {/* Navigation */}
        <div className="flex justify-between mt-6">
          <button
            onClick={() => setCurrentStep(Math.max(0, currentStep - 1))}
            disabled={currentStep === 0}
            className="bg-gray-600 text-white px-6 py-2 rounded-md hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Önceki
          </button>
          
          <button
            onClick={() => setCurrentStep(Math.min(steps.length - 1, currentStep + 1))}
            disabled={currentStep === steps.length - 1}
            className="bg-medical-600 text-white px-6 py-2 rounded-md hover:bg-medical-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            Sonraki
          </button>
        </div>
      </div>
    </div>
  );
}

