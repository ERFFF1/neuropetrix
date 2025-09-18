import React, { useState, useEffect } from 'react';
import { AnalysisResult as AnalysisResultType } from '../types';
import { geminiService } from '../services/geminiService';
import { Brain, CheckCircle, AlertCircle, Clock, TrendingUp } from 'lucide-react';

interface AnalysisResultProps {
  analysis: AnalysisResultType;
}

const AnalysisResult: React.FC<AnalysisResultProps> = ({ analysis }) => {
  const [followUpQuestions, setFollowUpQuestions] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadFollowUpQuestions();
  }, [analysis]);

  const loadFollowUpQuestions = async () => {
    try {
      setLoading(true);
      const questions = await geminiService.generateFollowUpQuestions(analysis);
      setFollowUpQuestions(questions);
    } catch (error) {
      console.error('Failed to load follow-up questions:', error);
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return 'text-green-600';
    if (confidence >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getConfidenceText = (confidence: number) => {
    if (confidence >= 0.8) return 'Yüksek';
    if (confidence >= 0.6) return 'Orta';
    return 'Düşük';
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            <Brain className="w-6 h-6 text-blue-600 mr-2" />
            <h3 className="text-lg font-semibold text-gray-900">AI Analiz Sonucu</h3>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <div className={`text-sm font-medium ${getConfidenceColor(analysis.confidence)}`}>
                Güven: {getConfidenceText(analysis.confidence)} ({Math.round(analysis.confidence * 100)}%)
              </div>
              <div className="text-xs text-gray-500">
                Model: {analysis.modelVersion}
              </div>
            </div>
            <div className="text-right">
              <div className="text-sm font-medium text-gray-900">
                {analysis.processingTime}s
              </div>
              <div className="text-xs text-gray-500">
                İşlem Süresi
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Summary */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
          <CheckCircle className="w-5 h-5 text-green-600 mr-2" />
          Analiz Özeti
        </h4>
        <div className="bg-gray-50 rounded-lg p-4">
          <p className="text-gray-700 leading-relaxed">{analysis.summary}</p>
        </div>
      </div>

      {/* Differential Diagnosis */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
          <AlertCircle className="w-5 h-5 text-orange-600 mr-2" />
          Ayırıcı Tanılar
        </h4>
        <div className="space-y-2">
          {analysis.differentialDiagnosis.map((diagnosis, index) => (
            <div key={index} className="flex items-start">
              <div className="flex-shrink-0 w-6 h-6 bg-orange-100 text-orange-600 rounded-full flex items-center justify-center text-sm font-medium mr-3 mt-0.5">
                {index + 1}
              </div>
              <div className="flex-1">
                <p className="text-gray-700">{diagnosis}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Suggestions */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
          <TrendingUp className="w-5 h-5 text-blue-600 mr-2" />
          Öneriler
        </h4>
        <div className="space-y-2">
          {analysis.suggestions.map((suggestion, index) => (
            <div key={index} className="flex items-start">
              <div className="flex-shrink-0 w-6 h-6 bg-blue-100 text-blue-600 rounded-full flex items-center justify-center text-sm font-medium mr-3 mt-0.5">
                {index + 1}
              </div>
              <div className="flex-1">
                <p className="text-gray-700">{suggestion}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Follow-up Questions */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-3 flex items-center">
          <Clock className="w-5 h-5 text-purple-600 mr-2" />
          Takip Soruları
        </h4>
        {loading ? (
          <div className="flex items-center justify-center py-4">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-purple-600"></div>
            <span className="ml-2 text-gray-600">Sorular yükleniyor...</span>
          </div>
        ) : (
          <div className="space-y-2">
            {followUpQuestions.map((question, index) => (
              <div key={index} className="flex items-start">
                <div className="flex-shrink-0 w-6 h-6 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-medium mr-3 mt-0.5">
                  ?
                </div>
                <div className="flex-1">
                  <p className="text-gray-700">{question}</p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Confidence Indicator */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-3">Güven Seviyesi</h4>
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Analiz Güveni</span>
            <span className={`text-sm font-medium ${getConfidenceColor(analysis.confidence)}`}>
              {Math.round(analysis.confidence * 100)}%
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full ${
                analysis.confidence >= 0.8 ? 'bg-green-500' :
                analysis.confidence >= 0.6 ? 'bg-yellow-500' : 'bg-red-500'
              }`}
              style={{ width: `${analysis.confidence * 100}%` }}
            ></div>
          </div>
          <div className="text-xs text-gray-500">
            {analysis.confidence >= 0.8 && 'Yüksek güvenilirlik - Sonuçlar güvenilir'}
            {analysis.confidence >= 0.6 && analysis.confidence < 0.8 && 'Orta güvenilirlik - Ek değerlendirme önerilir'}
            {analysis.confidence < 0.6 && 'Düşük güvenilirlik - Manuel değerlendirme gerekli'}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysisResult;
