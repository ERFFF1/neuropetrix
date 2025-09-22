import React, { useState, useEffect } from 'react';
import { Case, ChatMessage } from '../types';
import { apiService } from '../services/api';
import { geminiService } from '../services/geminiService';
import AnalysisResult from './AnalysisResult';
import ChatInterface from './ChatInterface';
import DicomViewer from './DicomViewer';
import { Brain, MessageCircle, FileImage, FileText, Settings } from 'lucide-react';

interface CaseDetailProps {
  case: Case;
  onUpdateCase: (caseId: string, updates: Partial<Case>) => void;
}

const CaseDetail: React.FC<CaseDetailProps> = ({ case: caseItem, onUpdateCase }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'analysis' | 'chat' | 'images' | 'report'>('overview');
  const [chatHistory, setChatHistory] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (caseItem.chatHistory) {
      setChatHistory(caseItem.chatHistory);
    }
  }, [caseItem.chatHistory]);

  const handleStartAnalysis = async () => {
    try {
      setLoading(true);
      onUpdateCase(caseItem.id, { systemStatus: 'ai_running' });
      
      // Start AI analysis
      const analysisResult = await geminiService.analyzePatientData(caseItem.patientData);
      
      onUpdateCase(caseItem.id, {
        analysis: analysisResult,
        systemStatus: 'ai_done'
      });
    } catch (error) {
      console.error('Analysis failed:', error);
      onUpdateCase(caseItem.id, {
        systemStatus: 'ai_error',
        error: 'AI analizi sırasında hata oluştu'
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSendMessage = async (message: string) => {
    try {
      const newMessage: ChatMessage = {
        id: Date.now().toString(),
        role: 'user',
        content: message,
        timestamp: new Date()
      };

      setChatHistory(prev => [...prev, newMessage]);

      // Get AI response
      const aiResponse = await geminiService.continueChat(
        caseItem.id,
        message,
        caseItem.patientData,
        chatHistory
      );

      const aiMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: aiResponse,
        timestamp: new Date()
      };

      setChatHistory(prev => [...prev, aiMessage]);

      // Update case with new chat history
      onUpdateCase(caseItem.id, {
        chatHistory: [...chatHistory, newMessage, aiMessage]
      });
    } catch (error) {
      console.error('Chat failed:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'draft': return 'bg-gray-100 text-gray-800';
      case 'ai_running': return 'bg-blue-100 text-blue-800';
      case 'ai_done': return 'bg-green-100 text-green-800';
      case 'ai_error': return 'bg-red-100 text-red-800';
      case 'needs_review': return 'bg-yellow-100 text-yellow-800';
      case 'in_review': return 'bg-purple-100 text-purple-800';
      case 'awaiting_signature': return 'bg-orange-100 text-orange-800';
      case 'finalized': return 'bg-green-100 text-green-800';
      case 'reopened': return 'bg-indigo-100 text-indigo-800';
      case 'archived': return 'bg-gray-100 text-gray-600';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const formatDate = (date: Date) => {
    return new Intl.DateTimeFormat('tr-TR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    }).format(date);
  };

  const tabs = [
    { id: 'overview', label: 'Genel Bakış', icon: Settings },
    { id: 'analysis', label: 'AI Analizi', icon: Brain },
    { id: 'chat', label: 'Sohbet', icon: MessageCircle },
    { id: 'images', label: 'Görüntüler', icon: FileImage },
    { id: 'report', label: 'Rapor', icon: FileText }
  ];

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-6 border-b border-gray-200 bg-white">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">
              {caseItem.patientData.chiefComplaint}
            </h2>
            <p className="text-sm text-gray-500">
              Vaka ID: {caseItem.id} • {caseItem.patientData.age} yaş, {caseItem.patientData.gender === 'male' ? 'Erkek' : 'Kadın'}
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(caseItem.systemStatus)}`}>
              {caseItem.systemStatus}
            </span>
            <span className={`px-3 py-1 rounded-full text-sm font-medium ${
              caseItem.priority === 'urgent' ? 'bg-red-100 text-red-800' :
              caseItem.priority === 'high' ? 'bg-orange-100 text-orange-800' :
              caseItem.priority === 'normal' ? 'bg-blue-100 text-blue-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {caseItem.priority.toUpperCase()}
            </span>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex space-x-1">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors ${
                  activeTab === tab.id
                    ? 'bg-blue-100 text-blue-700'
                    : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Icon className="w-4 h-4 mr-2" />
                {tab.label}
              </button>
            );
          })}
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto p-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Patient Info */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Hasta Bilgileri</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Yaş</label>
                  <p className="text-gray-900">{caseItem.patientData.age}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Cinsiyet</label>
                  <p className="text-gray-900 capitalize">{caseItem.patientData.gender}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Başvuru Şikayeti</label>
                  <p className="text-gray-900">{caseItem.patientData.chiefComplaint}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Tıbbi Geçmiş</label>
                  <p className="text-gray-900">{caseItem.patientData.medicalHistory || 'Belirtilmemiş'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Mevcut İlaçlar</label>
                  <p className="text-gray-900">{caseItem.patientData.currentMedications || 'Belirtilmemiş'}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Ek Notlar</label>
                  <p className="text-gray-900">{caseItem.patientData.additionalNotes || 'Belirtilmemiş'}</p>
                </div>
              </div>
            </div>

            {/* Vitals */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Vital Bulgular</h3>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-blue-600">{caseItem.patientData.vitals.bloodPressure}</div>
                  <div className="text-sm text-gray-500">Kan Basıncı</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{caseItem.patientData.vitals.heartRate}</div>
                  <div className="text-sm text-gray-500">Kalp Hızı (bpm)</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-orange-600">{caseItem.patientData.vitals.temperature}°C</div>
                  <div className="text-sm text-gray-500">Sıcaklık</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">{caseItem.patientData.vitals.respiratoryRate}</div>
                  <div className="text-sm text-gray-500">Solunum (/dk)</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-indigo-600">{caseItem.patientData.vitals.oxygenSaturation}%</div>
                  <div className="text-sm text-gray-500">O2 Sat</div>
                </div>
              </div>
            </div>

            {/* Case Info */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Vaka Bilgileri</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="text-sm font-medium text-gray-500">Oluşturulma Tarihi</label>
                  <p className="text-gray-900">{formatDate(caseItem.createdAt)}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Son Güncelleme</label>
                  <p className="text-gray-900">{formatDate(caseItem.updatedAt)}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Sistem Durumu</label>
                  <p className="text-gray-900">{caseItem.systemStatus}</p>
                </div>
                <div>
                  <label className="text-sm font-medium text-gray-500">Klinik Durumu</label>
                  <p className="text-gray-900">{caseItem.clinicalStatus}</p>
                </div>
              </div>
            </div>

            {/* Actions */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Eylemler</h3>
              <div className="flex space-x-3">
                {caseItem.systemStatus === 'draft' && (
                  <button
                    onClick={handleStartAnalysis}
                    disabled={loading}
                    className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {loading ? 'AI Analizi Başlatılıyor...' : 'AI Analizi Başlat'}
                  </button>
                )}
                
                {caseItem.systemStatus === 'ai_done' && (
                  <button
                    onClick={() => setActiveTab('analysis')}
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                  >
                    Analizi Görüntüle
                  </button>
                )}

                <button
                  onClick={() => setActiveTab('chat')}
                  className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
                >
                  Sohbet Et
                </button>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'analysis' && caseItem.analysis && (
          <AnalysisResult analysis={caseItem.analysis} />
        )}

        {activeTab === 'chat' && (
          <ChatInterface
            chatHistory={chatHistory}
            onSendMessage={handleSendMessage}
            disabled={caseItem.systemStatus === 'ai_running'}
          />
        )}

        {activeTab === 'images' && (
          <DicomViewer caseId={caseItem.id} />
        )}

        {activeTab === 'report' && (
          <div className="bg-white rounded-lg border border-gray-200 p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Rapor</h3>
            <p className="text-gray-500">Rapor özelliği yakında eklenecek...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default CaseDetail;
