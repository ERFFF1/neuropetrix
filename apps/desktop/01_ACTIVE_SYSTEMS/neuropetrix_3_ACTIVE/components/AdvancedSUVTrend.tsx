import React, { useState, useEffect } from 'react';
import { getClinicalCriteriaService, PERCISTCriteria, DeauvilleCriteria, ResponseAssessment } from '../services/clinicalCriteriaService';
import { getDICOMService, SUVCalculation } from '../services/dicomService';

interface AdvancedSUVTrendProps {
  patientCase: any;
}

export default function AdvancedSUVTrend({ patientCase }: AdvancedSUVTrendProps) {
  const [baselineSUV, setBaselineSUV] = useState<number>(0);
  const [currentSUV, setCurrentSUV] = useState<number>(0);
  const [liverSUV, setLiverSUV] = useState<number>(2.0);
  const [assessment, setAssessment] = useState<ResponseAssessment | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showAdvanced, setShowAdvanced] = useState(false);

  const clinicalService = getClinicalCriteriaService();
  const dicomService = getDICOMService();

  useEffect(() => {
    clinicalService.initialize();
    dicomService.initialize();
  }, []);

  const performAssessment = async () => {
    if (!baselineSUV || !currentSUV) {
      alert('Lütfen baseline ve current SUV değerlerini girin');
      return;
    }

    setIsLoading(true);
    try {
      // PERCIST kriterleri uygula
      const perCIST = await clinicalService.applyPERCISTCriteria(baselineSUV, currentSUV);
      
      // Deauville kriterleri uygula (opsiyonel)
      let deauville: DeauvilleCriteria | undefined;
      if (liverSUV > 0) {
        deauville = await clinicalService.applyDeauvilleCriteria(liverSUV, currentSUV);
      }

      // Genel yanıt değerlendirmesi
      const overallAssessment = await clinicalService.assessOverallResponse(perCIST, deauville);
      
      setAssessment(overallAssessment);
    } catch (error) {
      console.error('Assessment failed:', error);
      alert('Değerlendirme sırasında hata oluştu');
    } finally {
      setIsLoading(false);
    }
  };

  const generateReport = async () => {
    if (!assessment) return;

    try {
      const report = await clinicalService.generateClinicalReport(assessment);
      
      // Raporu indir
      const blob = new Blob([report], { type: 'text/markdown' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `SUV_Assessment_${patientCase?.patient?.name || 'Unknown'}.md`;
      link.click();
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Report generation failed:', error);
      alert('Rapor oluşturulamadı');
    }
  };

  const getResponseColor = (response: string) => {
    switch (response) {
      case 'CR': return 'text-green-600 bg-green-100';
      case 'PR': return 'text-blue-600 bg-blue-100';
      case 'SD': return 'text-yellow-600 bg-yellow-100';
      case 'PD': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getDeauvilleColor = (score: number) => {
    if (score <= 2) return 'text-green-600 bg-green-100';
    if (score === 3) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <div className="min-h-screen bg-medical-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-medical-900 mb-2">
            Gelişmiş SUV Trend Analizi
          </h1>
          <p className="text-medical-600">
            PERCIST ve Deauville kriterleri ile klinik yanıt değerlendirmesi
          </p>
        </div>

        {/* Input Panel */}
        <div className="bg-white rounded-lg shadow-sm border border-medical-200 p-6 mb-6">
          <h2 className="text-xl font-semibold text-medical-900 mb-4">SUV Değerleri</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-medical-700 mb-2">
                Baseline SUV Max
              </label>
              <input
                type="number"
                step="0.1"
                value={baselineSUV}
                onChange={(e) => setBaselineSUV(parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500"
                placeholder="8.5"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-medical-700 mb-2">
                Current SUV Max
              </label>
              <input
                type="number"
                step="0.1"
                value={currentSUV}
                onChange={(e) => setCurrentSUV(parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500"
                placeholder="6.2"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-medical-700 mb-2">
                Karaciğer SUV Max (Deauville)
              </label>
              <input
                type="number"
                step="0.1"
                value={liverSUV}
                onChange={(e) => setLiverSUV(parseFloat(e.target.value) || 0)}
                className="w-full px-3 py-2 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500"
                placeholder="2.0"
              />
            </div>
          </div>

          <div className="flex space-x-4">
            <button
              onClick={performAssessment}
              disabled={isLoading || !baselineSUV || !currentSUV}
              className="bg-medical-600 text-white px-6 py-2 rounded-md hover:bg-medical-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isLoading ? 'Değerlendiriliyor...' : 'Değerlendir'}
            </button>

            <button
              onClick={() => setShowAdvanced(!showAdvanced)}
              className="bg-purple-600 text-white px-6 py-2 rounded-md hover:bg-purple-700 transition-colors"
            >
              {showAdvanced ? 'Gelişmiş Gizle' : 'Gelişmiş Göster'}
            </button>
          </div>
        </div>

        {/* Assessment Results */}
        {assessment && (
          <div className="bg-white rounded-lg shadow-sm border border-medical-200 p-6 mb-6">
            <h2 className="text-xl font-semibold text-medical-900 mb-4">Değerlendirme Sonuçları</h2>
            
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* PERCIST Results */}
              <div className="space-y-4">
                <h3 className="text-lg font-medium text-medical-800">PERCIST Kriterleri</h3>
                
                <div className="space-y-3">
                  <div className="flex justify-between items-center p-3 bg-medical-50 rounded-lg">
                    <span className="font-medium text-medical-700">Yanıt:</span>
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getResponseColor(assessment.perCIST.response)}`}>
                      {assessment.perCIST.response}
                    </span>
                  </div>

                  <div className="flex justify-between items-center p-3 bg-medical-50 rounded-lg">
                    <span className="font-medium text-medical-700">Değişim:</span>
                    <span className={`text-lg font-bold ${
                      assessment.perCIST.changePercent <= -30 ? 'text-green-600' : 
                      assessment.perCIST.changePercent >= 30 ? 'text-red-600' : 'text-yellow-600'
                    }`}>
                      {assessment.perCIST.changePercent > 0 ? '+' : ''}{assessment.perCIST.changePercent.toFixed(1)}%
                    </span>
                  </div>

                  <div className="flex justify-between items-center p-3 bg-medical-50 rounded-lg">
                    <span className="font-medium text-medical-700">Güven:</span>
                    <span className="text-lg font-bold text-medical-600">
                      {(assessment.perCIST.confidence * 100).toFixed(1)}%
                    </span>
                  </div>
                </div>

                <div className="p-3 bg-medical-50 rounded-lg">
                  <p className="text-sm text-medical-700">{assessment.perCIST.reasoning}</p>
                </div>
              </div>

              {/* Deauville Results */}
              {assessment.deauville && (
                <div className="space-y-4">
                  <h3 className="text-lg font-medium text-medical-800">Deauville Kriterleri</h3>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between items-center p-3 bg-medical-50 rounded-lg">
                      <span className="font-medium text-medical-700">Skor:</span>
                      <span className={`px-3 py-1 rounded-full text-sm font-medium ${getDeauvilleColor(assessment.deauville.score)}`}>
                        {assessment.deauville.score}/5
                      </span>
                    </div>

                    <div className="p-3 bg-medical-50 rounded-lg">
                      <p className="text-sm text-medical-700">{assessment.deauville.interpretation}</p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* Overall Assessment */}
            <div className="mt-6 p-4 bg-medical-100 rounded-lg">
              <h3 className="text-lg font-medium text-medical-800 mb-3">Genel Değerlendirme</h3>
              
              <div className="flex justify-between items-center mb-4">
                <span className="font-medium text-medical-700">Yanıt:</span>
                <span className="text-xl font-bold text-medical-900">
                  {assessment.overallResponse}
                </span>
              </div>

              <div className="flex justify-between items-center mb-4">
                <span className="font-medium text-medical-700">Güven:</span>
                <span className="text-lg font-bold text-medical-600">
                  {(assessment.confidence * 100).toFixed(1)}%
                </span>
              </div>

              <div className="space-y-2">
                <h4 className="font-medium text-medical-700">Sonraki Adımlar:</h4>
                {assessment.nextSteps.map((step, index) => (
                  <div key={index} className="flex items-start space-x-2">
                    <span className="text-medical-500 mt-1">•</span>
                    <span className="text-sm text-medical-700">{step}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="mt-6 flex space-x-4">
              <button
                onClick={generateReport}
                className="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 transition-colors"
              >
                Rapor İndir
              </button>

              <button
                onClick={() => setAssessment(null)}
                className="bg-gray-600 text-white px-6 py-2 rounded-md hover:bg-gray-700 transition-colors"
              >
                Yeni Değerlendirme
              </button>
            </div>
          </div>
        )}

        {/* Advanced Features */}
        {showAdvanced && (
          <div className="bg-white rounded-lg shadow-sm border border-medical-200 p-6">
            <h2 className="text-xl font-semibold text-medical-900 mb-4">Gelişmiş Özellikler</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-medium text-medical-800 mb-3">PERCIST Detayları</h3>
                <div className="space-y-2 text-sm text-medical-600">
                  <p>• <strong>CR:</strong> SUV Max ≤ 1.5 ve %30'dan fazla azalma</p>
                  <p>• <strong>PR:</strong> SUV Max %30'dan fazla azalma</p>
                  <p>• <strong>SD:</strong> SUV Max değişimi %30'dan az</p>
                  <p>• <strong>PD:</strong> SUV Max %30'dan fazla artma</p>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-medium text-medical-800 mb-3">Deauville Skorları</h3>
                <div className="space-y-2 text-sm text-medical-600">
                  <p>• <strong>1-2:</strong> Normal/Minimal aktivite</p>
                  <p>• <strong>3:</strong> Orta aktivite (belirsiz)</p>
                  <p>• <strong>4-5:</strong> Yüksek aktivite (progresif)</p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}


