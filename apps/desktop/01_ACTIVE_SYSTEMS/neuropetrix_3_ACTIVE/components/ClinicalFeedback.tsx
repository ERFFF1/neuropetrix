import React, { useState, useEffect } from 'react';
import { ClinicalFeedback, LearningLoop } from '../types';

interface ClinicalFeedbackProps {
  caseId: string;
  physicianId: string;
  currentRecommendation: any;
  onFeedbackSubmitted: (feedback: ClinicalFeedback) => void;
}

export default function ClinicalFeedback({ 
  caseId, 
  physicianId, 
  currentRecommendation, 
  onFeedbackSubmitted 
}: ClinicalFeedbackProps) {
  const [feedback, setFeedback] = useState<ClinicalFeedback>({
    caseId,
    physicianId,
    feedbackType: 'neutral',
    feedbackDetails: '',
    timestamp: new Date().toISOString(),
    confidenceLevel: 5
  });
  const [learningLoops, setLearningLoops] = useState<LearningLoop[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Mevcut öğrenme döngülerini yükle
  useEffect(() => {
    loadLearningLoops();
  }, [caseId]);

  const loadLearningLoops = async () => {
    try {
      const response = await fetch(`/api/feedback/learning-loops/${caseId}`);
      const data = await response.json();
      setLearningLoops(data.learningLoops || []);
    } catch (error) {
      console.error('Öğrenme döngüleri yüklenemedi:', error);
    }
  };

  const submitFeedback = async () => {
    setIsSubmitting(true);
    try {
      const response = await fetch('/api/feedback/submit', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(feedback)
      });

      const result = await response.json();
      
      if (result.success) {
        onFeedbackSubmitted(feedback);
        // Formu sıfırla
        setFeedback({
          caseId,
          physicianId,
          feedbackType: 'neutral',
          feedbackDetails: '',
          timestamp: new Date().toISOString(),
          confidenceLevel: 5
        });
        
        // Öğrenme döngülerini yenile
        await loadLearningLoops();
      }
    } catch (error) {
      console.error('Geri bildirim gönderilemedi:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  const approveModelUpdate = async (learningLoopId: string) => {
    try {
      const response = await fetch(`/api/feedback/approve-update/${learningLoopId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          approvedBy: physicianId,
          approvalDate: new Date().toISOString()
        })
      });

      if (response.ok) {
        await loadLearningLoops();
      }
    } catch (error) {
      console.error('Model güncellemesi onaylanamadı:', error);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Başlık */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-800">
            💬 Klinik Geri Bildirim
          </h1>
          <p className="text-slate-600 mt-2">
            Hekim geri bildirimi ve öğrenme döngüleri
          </p>
        </div>

        {/* Ana İçerik */}
        <div className="bg-white rounded-lg shadow-md border border-slate-200 p-6">
          <h2 className="text-2xl font-bold text-slate-800 mb-6">Klinik Karar Döngüsü</h2>
          
          {/* Mevcut Öneri */}
          <div className="bg-blue-50 p-4 rounded-lg mb-6 border border-blue-200">
            <h3 className="text-lg font-semibold mb-3 text-slate-800">Mevcut AI Önerisi</h3>
            <div className="space-y-2">
              <div className="text-slate-700"><strong>Tanı:</strong> {currentRecommendation?.diagnosis || 'N/A'}</div>
              <div className="text-slate-700"><strong>Tedavi:</strong> {currentRecommendation?.treatment || 'N/A'}</div>
              <div className="text-slate-700"><strong>Güven Skoru:</strong> {currentRecommendation?.confidence || 'N/A'}</div>
            </div>
          </div>

        {/* Geri Bildirim Formu */}
        <div className="space-y-6">
          <h3 className="text-xl font-semibold text-slate-800">Hekim Geri Bildirimi</h3>
          
          {/* Feedback Type */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Geri Bildirim Türü
            </label>
            <div className="grid grid-cols-3 gap-4">
              {[
                { value: 'supportive_positive', label: 'Destekleyici', icon: '✅' },
                { value: 'neutral', label: 'Nötr', icon: '➖' },
                { value: 'hard_negative', label: 'Reddedici', icon: '❌' }
              ].map((type) => (
                <button
                  key={type.value}
                  onClick={() => setFeedback({...feedback, feedbackType: type.value as any})}
                  className={`p-4 rounded-lg border-2 text-center transition-colors duration-200 ${
                    feedback.feedbackType === type.value
                      ? 'border-blue-500 bg-blue-50'
                      : 'border-slate-200 hover:border-slate-300'
                  }`}
                >
                  <div className="text-2xl mb-2">{type.icon}</div>
                  <div className="text-sm font-medium text-slate-700">{type.label}</div>
                </button>
              ))}
            </div>
          </div>

          {/* Confidence Level */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Güven Seviyesi: {feedback.confidenceLevel}/10
            </label>
            <input
              type="range"
              min="1"
              max="10"
              value={feedback.confidenceLevel}
              onChange={(e) => setFeedback({...feedback, confidenceLevel: parseInt(e.target.value)})}
              className="w-full h-2 bg-slate-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-slate-500 mt-1">
              <span>Düşük</span>
              <span>Yüksek</span>
            </div>
          </div>

          {/* Feedback Details */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Detaylı Açıklama
            </label>
            <textarea
              value={feedback.feedbackDetails}
              onChange={(e) => setFeedback({...feedback, feedbackDetails: e.target.value})}
              className="w-full p-3 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Öneri hakkında detaylı geri bildiriminizi yazın..."
              rows={4}
            />
          </div>

          {/* Alternative Recommendation */}
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-2">
              Alternatif Öneri (Opsiyonel)
            </label>
            <textarea
              value={feedback.alternativeRecommendation || ''}
              onChange={(e) => setFeedback({...feedback, alternativeRecommendation: e.target.value})}
              className="w-full p-3 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              placeholder="Eğer farklı bir öneriniz varsa yazın..."
              rows={3}
            />
          </div>

          {/* Submit Button */}
          <button
            onClick={submitFeedback}
            disabled={isSubmitting || !feedback.feedbackDetails.trim()}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors duration-200 font-medium"
          >
            {isSubmitting ? 'Gönderiliyor...' : 'Geri Bildirimi Gönder'}
          </button>
        </div>
        </div>

      {/* Learning Loops */}
      {learningLoops.length > 0 && (
        <div className="bg-white rounded-lg shadow-md border border-slate-200 p-6">
          <h3 className="text-xl font-semibold mb-4 text-slate-800">Öğrenme Döngüleri</h3>
          <div className="space-y-4">
            {learningLoops.map((loop, index) => (
              <div key={index} className="border border-slate-200 rounded-lg p-4">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h4 className="font-medium text-slate-800">Model Güncellemesi v{loop.modelUpdate.version}</h4>
                    <p className="text-sm text-slate-600">
                      {new Date(loop.feedback.timestamp).toLocaleDateString('tr-TR')}
                    </p>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                    loop.validationStatus === 'approved' ? 'bg-green-100 text-green-800' :
                    loop.validationStatus === 'rejected' ? 'bg-red-100 text-red-800' :
                    'bg-yellow-100 text-yellow-800'
                  }`}>
                    {loop.validationStatus === 'approved' ? 'Onaylandı' :
                     loop.validationStatus === 'rejected' ? 'Reddedildi' : 'Beklemede'}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-3">
                  <div>
                    <span className="text-sm font-medium">Doğruluk:</span>
                    <div className="text-lg font-bold text-blue-600">
                      {(loop.modelUpdate.performanceMetrics.accuracy * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div>
                    <span className="text-sm font-medium">Hassasiyet:</span>
                    <div className="text-lg font-bold text-green-600">
                      {(loop.modelUpdate.performanceMetrics.sensitivity * 100).toFixed(1)}%
                    </div>
                  </div>
                  <div>
                    <span className="text-sm font-medium">Özgüllük:</span>
                    <div className="text-lg font-bold text-purple-600">
                      {(loop.modelUpdate.performanceMetrics.specificity * 100).toFixed(1)}%
                    </div>
                  </div>
                </div>

                <div className="mb-3">
                  <span className="text-sm font-medium">Değişiklikler:</span>
                  <ul className="mt-1 space-y-1">
                    {loop.modelUpdate.changes.map((change, idx) => (
                      <li key={idx} className="text-sm text-gray-600">• {change}</li>
                    ))}
                  </ul>
                </div>

                {loop.validationStatus === 'pending' && (
                  <div className="flex space-x-2">
                    <button
                      onClick={() => approveModelUpdate(loop.feedback.caseId)}
                      className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 text-sm"
                    >
                      Onayla
                    </button>
                    <button
                      onClick={() => {/* Reject logic */}}
                      className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 text-sm"
                    >
                      Reddet
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Compliance Information */}
      <div className="bg-slate-50 rounded-lg p-4 border border-slate-200">
        <h4 className="font-medium mb-2 text-slate-800">Yasal Uyum Bilgileri</h4>
        <div className="text-sm text-slate-600 space-y-1">
          <div>• Tüm geri bildirimler anonimleştirilir ve güvenli şekilde saklanır</div>
          <div>• Model güncellemeleri sadece yetkili klinisyenler tarafından onaylanır</div>
          <div>• KVKK, HIPAA ve GDPR standartlarına uygunluk sağlanır</div>
        </div>
      </div>
      </div>
    </div>
  );
}
