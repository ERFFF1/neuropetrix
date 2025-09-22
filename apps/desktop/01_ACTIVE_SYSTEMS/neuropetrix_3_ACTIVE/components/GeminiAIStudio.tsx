import React, { useState, useEffect } from 'react';

interface GeminiAIStudioProps {
  onClose?: () => void;
}

interface AIConclusion {
  ai_conclusion: string;
  rationale_keys: string[];
  optional: {
    percist?: string;
    deauville?: number;
    qc_flags?: string[];
    grade_summary?: string;
    refs?: string[];
  };
  created_at: string;
  model_version: string;
}

export default function GeminiAIStudio({ onClose }: GeminiAIStudioProps) {
  const [clinicalGoal, setClinicalGoal] = useState('response');
  const [imagingAvailable, setImagingAvailable] = useState(true);
  const [suvmax, setSuvmax] = useState(8.5);
  const [mtv, setMtv] = useState(12.3);
  const [percist, setPercist] = useState('PMR');
  const [deauville, setDeauville] = useState(2);
  const [qcFlags, setQcFlags] = useState<string[]>(['normal_glucose']);
  const [evidenceSummary, setEvidenceSummary] = useState('Strong evidence supports PET/CT use');
  const [aiConclusion, setAiConclusion] = useState<AIConclusion | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const generateAIConclusion = async () => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/gemini/generate-conclusion', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          clinical_goal: clinicalGoal,
          imaging_available: imagingAvailable,
          imaging_metrics: {
            suvmax: parseFloat(suvmax.toString()),
            mtv: parseFloat(mtv.toString()),
            tlg: parseFloat(suvmax.toString()) * parseFloat(mtv.toString()),
            percist: percist,
            deauville: parseInt(deauville.toString())
          },
          qc_flags: qcFlags,
          evidence_summary: evidenceSummary
        })
      });

      if (response.ok) {
        const data = await response.json();
        setAiConclusion(data.data);
      } else {
        throw new Error('AI conclusion generation failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error');
    } finally {
      setIsLoading(false);
    }
  };

  const addQcFlag = () => {
    const newFlag = prompt('Yeni QC flag ekle:');
    if (newFlag && !qcFlags.includes(newFlag)) {
      setQcFlags([...qcFlags, newFlag]);
    }
  };

  const removeQcFlag = (flag: string) => {
    setQcFlags(qcFlags.filter(f => f !== flag));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-2xl max-w-4xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-pink-600 text-white p-6 rounded-t-xl">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold flex items-center">
              🤖 Gemini AI Studio
            </h2>
            <button
              onClick={onClose}
              className="text-white hover:text-gray-200 text-2xl"
            >
              ×
            </button>
          </div>
          <p className="text-purple-100 mt-2">
            AI destekli klinik karar verme sistemi
          </p>
        </div>

        <div className="p-6">
          {/* Input Form */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {/* Left Column */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Klinik Amaç
                </label>
                <select
                  value={clinicalGoal}
                  onChange={(e) => setClinicalGoal(e.target.value)}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                >
                  <option value="staging">Staging</option>
                  <option value="response">Response</option>
                  <option value="lymphoma_followup">Lymphoma Follow-up</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Görüntüleme Mevcut
                </label>
                <div className="flex items-center space-x-4">
                  <label className="flex items-center">
                    <input
                      type="radio"
                      checked={imagingAvailable}
                      onChange={() => setImagingAvailable(true)}
                      className="mr-2"
                    />
                    Evet
                  </label>
                  <label className="flex items-center">
                    <input
                      type="radio"
                      checked={!imagingAvailable}
                      onChange={() => setImagingAvailable(false)}
                      className="mr-2"
                    />
                    Hayır
                  </label>
                </div>
              </div>

              {imagingAvailable && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      SUVmax (g/ml)
                    </label>
                    <input
                      type="number"
                      value={suvmax}
                      onChange={(e) => setSuvmax(parseFloat(e.target.value))}
                      step="0.1"
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      MTV (cc)
                    </label>
                    <input
                      type="number"
                      value={mtv}
                      onChange={(e) => setMtv(parseFloat(e.target.value))}
                      step="0.1"
                      className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>

                  {clinicalGoal === 'response' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        PERCIST Skoru
                      </label>
                      <select
                        value={percist}
                        onChange={(e) => setPercist(e.target.value)}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      >
                        <option value="PMR">PMR (Partial Metabolic Response)</option>
                        <option value="SMD">SMD (Stable Metabolic Disease)</option>
                        <option value="PMD">PMD (Progressive Metabolic Disease)</option>
                        <option value="SDP">SDP (Stable Disease with Progression)</option>
                      </select>
                    </div>
                  )}

                  {clinicalGoal === 'lymphoma_followup' && (
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Deauville Skoru
                      </label>
                      <select
                        value={deauville}
                        onChange={(e) => setDeauville(parseInt(e.target.value))}
                        className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                      >
                        <option value={1}>1 - No uptake above background</option>
                        <option value={2}>2 - Uptake ≤ mediastinum</option>
                        <option value={3}>3 - Uptake > mediastinum but ≤ liver</option>
                        <option value={4}>4 - Uptake moderately higher than liver</option>
                        <option value={5}>5 - Uptake markedly higher than liver</option>
                      </select>
                    </div>
                  )}
                </>
              )}
            </div>

            {/* Right Column */}
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  QC Flags
                </label>
                <div className="space-y-2">
                  {qcFlags.map((flag, index) => (
                    <div key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                      <span className="text-sm">{flag}</span>
                      <button
                        onClick={() => removeQcFlag(flag)}
                        className="text-red-500 hover:text-red-700 text-sm"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                  <button
                    onClick={addQcFlag}
                    className="w-full p-2 border-2 border-dashed border-gray-300 rounded text-gray-500 hover:border-gray-400 hover:text-gray-600"
                  >
                    + QC Flag Ekle
                  </button>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Kanıt Özeti
                </label>
                <textarea
                  value={evidenceSummary}
                  onChange={(e) => setEvidenceSummary(e.target.value)}
                  rows={4}
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  placeholder="Kanıt özetini girin..."
                />
              </div>

              <button
                onClick={generateAIConclusion}
                disabled={isLoading}
                className="w-full bg-gradient-to-r from-purple-600 to-pink-600 text-white py-3 px-6 rounded-lg font-semibold hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
              >
                {isLoading ? '🤖 AI Sonucu Üretiliyor...' : '🚀 AI Sonucu Üret'}
              </button>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-800">❌ Hata: {error}</p>
            </div>
          )}

          {/* AI Conclusion Display */}
          {aiConclusion && (
            <div className="bg-gradient-to-r from-green-50 to-blue-50 border border-green-200 rounded-xl p-6">
              <h3 className="text-xl font-bold text-green-900 mb-4 flex items-center">
                🎯 AI Sonucu
                <span className="ml-2 text-sm font-normal text-green-600">
                  {aiConclusion.model_version}
                </span>
              </h3>
              
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold text-green-800 mb-2">Ana Sonuç</h4>
                  <p className="text-lg font-medium text-green-900 bg-white p-3 rounded border">
                    {aiConclusion.ai_conclusion}
                  </p>
                </div>

                <div>
                  <h4 className="font-semibold text-green-800 mb-2">Gerekçe</h4>
                  <div className="flex flex-wrap gap-2">
                    {aiConclusion.rationale_keys.map((key, index) => (
                      <span key={index} className="px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm">
                        {key}
                      </span>
                    ))}
                  </div>
                </div>

                {aiConclusion.optional.percist && (
                  <div>
                    <h4 className="font-semibold text-green-800 mb-2">PERCIST</h4>
                    <p className="text-lg font-medium text-green-900 bg-white p-3 rounded border">
                      {aiConclusion.optional.percist}
                    </p>
                  </div>
                )}

                {aiConclusion.optional.deauville && (
                  <div>
                    <h4 className="font-semibold text-green-800 mb-2">Deauville Skoru</h4>
                    <p className="text-lg font-medium text-green-900 bg-white p-3 rounded border">
                      {aiConclusion.optional.deauville}
                    </p>
                  </div>
                )}

                {aiConclusion.optional.qc_flags && aiConclusion.optional.qc_flags.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-green-800 mb-2">QC Uyarıları</h4>
                    <div className="space-y-1">
                      {aiConclusion.optional.qc_flags.map((flag, index) => (
                        <p key={index} className="text-sm text-green-800 bg-white p-2 rounded border">
                          ⚠️ {flag}
                        </p>
                      ))}
                    </div>
                  </div>
                )}

                {aiConclusion.optional.grade_summary && (
                  <div>
                    <h4 className="font-semibold text-green-800 mb-2">Kanıt Kalitesi</h4>
                    <p className="text-lg font-medium text-green-900 bg-white p-3 rounded border">
                      {aiConclusion.optional.grade_summary}
                    </p>
                  </div>
                )}

                {aiConclusion.optional.refs && aiConclusion.optional.refs.length > 0 && (
                  <div className="lg:col-span-2">
                    <h4 className="font-semibold text-green-800 mb-2">Referanslar</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                      {aiConclusion.optional.refs.map((ref, index) => (
                        <p key={index} className="text-sm text-green-800 bg-white p-2 rounded border">
                          📚 {ref}
                        </p>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="mt-4 text-right text-sm text-green-600">
                Oluşturulma: {new Date(aiConclusion.created_at).toLocaleString('tr-TR')}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}


