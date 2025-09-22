import React, { useState, useEffect, useRef } from 'react';
import { getDICOMService, DICOMAnalysisResult, SUVCalculation } from '../services/dicomService';

interface DICOMViewerProps {
  onAnalysisComplete?: (result: DICOMAnalysisResult) => void;
}

export default function DICOMViewer({ onAnalysisComplete }: DICOMViewerProps) {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<DICOMAnalysisResult | null>(null);
  const [currentStep, setCurrentStep] = useState<'upload' | 'processing' | 'analysis' | 'complete'>('upload');
  const [progress, setProgress] = useState(0);
  const [previewUrl, setPreviewUrl] = useState<string>('');
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const dicomService = getDICOMService();

  useEffect(() => {
    dicomService.initialize();
  }, []);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.name.toLowerCase().endsWith('.dcm')) {
      setSelectedFile(file);
      setCurrentStep('upload');
      
      // Preview oluştur
      const url = URL.createObjectURL(file);
      setPreviewUrl(url);
    } else {
      alert('Lütfen geçerli bir DICOM (.dcm) dosyası seçin');
    }
  };

  const processDICOM = async () => {
    if (!selectedFile) return;

    setIsProcessing(true);
    setCurrentStep('processing');
    setProgress(0);

    try {
      // Progress simulation
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 300);

      // DICOM işleme
      const result = await dicomService.processDICOMFile(selectedFile);
      
      clearInterval(progressInterval);
      setProgress(100);
      setCurrentStep('analysis');
      
      // Sonuçları göster
      setAnalysisResult(result);
      setCurrentStep('complete');
      
      if (onAnalysisComplete) {
        onAnalysisComplete(result);
      }

    } catch (error) {
      console.error('DICOM processing failed:', error);
      alert('DICOM işleme sırasında hata oluştu');
    } finally {
      setIsProcessing(false);
    }
  };

  const calculateSUV = async (region: string) => {
    if (!analysisResult) return;

    try {
      // Mock image data
      const mockImageData = new ImageData(512, 512);
      const suvResult = await dicomService.calculateSUV(mockImageData, region);
      
      // SUV sonucunu güncelle
      setAnalysisResult(prev => {
        if (!prev) return prev;
        return {
          ...prev,
          suvCalculations: [...prev.suvCalculations, suvResult]
        };
      });
    } catch (error) {
      console.error('SUV calculation failed:', error);
      alert('SUV hesaplama sırasında hata oluştu');
    }
  };

  const applyPERCIST = async () => {
    if (!analysisResult || analysisResult.suvCalculations.length < 2) {
      alert('PERCIST analizi için en az 2 SUV ölçümü gerekli');
      return;
    }

    try {
      const baseline = analysisResult.suvCalculations[0];
      const current = analysisResult.suvCalculations[analysisResult.suvCalculations.length - 1];
      
      const perCISTResult = await dicomService.applyPERCISTCriteria(
        baseline.suvMax,
        current.suvMax
      );

      alert(`PERCIST Sonucu: ${perCISTResult.response}\nGüven: ${(perCISTResult.confidence * 100).toFixed(1)}%\nAçıklama: ${perCISTResult.reasoning}`);
    } catch (error) {
      console.error('PERCIST analysis failed:', error);
      alert('PERCIST analizi sırasında hata oluştu');
    }
  };

  const generate3DVisualization = async () => {
    if (!analysisResult) return;

    try {
      const visualization = await dicomService.generate3DVisualization(analysisResult);
      
      // 3D görselleştirmeyi yeni sekmede aç
      const newWindow = window.open('', '_blank');
      if (newWindow) {
        newWindow.document.write(`
          <html>
            <head><title>3D DICOM Visualization</title></head>
            <body style="margin:0; background:black;">
              <img src="${visualization}" style="width:100%; height:100vh; object-fit:contain;" />
            </body>
          </html>
        `);
      }
    } catch (error) {
      console.error('3D visualization failed:', error);
      alert('3D görselleştirme oluşturulamadı');
    }
  };

  const resetViewer = () => {
    setSelectedFile(null);
    setAnalysisResult(null);
    setCurrentStep('upload');
    setProgress(0);
    setPreviewUrl('');
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="min-h-screen bg-medical-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-medical-900 mb-2">
            DICOM Görüntüleyici ve Analiz
          </h1>
          <p className="text-medical-600">
            DICOM dosyalarını yükleyin, analiz edin ve SUV ölçümleri yapın
          </p>
        </div>

        {/* File Upload */}
        <div className="bg-white rounded-lg shadow-sm border border-medical-200 p-6 mb-6">
          <h2 className="text-xl font-semibold text-medical-900 mb-4">DICOM Dosya Yükleme</h2>
          
          <div className="border-2 border-dashed border-medical-300 rounded-lg p-8 text-center">
            <input
              ref={fileInputRef}
              type="file"
              accept=".dcm"
              onChange={handleFileSelect}
              className="hidden"
            />
            
            {!selectedFile ? (
              <div>
                <div className="text-medical-400 mb-4">
                  <svg className="mx-auto h-12 w-12" stroke="currentColor" fill="none" viewBox="0 0 48 48">
                    <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" />
                  </svg>
                </div>
                <p className="text-medical-600 mb-2">DICOM dosyasını buraya sürükleyin veya tıklayın</p>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="bg-medical-600 text-white px-6 py-2 rounded-md hover:bg-medical-700 transition-colors"
                >
                  Dosya Seç
                </button>
              </div>
            ) : (
              <div>
                <div className="text-green-600 mb-4">
                  <svg className="mx-auto h-12 w-12" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <p className="text-medical-900 font-medium mb-2">{selectedFile.name}</p>
                <p className="text-medical-600 mb-4">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
                
                <div className="flex space-x-4 justify-center">
                  <button
                    onClick={processDICOM}
                    disabled={isProcessing}
                    className="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 disabled:opacity-50 transition-colors"
                  >
                    {isProcessing ? 'İşleniyor...' : 'Analiz Et'}
                  </button>
                  
                  <button
                    onClick={resetViewer}
                    className="bg-gray-600 text-white px-6 py-2 rounded-md hover:bg-gray-700 transition-colors"
                  >
                    Yeni Dosya
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Processing Progress */}
        {isProcessing && (
          <div className="bg-white rounded-lg shadow-sm border border-medical-200 p-6 mb-6">
            <h3 className="text-lg font-medium text-medical-900 mb-4">İşleniyor...</h3>
            
            <div className="space-y-4">
              <div className="flex justify-between text-sm text-medical-600">
                <span>Adım: {currentStep === 'processing' ? 'DICOM İşleme' : 'Analiz'}</span>
                <span>{progress}%</span>
              </div>
              
              <div className="w-full bg-medical-200 rounded-full h-2">
                <div 
                  className="bg-medical-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${progress}%` }}
                ></div>
              </div>
            </div>
          </div>
        )}

        {/* Analysis Results */}
        {analysisResult && (
          <div className="space-y-6">
            {/* Metadata */}
            <div className="bg-white rounded-lg shadow-sm border border-medical-200 p-6">
              <h3 className="text-lg font-medium text-medical-900 mb-4">DICOM Metadata</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <span className="text-sm font-medium text-medical-600">Hasta Adı:</span>
                  <p className="text-medical-900">{analysisResult.metadata.patientName}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-medical-600">Hasta ID:</span>
                  <p className="text-medical-900">{analysisResult.metadata.patientID}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-medical-600">Çalışma Tarihi:</span>
                  <p className="text-medical-900">{analysisResult.metadata.studyDate}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-medical-600">Modalite:</span>
                  <p className="text-medical-900">{analysisResult.metadata.modality}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-medical-600">Görüntü Boyutu:</span>
                  <p className="text-medical-900">{analysisResult.metadata.imageSize.join(' × ')}</p>
                </div>
                <div>
                  <span className="text-sm font-medium text-medical-600">Kalite Skoru:</span>
                  <p className="text-medical-900">{(analysisResult.qualityScore * 100).toFixed(1)}%</p>
                </div>
              </div>
            </div>

            {/* SUV Calculations */}
            <div className="bg-white rounded-lg shadow-sm border border-medical-200 p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium text-medical-900">SUV Ölçümleri</h3>
                <button
                  onClick={() => calculateSUV(`Bölge ${analysisResult.suvCalculations.length + 1}`)}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 transition-colors"
                >
                  Yeni Ölçüm
                </button>
              </div>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                {analysisResult.suvCalculations.map((suv, index) => (
                  <div key={index} className="p-4 bg-medical-50 rounded-lg">
                    <h4 className="font-medium text-medical-800 mb-2">{suv.region}</h4>
                    <div className="grid grid-cols-2 gap-2 text-sm">
                      <div>
                        <span className="text-medical-600">SUV Max:</span>
                        <span className="ml-2 font-medium text-medical-900">{suv.suvMax.toFixed(2)}</span>
                      </div>
                      <div>
                        <span className="text-medical-600">SUV Mean:</span>
                        <span className="ml-2 font-medium text-medical-900">{suv.suvMean.toFixed(2)}</span>
                      </div>
                      <div>
                        <span className="text-medical-600">SUV Peak:</span>
                        <span className="ml-2 font-medium text-medical-900">{suv.suvPeak.toFixed(2)}</span>
                      </div>
                      <div>
                        <span className="text-medical-600">Hacim:</span>
                        <span className="ml-2 font-medium text-medical-900">{suv.volume.toFixed(1)} cm³</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Lesions */}
            <div className="bg-white rounded-lg shadow-sm border border-medical-200 p-6">
              <h3 className="text-lg font-medium text-medical-900 mb-4">Tespit Edilen Lezyonlar</h3>
              
              <div className="space-y-3">
                {analysisResult.lesions.map((lesion, index) => (
                  <div key={index} className="flex justify-between items-center p-3 bg-medical-50 rounded-lg">
                    <div>
                      <span className="font-medium text-medical-800">{lesion.location}</span>
                      <span className="text-sm text-medical-600 ml-2">({lesion.size} cm)</span>
                    </div>
                    <div className="flex items-center space-x-4">
                      <span className="text-medical-900 font-medium">SUV Max: {lesion.suvMax.toFixed(2)}</span>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        lesion.confidence > 0.9 ? 'bg-green-100 text-green-800' :
                        lesion.confidence > 0.7 ? 'bg-yellow-100 text-yellow-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        Güven: {(lesion.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Actions */}
            <div className="bg-white rounded-lg shadow-sm border border-medical-200 p-6">
              <h3 className="text-lg font-medium text-medical-900 mb-4">Analiz Araçları</h3>
              
              <div className="flex flex-wrap gap-4">
                <button
                  onClick={applyPERCIST}
                  disabled={analysisResult.suvCalculations.length < 2}
                  className="bg-purple-600 text-white px-6 py-2 rounded-md hover:bg-purple-700 disabled:opacity-50 transition-colors"
                >
                  PERCIST Analizi
                </button>
                
                <button
                  onClick={generate3DVisualization}
                  className="bg-indigo-600 text-white px-6 py-2 rounded-md hover:bg-indigo-700 transition-colors"
                >
                  3D Görselleştirme
                </button>
                
                <button
                  onClick={() => {
                    const report = JSON.stringify(analysisResult, null, 2);
                    const blob = new Blob([report], { type: 'application/json' });
                    const url = URL.createObjectURL(blob);
                    const link = document.createElement('a');
                    link.href = url;
                    link.download = 'dicom_analysis.json';
                    link.click();
                    URL.revokeObjectURL(url);
                  }}
                  className="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 transition-colors"
                >
                  JSON Rapor İndir
                </button>
              </div>
            </div>

            {/* Recommendations */}
            <div className="bg-white rounded-lg shadow-sm border border-medical-200 p-6">
              <h3 className="text-lg font-medium text-medical-900 mb-4">Öneriler</h3>
              
              <div className="space-y-2">
                {analysisResult.recommendations.map((rec, index) => (
                  <div key={index} className="flex items-start space-x-2">
                    <span className="text-medical-500 mt-1">•</span>
                    <span className="text-medical-700">{rec}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

