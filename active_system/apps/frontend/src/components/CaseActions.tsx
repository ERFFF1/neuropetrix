import React, { useState } from 'react';
import { Case } from '../services/api';
import { apiService } from '../services/api';

interface CaseActionsProps {
  case: Case;
  onUpdate: (updatedCase: Case) => void;
}

export const CaseActions: React.FC<CaseActionsProps> = ({ case: caseData, onUpdate }) => {
  const [loading, setLoading] = useState<string | null>(null);

  const handleAction = async (action: string) => {
    setLoading(action);
    try {
      switch (action) {
        case 'review':
          await apiService.updateCase(caseData.id, { 
            clinical_status: 'IN_REVIEW' 
          });
          break;
        case 'approve':
          await apiService.updateCase(caseData.id, { 
            clinical_status: 'AWAITING_SIGNATURE' 
          });
          break;
        case 'finalize':
          await apiService.updateCase(caseData.id, { 
            clinical_status: 'FINALIZED' 
          });
          break;
        case 'consultation':
          await apiService.updateCase(caseData.id, { 
            clinical_status: 'NEEDS_REVIEW' 
          });
          break;
        case 'pdf':
          const pdfResult = await apiService.generatePDF(caseData.id);
          window.open(pdfResult.pdf_url, '_blank');
          break;
        case 'share':
          const shareResult = await apiService.createShare(
            caseData.id, 
            new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(), // 7 days
            3
          );
          navigator.clipboard.writeText(shareResult.share_url);
          alert('Share link copied to clipboard!');
          break;
        case 'analysis':
          await apiService.enqueueAnalysis(caseData.id);
          await apiService.updateCase(caseData.id, { 
            system_status: 'AI_RUNNING' 
          });
          break;
      }
      
      // Refresh case data
      const updatedCase = await apiService.getCases();
      const currentCase = updatedCase.find(c => c.id === caseData.id);
      if (currentCase) {
        onUpdate(currentCase);
      }
    } catch (error) {
      console.error(`Error performing ${action}:`, error);
      alert(`Error performing ${action}. Please try again.`);
    } finally {
      setLoading(null);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'DRAFT': return 'bg-gray-100 text-gray-800';
      case 'AI_RUNNING': return 'bg-blue-100 text-blue-800';
      case 'AI_DONE': return 'bg-green-100 text-green-800';
      case 'AI_ERROR': return 'bg-red-100 text-red-800';
      case 'NEW': return 'bg-yellow-100 text-yellow-800';
      case 'NEEDS_REVIEW': return 'bg-orange-100 text-orange-800';
      case 'IN_REVIEW': return 'bg-blue-100 text-blue-800';
      case 'AWAITING_SIGNATURE': return 'bg-purple-100 text-purple-800';
      case 'FINALIZED': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-4">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Case Actions</h3>
        <div className="flex space-x-2">
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(caseData.system_status)}`}>
            {caseData.system_status}
          </span>
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(caseData.clinical_status)}`}>
            {caseData.clinical_status}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-2">
        {/* Analysis Actions */}
        <button
          onClick={() => handleAction('analysis')}
          disabled={loading === 'analysis' || caseData.system_status === 'AI_RUNNING'}
          className="px-3 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading === 'analysis' ? 'Running...' : 'Start Analysis'}
        </button>

        {/* Review Actions */}
        <button
          onClick={() => handleAction('review')}
          disabled={loading === 'review' || caseData.clinical_status === 'IN_REVIEW'}
          className="px-3 py-2 text-sm bg-yellow-600 text-white rounded hover:bg-yellow-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading === 'review' ? 'Processing...' : 'Review'}
        </button>

        {/* Approval Actions */}
        <button
          onClick={() => handleAction('approve')}
          disabled={loading === 'approve' || caseData.clinical_status === 'AWAITING_SIGNATURE'}
          className="px-3 py-2 text-sm bg-green-600 text-white rounded hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading === 'approve' ? 'Processing...' : 'Approve'}
        </button>

        {/* Finalization Actions */}
        <button
          onClick={() => handleAction('finalize')}
          disabled={loading === 'finalize' || caseData.clinical_status === 'FINALIZED'}
          className="px-3 py-2 text-sm bg-purple-600 text-white rounded hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading === 'finalize' ? 'Processing...' : 'Finalize'}
        </button>

        {/* Consultation Actions */}
        <button
          onClick={() => handleAction('consultation')}
          disabled={loading === 'consultation' || caseData.clinical_status === 'NEEDS_REVIEW'}
          className="px-3 py-2 text-sm bg-orange-600 text-white rounded hover:bg-orange-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading === 'consultation' ? 'Processing...' : 'Consultation'}
        </button>

        {/* PDF Actions */}
        <button
          onClick={() => handleAction('pdf')}
          disabled={loading === 'pdf'}
          className="px-3 py-2 text-sm bg-red-600 text-white rounded hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading === 'pdf' ? 'Generating...' : 'Generate PDF'}
        </button>

        {/* Share Actions */}
        <button
          onClick={() => handleAction('share')}
          disabled={loading === 'share'}
          className="px-3 py-2 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading === 'share' ? 'Creating...' : 'Share Link'}
        </button>
      </div>

      {/* Case Info */}
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="text-sm text-gray-600">
          <p><strong>ID:</strong> {caseData.id}</p>
          <p><strong>Patient ID:</strong> {caseData.patient_id || 'N/A'}</p>
          <p><strong>ICD Code:</strong> {caseData.icd_code || 'N/A'}</p>
          <p><strong>Created:</strong> {new Date(caseData.created_at).toLocaleDateString()}</p>
        </div>
      </div>
    </div>
  );
};
