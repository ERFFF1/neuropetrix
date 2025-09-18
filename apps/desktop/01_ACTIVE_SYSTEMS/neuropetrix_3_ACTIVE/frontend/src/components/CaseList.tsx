import React, { useState } from 'react';
import { Case, PatientData } from '../types';
import { Plus, Search, Filter, Calendar } from 'lucide-react';
import PatientDataForm from './PatientDataForm';

interface CaseListProps {
  cases: Case[];
  selectedCase: Case | null;
  onSelectCase: (caseItem: Case) => void;
  onCreateCase: (patientData: PatientData) => void;
  onUpdateCase: (caseId: string, updates: Partial<Case>) => void;
}

const CaseList: React.FC<CaseListProps> = ({
  cases,
  selectedCase,
  onSelectCase,
  onCreateCase,
  onUpdateCase
}) => {
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  const filteredCases = cases.filter(caseItem => {
    const matchesSearch = caseItem.patientData.chiefComplaint
      .toLowerCase()
      .includes(searchTerm.toLowerCase()) ||
      caseItem.id.toLowerCase().includes(searchTerm.toLowerCase());
    
    const matchesStatus = statusFilter === 'all' || 
      caseItem.systemStatus === statusFilter ||
      caseItem.clinicalStatus === statusFilter;
    
    return matchesSearch && matchesStatus;
  });

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

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'urgent': return 'text-red-600';
      case 'high': return 'text-orange-600';
      case 'normal': return 'text-blue-600';
      case 'low': return 'text-gray-600';
      default: return 'text-gray-600';
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

  return (
    <div className="h-full flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-gray-900">Vakalar</h2>
          <button
            onClick={() => setShowCreateForm(true)}
            className="flex items-center px-3 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-4 h-4 mr-2" />
            Yeni Vaka
          </button>
        </div>

        {/* Search */}
        <div className="relative mb-3">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Vaka ara..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        {/* Filter */}
        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-gray-400" />
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="all">Tüm Durumlar</option>
            <option value="draft">Taslak</option>
            <option value="ai_running">AI Çalışıyor</option>
            <option value="ai_done">AI Tamamlandı</option>
            <option value="needs_review">İnceleme Gerekli</option>
            <option value="in_review">İnceleniyor</option>
            <option value="finalized">Tamamlandı</option>
            <option value="ai_error">Hata</option>
          </select>
        </div>
      </div>

      {/* Cases List */}
      <div className="flex-1 overflow-y-auto">
        {filteredCases.length === 0 ? (
          <div className="p-4 text-center text-gray-500">
            <div className="text-4xl mb-2">📋</div>
            <p>Vaka bulunamadı</p>
          </div>
        ) : (
          <div className="p-2">
            {filteredCases.map((caseItem) => (
              <div
                key={caseItem.id}
                onClick={() => onSelectCase(caseItem)}
                className={`p-3 mb-2 rounded-lg border cursor-pointer transition-colors ${
                  selectedCase?.id === caseItem.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                }`}
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <h3 className="font-medium text-gray-900 text-sm">
                      {caseItem.patientData.chiefComplaint}
                    </h3>
                    <p className="text-xs text-gray-500 mt-1">
                      {caseItem.patientData.age} yaş, {caseItem.patientData.gender === 'male' ? 'Erkek' : 'Kadın'}
                    </p>
                  </div>
                  <div className="flex items-center space-x-1">
                    <span className={`text-xs px-2 py-1 rounded-full ${getStatusColor(caseItem.systemStatus)}`}>
                      {caseItem.systemStatus}
                    </span>
                  </div>
                </div>

                <div className="flex items-center justify-between text-xs text-gray-500">
                  <div className="flex items-center">
                    <Calendar className="w-3 h-3 mr-1" />
                    {formatDate(caseItem.createdAt)}
                  </div>
                  <span className={`font-medium ${getPriorityColor(caseItem.priority)}`}>
                    {caseItem.priority.toUpperCase()}
                  </span>
                </div>

                {caseItem.analysis && (
                  <div className="mt-2 p-2 bg-green-50 rounded text-xs">
                    <span className="text-green-800">✓ AI Analizi Tamamlandı</span>
                  </div>
                )}

                {caseItem.error && (
                  <div className="mt-2 p-2 bg-red-50 rounded text-xs">
                    <span className="text-red-800">⚠️ Hata: {caseItem.error}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Case Modal */}
      {showCreateForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold">Yeni Vaka Oluştur</h3>
              <button
                onClick={() => setShowCreateForm(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ×
              </button>
            </div>
            
            <PatientDataForm
              onSubmit={(patientData) => {
                onCreateCase(patientData);
                setShowCreateForm(false);
              }}
              onCancel={() => setShowCreateForm(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default CaseList;
