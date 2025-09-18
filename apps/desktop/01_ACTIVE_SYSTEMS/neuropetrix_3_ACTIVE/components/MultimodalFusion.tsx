import React, { useState, useEffect } from 'react';
import { MultimodalData, RadiomicsFeatures, SUVMeasurement } from '../types';

interface MultimodalFusionProps {
  patientCase: any;
  onFusionComplete: (result: any) => void;
}

export default function MultimodalFusion({ patientCase, onFusionComplete }: MultimodalFusionProps) {
  const [multimodalData, setMultimodalData] = useState<MultimodalData | null>(null);
  const [fusionProgress, setFusionProgress] = useState(0);
  const [currentStep, setCurrentStep] = useState<'imaging' | 'clinical' | 'textual' | 'fusion'>('imaging');
  const [isProcessing, setIsProcessing] = useState(false);

  // Görüntü Verilerini İşleme
  const processImagingData = async () => {
    setIsProcessing(true);
    setFusionProgress(25);
    
    try {
      const response = await fetch('/api/multimodal/imaging', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patientId: patientCase.id,
          dicomFiles: patientCase.dicomFiles || []
        })
      });

      const result = await response.json();
      setMultimodalData(prev => ({
        ...prev,
        imaging: result.imaging
      }));
      
      setCurrentStep('clinical');
      setFusionProgress(50);
    } catch (error) {
      console.error('Görüntü işleme hatası:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  // Klinik Verileri İşleme
  const processClinicalData = async () => {
    setIsProcessing(true);
    
    try {
      const response = await fetch('/api/multimodal/clinical', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patientId: patientCase.id,
          demographics: patientCase.patientInfo,
          laboratory: patientCase.laboratory || {},
          medications: patientCase.medications || []
        })
      });

      const result = await response.json();
      setMultimodalData(prev => ({
        ...prev,
        clinical: result.clinical
      }));
      
      setCurrentStep('textual');
      setFusionProgress(75);
    } catch (error) {
      console.error('Klinik veri işleme hatası:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  // Metin Verilerini İşleme
  const processTextualData = async () => {
    setIsProcessing(true);
    
    try {
      const response = await fetch('/api/multimodal/textual', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patientId: patientCase.id,
          clinicalNotes: patientCase.clinicalNotes,
          radiologyReports: patientCase.radiologyReports || [],
          transcribedAudio: patientCase.transcribedAudio || ''
        })
      });

      const result = await response.json();
      setMultimodalData(prev => ({
        ...prev,
        textual: result.textual
      }));
      
      setCurrentStep('fusion');
      setFusionProgress(90);
    } catch (error) {
      console.error('Metin işleme hatası:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  // Multimodal Füzyon
  const performFusion = async () => {
    setIsProcessing(true);
    
    try {
      const response = await fetch('/api/multimodal/fusion', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          multimodalData,
          patientCase
        })
      });

      const result = await response.json();
      setFusionProgress(100);
      
      // Füzyon tamamlandı
      onFusionComplete(result);
    } catch (error) {
      console.error('Füzyon hatası:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Başlık */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-800">
            🔗 Multimodal Füzyon
          </h1>
          <p className="text-slate-600 mt-2">
            Görüntü, klinik ve metin verilerinin entegrasyonu ve analizi
          </p>
        </div>

        {/* Ana İçerik */}
        <div className="bg-white rounded-lg shadow-md border border-slate-200 p-6">
          <h2 className="text-2xl font-bold text-slate-800 mb-6">Multimodal Füzyon Mimarisi</h2>
          
          {/* Progress Bar */}
          <div className="mb-8">
            <div className="flex justify-between text-sm text-slate-600 mb-2">
              <span>Füzyon İlerlemesi</span>
              <span>{fusionProgress}%</span>
            </div>
            <div className="w-full bg-slate-200 rounded-full h-2">
              <div 
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${fusionProgress}%` }}
              ></div>
            </div>
          </div>

        {/* Step Indicators */}
        <div className="grid grid-cols-4 gap-4 mb-8">
          {[
            { key: 'imaging', label: 'Görüntü Verileri', icon: '🖼️' },
            { key: 'clinical', label: 'Klinik Veriler', icon: '🏥' },
            { key: 'textual', label: 'Metin Verileri', icon: '📝' },
            { key: 'fusion', label: 'Füzyon', icon: '🔗' }
          ].map((step) => (
            <div key={step.key} className={`text-center p-4 rounded-lg border-2 ${
              currentStep === step.key 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-slate-200 bg-slate-50'
            }`}>
              <div className="text-2xl mb-2">{step.icon}</div>
              <div className="text-sm font-medium text-slate-700">{step.label}</div>
            </div>
          ))}
        </div>

        {/* Step 1: Imaging Data */}
        {currentStep === 'imaging' && (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-slate-800">1. Görüntü Verileri İşleme</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                <h4 className="font-medium mb-3 text-slate-800">DICOM Dosyaları</h4>
                <div className="space-y-2">
                  {patientCase.dicomFiles?.map((file: string, index: number) => (
                    <div key={index} className="flex items-center text-sm">
                      <span className="text-green-500 mr-2">✓</span>
                      <span className="text-slate-700">{file}</span>
                    </div>
                  )) || (
                    <div className="text-slate-500 text-sm">DICOM dosyası yüklenmedi</div>
                  )}
                </div>
              </div>
              
              <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                <h4 className="font-medium mb-3 text-slate-800">Radyomik Özellikler</h4>
                <div className="space-y-2 text-sm">
                  <div className="text-slate-700">SUV Max: {multimodalData?.imaging?.radiomicsFeatures?.firstOrder?.suvMax || 'Hesaplanıyor...'}</div>
                  <div className="text-slate-700">Hacim: {multimodalData?.imaging?.radiomicsFeatures?.firstOrder?.volume || 'Hesaplanıyor...'}</div>
                  <div className="text-slate-700">Segmentasyon: {multimodalData?.imaging?.segmentationMasks?.length || 0} maske</div>
                </div>
              </div>
            </div>
            
            <button
              onClick={processImagingData}
              disabled={isProcessing}
              className="bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors duration-200 font-medium"
            >
              {isProcessing ? 'İşleniyor...' : 'Görüntü Verilerini İşle'}
            </button>
          </div>
        )}

        {/* Step 2: Clinical Data */}
        {currentStep === 'clinical' && (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-slate-800">2. Klinik Veriler İşleme</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                <h4 className="font-medium mb-3 text-slate-800">Demografik Bilgiler</h4>
                <div className="space-y-1 text-sm">
                  <div className="text-slate-700">Yaş: {patientCase.patientInfo?.age}</div>
                  <div className="text-slate-700">Cinsiyet: {patientCase.patientInfo?.gender}</div>
                  <div className="text-slate-700">BMI: {multimodalData?.clinical?.demographics?.bmi || 'Hesaplanıyor...'}</div>
                </div>
              </div>
              
              <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                <h4 className="font-medium mb-3 text-slate-800">Laboratuvar</h4>
                <div className="space-y-1 text-sm">
                  <div className="text-slate-700">Glukoz: {multimodalData?.clinical?.laboratory?.glucose || 'N/A'}</div>
                  <div className="text-slate-700">Kreatinin: {multimodalData?.clinical?.laboratory?.creatinine || 'N/A'}</div>
                  <div className="text-slate-700">eGFR: {multimodalData?.clinical?.laboratory?.egfr || 'N/A'}</div>
                </div>
              </div>
              
              <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                <h4 className="font-medium mb-3 text-slate-800">İlaçlar</h4>
                <div className="space-y-1 text-sm">
                  {multimodalData?.clinical?.medications?.currentMedications?.map((med: any, index: number) => (
                    <div key={index} className="text-slate-700">{med.name} - {med.dose}</div>
                  )) || <div className="text-slate-500">İlaç bilgisi yok</div>}
                </div>
              </div>
            </div>
            
            <div className="flex justify-between">
              <button
                onClick={() => setCurrentStep('imaging')}
                className="bg-slate-600 text-white px-6 py-3 rounded-md hover:bg-slate-700 transition-colors duration-200 font-medium"
              >
                Geri
              </button>
              <button
                onClick={processClinicalData}
                disabled={isProcessing}
                className="bg-green-600 text-white px-6 py-3 rounded-md hover:bg-green-700 disabled:opacity-50 transition-colors duration-200 font-medium"
              >
                {isProcessing ? 'İşleniyor...' : 'Klinik Verileri İşle'}
              </button>
            </div>
          </div>
        )}

        {/* Step 3: Textual Data */}
        {currentStep === 'textual' && (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-slate-800">3. Metin Verileri İşleme</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                <h4 className="font-medium mb-3 text-slate-800">Klinik Notlar</h4>
                <div className="text-sm text-slate-700 max-h-32 overflow-y-auto">
                  {patientCase.clinicalNotes || 'Klinik not bulunamadı'}
                </div>
              </div>
              
              <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                <h4 className="font-medium mb-3 text-slate-800">Radyoloji Raporları</h4>
                <div className="space-y-2 text-sm">
                  {multimodalData?.textual?.radiologyReports?.map((report: string, index: number) => (
                    <div key={index} className="p-2 bg-white rounded border border-slate-200">
                      <span className="text-slate-700">Rapor {index + 1}: {report.substring(0, 100)}...</span>
                    </div>
                  )) || <div className="text-slate-500">Radyoloji raporu yok</div>}
                </div>
              </div>
            </div>
            
            <div className="flex justify-between">
              <button
                onClick={() => setCurrentStep('clinical')}
                className="bg-slate-600 text-white px-6 py-3 rounded-md hover:bg-slate-700 transition-colors duration-200 font-medium"
              >
                Geri
              </button>
              <button
                onClick={processTextualData}
                disabled={isProcessing}
                className="bg-purple-600 text-white px-6 py-3 rounded-md hover:bg-purple-700 disabled:opacity-50 transition-colors duration-200 font-medium"
              >
                {isProcessing ? 'İşleniyor...' : 'Metin Verilerini İşle'}
              </button>
            </div>
          </div>
        )}

        {/* Step 4: Fusion */}
        {currentStep === 'fusion' && (
          <div className="space-y-6">
            <h3 className="text-xl font-semibold text-slate-800">4. Multimodal Füzyon</h3>
            <div className="bg-blue-50 p-6 rounded-lg border border-blue-200">
              <h4 className="font-medium mb-4 text-slate-800">Füzyon Özeti</h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                <div>
                  <span className="font-medium text-slate-700">Görüntü Verileri:</span>
                  <ul className="mt-1 space-y-1 text-slate-600">
                    <li>• {multimodalData?.imaging?.dicomFiles?.length || 0} DICOM dosyası</li>
                    <li>• {multimodalData?.imaging?.suvMeasurements?.length || 0} SUV ölçümü</li>
                    <li>• {multimodalData?.imaging?.segmentationMasks?.length || 0} segmentasyon</li>
                  </ul>
                </div>
                <div>
                  <span className="font-medium text-slate-700">Klinik Veriler:</span>
                  <ul className="mt-1 space-y-1 text-slate-600">
                    <li>• Demografik bilgiler</li>
                    <li>• {multimodalData?.clinical?.laboratory ? 'Laboratuvar verileri' : 'Laboratuvar yok'}</li>
                    <li>• {multimodalData?.clinical?.medications?.currentMedications?.length || 0} ilaç</li>
                  </ul>
                </div>
                <div>
                  <span className="font-medium text-slate-700">Metin Verileri:</span>
                  <ul className="mt-1 space-y-1 text-slate-600">
                    <li>• Klinik notlar</li>
                    <li>• {multimodalData?.textual?.radiologyReports?.length || 0} radyoloji raporu</li>
                    <li>• Transkripsiyon verileri</li>
                  </ul>
                </div>
              </div>
            </div>
            
            <div className="flex justify-between">
              <button
                onClick={() => setCurrentStep('textual')}
                className="bg-slate-600 text-white px-6 py-3 rounded-md hover:bg-slate-700 transition-colors duration-200 font-medium"
              >
                Geri
              </button>
              <button
                onClick={performFusion}
                disabled={isProcessing}
                className="bg-orange-600 text-white px-6 py-3 rounded-md hover:bg-orange-700 disabled:opacity-50 transition-colors duration-200 font-medium"
              >
                {isProcessing ? 'Füzyon Yapılıyor...' : 'Füzyonu Başlat'}
              </button>
            </div>
          </div>
        )}
        </div>
      </div>
    </div>
  );
}
