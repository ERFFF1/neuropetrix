import React, { useState } from 'react';
import { PatientCase, AnalysisResult, AnalysisProgress, QualityControl, EvidenceLevel, ClinicalGoal } from '../types';
import { runAnalysis } from '../services/mockApiService';
import LoadingSpinner from './LoadingSpinner';

interface CaseDetailViewProps {
  patientCase: PatientCase;
  onBack: () => void;
  onAnalysisComplete: (caseId: string, result: AnalysisResult) => void;
  onManualCorrection: (caseId: string) => void;
}

const QualityControlBanner: React.FC<{ status: QualityControl }> = ({ status }) => {
    if (status === 'PASSED') return null;
    
    const config = {
        BORDERLINE: {
            bgColor: 'bg-yellow-50',
            borderColor: 'border-yellow-200',
            textColor: 'text-yellow-800',
            title: 'Quality Control: Borderline',
            message: 'Image quality is suboptimal. Quantitative analysis may be less reliable; please correlate clinically.'
        },
        FAILED: {
            bgColor: 'bg-red-50',
            borderColor: 'border-red-200',
            textColor: 'text-red-800',
            title: 'Quality Control: Failed',
            message: 'Image quality is poor. Quantitative analysis is unreliable. A repeat scan is recommended.'
        }
    };
    const { bgColor, borderColor, textColor, title, message } = config[status];

    return (
        <div className={`p-4 rounded-lg border ${bgColor} ${borderColor} my-4`}>
            <h3 className={`font-bold ${textColor}`}>{title}</h3>
            <p className={`text-sm ${textColor}`}>{message}</p>
        </div>
    );
};

const CaseDetailView: React.FC<CaseDetailViewProps> = ({ patientCase, onBack, onAnalysisComplete, onManualCorrection }) => {
    const [isAnalyzing, setIsAnalyzing] = useState(false);
    const [analysisProgress, setAnalysisProgress] = useState<AnalysisProgress | null>(null);
    const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(patientCase.analysisResult || null);
    const [selectedGoal, setSelectedGoal] = useState<ClinicalGoal>('TX_RESPONSE');
    
    const handleRunAnalysis = async () => {
        setIsAnalyzing(true);
        setAnalysisResult(null);
        const result = await runAnalysis(patientCase, selectedGoal, setAnalysisProgress);
        if (result) {
            setAnalysisResult(result);
            onAnalysisComplete(patientCase.id, result);
        }
        setIsAnalyzing(false);
    };

    const handleSuggestCorrection = () => {
        onManualCorrection(patientCase.id);
        alert("Your correction suggestion has been logged for future model improvement.");
    };
    
    const getEvidenceBadgeClass = (level: EvidenceLevel) => {
        const baseClass = "inline-flex items-center rounded-md px-2 py-0.5 text-xs font-medium ring-1 ring-inset";
        switch (level) {
            case '1A': case '1B': return `${baseClass} bg-green-50 text-green-700 ring-green-600/20`;
            case '2A': case '2B': return `${baseClass} bg-blue-50 text-blue-700 ring-blue-600/20`;
            case '3': return `${baseClass} bg-yellow-50 text-yellow-800 ring-yellow-600/20`;
            case 'Expert': return `${baseClass} bg-indigo-50 text-indigo-700 ring-indigo-600/20`;
            default: return `${baseClass} bg-slate-50 text-slate-600 ring-slate-500/20`;
        }
    };
    
    const getTrendClass = (trend?: AnalysisResult['trend']["label"]) => {
        switch (trend) {
            case 'Progresyon adayı': return 'text-red-600';
            case 'Anlamlı yanıt adayı': return 'text-green-600';
            case 'Stabil/Belirsiz': return 'text-slate-600';
            default: return 'text-slate-500';
        }
    };

    const renderAnalysisResult = (result: AnalysisResult) => (
        <div className="space-y-6">
            <div className="p-4 bg-white rounded-lg border border-slate-200">
                <h3 className="text-lg font-bold text-slate-800">Structured Report</h3>
                <div className="mt-4 space-y-3 text-sm">
                    <div>
                        <h4 className="font-semibold text-slate-600">Indication</h4>
                        <p className="text-slate-700">{result.structuredReport.indication}</p>
                    </div>
                    <div>
                        <h4 className="font-semibold text-slate-600">Findings</h4>
                        {result.trend && (
                        <div className="flex items-center space-x-4">
                             <p className={`font-bold ${getTrendClass(result.trend.label)}`}>{result.trend.label}</p>
                            {result.trend.deltaSUVpct !== undefined && <p className="text-slate-600">ΔSUVmax: {result.trend.deltaSUVpct.toFixed(1)}%</p>}
                        </div>
                        )}
                        <p className="text-slate-700 mt-1">{result.structuredReport.findings}</p>
                         {result.qcFlag === 'LOW_CONFIDENCE' && <p className="text-sm text-amber-700 mt-2 font-semibold">Note: Low confidence in quantitative findings due to image quality.</p>}
                    </div>
                    <div>
                        <h4 className="font-semibold text-slate-600">Conclusion</h4>
                        <p className="text-slate-800 font-medium">{result.structuredReport.conclusion}</p>
                    </div>
                </div>
            </div>
             {result.diagnosticSteps && result.diagnosticSteps.length > 0 && (
                <div className="space-y-4">
                    <h3 className="text-lg font-bold text-slate-800">Diagnostic Steps</h3>
                    {result.diagnosticSteps.map((step, index) => (
                         <div key={index} className="p-4 bg-white rounded-lg border border-slate-200 shadow-sm">
                             <h4 className="font-semibold text-blue-800">{step.name}</h4>
                             <p className="mt-2 text-sm text-slate-600">{step.rationale}</p>
                         </div>
                    ))}
                </div>
             )}
             <div className="space-y-4">
                 <h3 className="text-lg font-bold text-slate-800">Recommendation Cards</h3>
                {result.recommendationCards && result.recommendationCards.filter(card => card.evidenceLevel).map((card, index) => (
                     <div key={index} className="p-4 bg-white rounded-lg border border-slate-200 shadow-sm">
                         <div className="flex justify-between items-start">
                             <h4 className="font-semibold text-blue-800">{card.title}</h4>
                             <span className={getEvidenceBadgeClass(card.evidenceLevel)}>Evidence: {card.evidenceLevel}</span>
                         </div>
                         <p className="mt-2 text-sm text-slate-600">{card.rationale}</p>
                     </div>
                ))}
             </div>
             <div className="pt-4 border-t border-slate-200">
                <div className="flex space-x-4">
                    <button 
                        onClick={() => alert('Approved report logged to system library.')} 
                        className="flex-1 rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500">
                        Approve & Add to Library
                    </button>
                    <button 
                        onClick={handleSuggestCorrection}
                        className="flex-1 rounded-md bg-white px-3 py-2 text-sm font-semibold text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 hover:bg-slate-50">
                        Suggest Correction
                    </button>
                </div>
                {(result.rulesVersion || result.guidelineVersion) && (
                    <div className="mt-4 text-center text-xs text-slate-400">
                        Analysis based on: Rules v{result.rulesVersion || 'N/A'} / Guidelines: {result.guidelineVersion || 'N/A'}
                    </div>
                )}
             </div>
        </div>
    );

    return (
        <div className="p-4 sm:p-6 lg:p-8 bg-white max-w-7xl mx-auto my-8 rounded-lg shadow-lg border border-slate-200">
            <div className="flex justify-between items-start">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900">{patientCase.patientInfo.name}</h1>
                    <p className="text-md text-slate-500">{patientCase.id} - {patientCase.diagnosis}</p>
                </div>
                <button onClick={onBack} className="rounded-md bg-white px-3.5 py-2.5 text-sm font-semibold text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 hover:bg-slate-50">&larr; Back to Dashboard</button>
            </div>
            
            <QualityControlBanner status={patientCase.qualityControl} />

            <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-4 border-t border-b border-slate-200 py-4">
                <div><dt className="text-sm font-medium text-slate-500">Age</dt><dd className="mt-1 text-lg font-semibold text-slate-900">{patientCase.patientInfo.age}</dd></div>
                <div><dt className="text-sm font-medium text-slate-500">Gender</dt><dd className="mt-1 text-lg font-semibold text-slate-900">{patientCase.patientInfo.gender}</dd></div>
                <div><dt className="text-sm font-medium text-slate-500">Current SUVmax</dt><dd className="mt-1 text-lg font-semibold text-slate-900">{patientCase.currentSUVmax ?? 'N/A'}</dd></div>
                <div><dt className="text-sm font-medium text-slate-500">Template</dt><dd className="mt-1 text-lg font-semibold text-slate-900">{patientCase.clinicalTemplate || 'General'}</dd></div>
            </div>

            <div className="mt-8 grid grid-cols-1 lg:grid-cols-3 gap-8">
                <div className="lg:col-span-2 space-y-8">
                    <section>
                        <h2 className="text-xl font-semibold text-slate-800 mb-4">Clinical Notes</h2>
                        <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                            <p className="text-slate-700 leading-relaxed whitespace-pre-wrap">{patientCase.clinicalNotes || 'No clinical notes provided.'}</p>
                        </div>
                    </section>
                </div>

                <div className="lg:col-span-1">
                     <div className="sticky top-8 bg-blue-50 p-6 rounded-lg border border-blue-200 min-h-[400px] flex flex-col">
                        <h2 className="text-xl font-semibold text-slate-800 flex-shrink-0">AI Expert Assistant</h2>
                        <div className="flex-grow flex flex-col justify-center mt-4">
                           {isAnalyzing ? (
                                <LoadingSpinner text={analysisProgress?.message || "Analyzing..."} />
                           ) : analysisResult ? (
                                renderAnalysisResult(analysisResult)
                           ) : (
                                <div className="text-center">
                                    <div className="mb-4">
                                        <label htmlFor="clinicalGoal" className="block text-sm font-medium text-slate-700 mb-1">Select Clinical Goal</label>
                                        <select 
                                            id="clinicalGoal" 
                                            value={selectedGoal}
                                            onChange={(e) => setSelectedGoal(e.target.value as ClinicalGoal)}
                                            className="mt-1 block w-full rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-indigo-500 focus:outline-none focus:ring-indigo-500 sm:text-sm"
                                        >
                                            <option value="DIAGNOSIS">Diagnosis</option>
                                            <option value="TREATMENT">Treatment</option>
                                            <option value="TX_RESPONSE">Treatment Response</option>
                                            <option value="PROGNOSIS">Prognosis</option>
                                        </select>
                                    </div>

                                    <p className="text-slate-600 mb-4 text-sm">This case is ready for analysis by the AI Expert System.</p>
                                    <button 
                                        onClick={handleRunAnalysis}
                                        disabled={isAnalyzing}
                                        className="w-full rounded-md bg-blue-600 px-3.5 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 disabled:bg-slate-400"
                                    >
                                        Run Analysis ({selectedGoal.replace('_', ' ')})
                                    </button>
                                </div>
                           )}
                        </div>
                     </div>
                </div>
            </div>
        </div>
    );
};

export default CaseDetailView;
