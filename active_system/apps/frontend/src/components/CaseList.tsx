import React, { useState, useEffect } from 'react';
import { Case, apiService } from '../services/api';
import { CaseActions } from './CaseActions';

export const CaseList: React.FC = () => {
  const [cases, setCases] = useState<Case[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'system' | 'clinical'>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadCases();
  }, []);

  const loadCases = async () => {
    try {
      setLoading(true);
      const data = await apiService.getCases();
      setCases(data);
    } catch (error) {
      console.error('Error loading cases:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCaseUpdate = (updatedCase: Case) => {
    setCases(prev => prev.map(c => c.id === updatedCase.id ? updatedCase : c));
  };

  const filteredCases = cases.filter(caseData => {
    // Search filter
    if (searchTerm && !caseData.title.toLowerCase().includes(searchTerm.toLowerCase()) &&
        !caseData.patient_id?.toLowerCase().includes(searchTerm.toLowerCase())) {
      return false;
    }

    // Status filter
    if (statusFilter !== 'all') {
      if (filter === 'system' && caseData.system_status !== statusFilter) return false;
      if (filter === 'clinical' && caseData.clinical_status !== statusFilter) return false;
    }

    return true;
  });

  const getStatusCounts = () => {
    const counts = {
      system: {} as Record<string, number>,
      clinical: {} as Record<string, number>
    };

    cases.forEach(caseData => {
      counts.system[caseData.system_status] = (counts.system[caseData.system_status] || 0) + 1;
      counts.clinical[caseData.clinical_status] = (counts.clinical[caseData.clinical_status] || 0) + 1;
    });

    return counts;
  };

  const statusCounts = getStatusCounts();

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-lg text-gray-600">Loading cases...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="bg-white rounded-lg border border-gray-200 p-4">
        <div className="flex flex-wrap gap-4 items-center">
          {/* Filter Type */}
          <div className="flex space-x-2">
            <button
              onClick={() => setFilter('all')}
              className={`px-3 py-1 rounded text-sm ${
                filter === 'all' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'
              }`}
            >
              All
            </button>
            <button
              onClick={() => setFilter('system')}
              className={`px-3 py-1 rounded text-sm ${
                filter === 'system' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'
              }`}
            >
              System Status
            </button>
            <button
              onClick={() => setFilter('clinical')}
              className={`px-3 py-1 rounded text-sm ${
                filter === 'clinical' ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'
              }`}
            >
              Clinical Status
            </button>
          </div>

          {/* Status Filter */}
          {filter !== 'all' && (
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-3 py-1 border border-gray-300 rounded text-sm"
            >
              <option value="all">All Statuses</option>
              {Object.keys(statusCounts[filter]).map(status => (
                <option key={status} value={status}>
                  {status} ({statusCounts[filter][status]})
                </option>
              ))}
            </select>
          )}

          {/* Search */}
          <input
            type="text"
            placeholder="Search cases..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="px-3 py-1 border border-gray-300 rounded text-sm flex-1 min-w-64"
          />

          {/* Refresh */}
          <button
            onClick={loadCases}
            className="px-3 py-1 bg-green-600 text-white rounded text-sm hover:bg-green-700"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Status Counts */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">System Status</h3>
          <div className="space-y-2">
            {Object.entries(statusCounts.system).map(([status, count]) => (
              <div key={status} className="flex justify-between items-center">
                <span className="text-sm text-gray-600">{status}</span>
                <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
                  {count}
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-lg border border-gray-200 p-4">
          <h3 className="text-lg font-semibold text-gray-900 mb-3">Clinical Status</h3>
          <div className="space-y-2">
            {Object.entries(statusCounts.clinical).map(([status, count]) => (
              <div key={status} className="flex justify-between items-center">
                <span className="text-sm text-gray-600">{status}</span>
                <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full text-xs">
                  {count}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Cases Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredCases.map(caseData => (
          <div key={caseData.id} className="bg-white rounded-lg border border-gray-200 p-4">
            <div className="flex items-start justify-between mb-3">
              <h3 className="text-lg font-semibold text-gray-900">{caseData.title}</h3>
              <div className="flex space-x-1">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  caseData.system_status === 'DRAFT' ? 'bg-gray-100 text-gray-800' :
                  caseData.system_status === 'AI_RUNNING' ? 'bg-blue-100 text-blue-800' :
                  caseData.system_status === 'AI_DONE' ? 'bg-green-100 text-green-800' :
                  'bg-red-100 text-red-800'
                }`}>
                  {caseData.system_status}
                </span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  caseData.clinical_status === 'NEW' ? 'bg-yellow-100 text-yellow-800' :
                  caseData.clinical_status === 'NEEDS_REVIEW' ? 'bg-orange-100 text-orange-800' :
                  caseData.clinical_status === 'IN_REVIEW' ? 'bg-blue-100 text-blue-800' :
                  caseData.clinical_status === 'AWAITING_SIGNATURE' ? 'bg-purple-100 text-purple-800' :
                  caseData.clinical_status === 'FINALIZED' ? 'bg-green-100 text-green-800' :
                  'bg-gray-100 text-gray-800'
                }`}>
                  {caseData.clinical_status}
                </span>
              </div>
            </div>

            <div className="text-sm text-gray-600 mb-4">
              <p><strong>ID:</strong> {caseData.id}</p>
              <p><strong>Patient ID:</strong> {caseData.patient_id || 'N/A'}</p>
              <p><strong>ICD Code:</strong> {caseData.icd_code || 'N/A'}</p>
              <p><strong>Created:</strong> {new Date(caseData.created_at).toLocaleDateString()}</p>
            </div>

            <CaseActions case={caseData} onUpdate={handleCaseUpdate} />
          </div>
        ))}
      </div>

      {filteredCases.length === 0 && (
        <div className="text-center py-12">
          <div className="text-lg text-gray-600 mb-2">No cases found</div>
          <div className="text-sm text-gray-500">
            {searchTerm ? 'Try adjusting your search terms' : 'Create your first case to get started'}
          </div>
        </div>
      )}
    </div>
  );
};