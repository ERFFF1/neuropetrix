import { useState } from 'react';
import { gen, compare } from './api';
import { PatientCase } from '../types';

// TSNM Konfigürasyonu
const TSNM_CONFIG = {
  tsnm_defaults: {
    device_model: "Siemens Biograph mCT", 
    fdg_dose_mbq: 300,
    glycemia_mgdl: 110,
    fasting_hours: 6
  },
  report_priority_order: [
    "primer_lez", "lenf_nodu", "uzak_met", "ilk_defa", "malignite_suphe", "klinik_onem", "onerilen_mudahale"
  ]
};

interface ReportStudioProps {
  patientCase?: PatientCase;
  onReportGenerated?: (reportData: any) => void;
}

export default function ReportStudio({ patientCase, onReportGenerated }: ReportStudioProps) {
  const [patientId, setPatientId] = useState(patientCase?.id || 'P-0001');
  const [modality, setModality] = useState<'FDG' | 'TSNM'>('FDG');
  const [structured, setStructured] = useState<any>({
    primer_lez: patientCase?.tsnmReport?.structuredFindings?.primerLez || "", 
    lenf_nodu: patientCase?.tsnmReport?.structuredFindings?.lenfNodu || "", 
    uzak_met: patientCase?.tsnmReport?.structuredFindings?.uzakMet || "", 
    SUVmax: patientCase?.currentSUVmax || 0
  });
  const [chips, setChips] = useState<string[]>(patientCase?.tsnmReport?.selectedSentences || ["klinik_onem"]);
  const [prevId, setPrevId] = useState<number|undefined>(patientCase?.tsnmReport?.previousReportId);
  const [body, setBody] = useState(patientCase?.tsnmReport?.reportBody || ""); 
  const [diff, setDiff] = useState("");
  const [out, setOut] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string|null>(null);
  
  // TSNM Defaults
  const [deviceModel, setDeviceModel] = useState(patientCase?.tsnmReport?.deviceModel || TSNM_CONFIG.tsnm_defaults.device_model);
  const [fdgDose, setFdgDose] = useState(patientCase?.tsnmReport?.fdgDoseMBq || TSNM_CONFIG.tsnm_defaults.fdg_dose_mbq);
  const [glycemia, setGlycemia] = useState(patientCase?.tsnmReport?.glycemiaMgdl || TSNM_CONFIG.tsnm_defaults.glycemia_mgdl);
  const [fastingHours, setFastingHours] = useState(patientCase?.tsnmReport?.fastingHours || TSNM_CONFIG.tsnm_defaults.fasting_hours);

  async function onGenerate() {
    setLoading(true); 
    setErr(null);
    
    try {
      // Structured data'yı hazırla
      const structuredData = {
        device_model: deviceModel,
        fdg_dose_mbq: fdgDose,
        glycemia_mgdl: glycemia,
        fasting_hours: fastingHours,
        ...structured
      };

      const payload = {
        patient_id: patientId,
        modality: "FDG",
        structured: structuredData,
        options: chips,
        previous_report_id: prevId
      };

      const r = await gen(payload);
      setOut(r);
      setBody(r.body);
      
      // Önceki rapor varsa karşılaştır
      if (r.previous_report_id) {
        const d = await compare(r.report_id, r.previous_report_id);
        setDiff(d.diff_html);
      } else {
        setDiff("");
      }

      // Parent component'e bildir
      if (onReportGenerated) {
        onReportGenerated({
          reportId: r.report_id,
          version: r.version,
          body: r.body,
          structured: structuredData,
          selectedSentences: chips,
          deviceModel,
          fdgDose,
          glycemia,
          fastingHours
        });
      }
    } catch (e: any) { 
      setErr(e.message); 
    } finally { 
      setLoading(false); 
    }
  }

  const ALL = ["primer_lez", "lenf_nodu", "uzak_met", "klinik_onem", "onerilen_mudahale"];

  return (
    <div className="p-4 max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-gray-800">📝 TSNM Report Studio</h2>
        {patientCase && (
          <div className="text-sm text-gray-600">
            <span className="font-medium">Hasta:</span> {patientCase.patientInfo.name} 
            <span className="mx-2">•</span>
            <span className="font-medium">Vaka ID:</span> {patientCase.id}
          </div>
        )}
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Sol Kolon - Form */}
        <div className="space-y-6">
          {/* Hasta Bilgileri */}
          <div className="bg-blue-50 p-4 rounded-lg">
            <h3 className="text-lg font-medium text-blue-800 mb-3">👤 Hasta Bilgileri</h3>
            <div className="space-y-3">
              <input 
                className="w-full border border-blue-200 p-2 rounded focus:ring-2 focus:ring-blue-500" 
                placeholder="Patient ID" 
                value={patientId} 
                onChange={e=>setPatientId(e.target.value)} 
              />
              <input 
                type="number"
                className="w-full border border-blue-200 p-2 rounded focus:ring-2 focus:ring-blue-500" 
                placeholder="Önceki Rapor ID (opsiyonel)" 
                value={prevId || ''} 
                onChange={e=>setPrevId(e.target.value ? Number(e.target.value) : undefined)} 
              />
            </div>
          </div>

          {/* TSNM Teknik Parametreleri */}
          <div className="bg-green-50 p-4 rounded-lg">
            <h3 className="text-lg font-medium text-green-800 mb-3">⚙️ TSNM Teknik Parametreleri</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-green-700 mb-1">Cihaz Modeli</label>
                <input 
                  className="w-full border border-green-200 p-2 rounded focus:ring-2 focus:ring-green-500" 
                  value={deviceModel} 
                  onChange={e=>setDeviceModel(e.target.value)} 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-green-700 mb-1">FDG Dozu (MBq)</label>
                <input 
                  type="number"
                  className="w-full border border-green-200 p-2 rounded focus:ring-2 focus:ring-green-500" 
                  value={fdgDose} 
                  onChange={e=>setFdgDose(Number(e.target.value))} 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-green-700 mb-1">Glisemi (mg/dL)</label>
                <input 
                  type="number"
                  className="w-full border border-green-200 p-2 rounded focus:ring-2 focus:ring-green-500" 
                  value={glycemia} 
                  onChange={e=>setGlycemia(Number(e.target.value))} 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-green-700 mb-1">Açlık Süresi (saat)</label>
                <input 
                  type="number"
                  className="w-full border border-green-200 p-2 rounded focus:ring-2 focus:ring-green-500" 
                  value={fastingHours} 
                  onChange={e=>setFastingHours(Number(e.target.value))} 
                />
              </div>
            </div>
          </div>

          {/* TSNM Bulgular */}
          <div className="bg-purple-50 p-4 rounded-lg">
            <h3 className="text-lg font-medium text-purple-800 mb-3">🔍 TSNM Bulgular</h3>
            <div className="space-y-3">
              <div>
                <label className="block text-sm font-medium text-purple-700 mb-1">Primer Lezyon</label>
                <input 
                  className="w-full border border-purple-200 p-2 rounded focus:ring-2 focus:ring-purple-500" 
                  value={structured.primer_lez} 
                  onChange={e=>setStructured({...structured, primer_lez: e.target.value})} 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-purple-700 mb-1">Lenf Nodları</label>
                <input 
                  className="w-full border border-purple-200 p-2 rounded focus:ring-2 focus:ring-purple-500" 
                  value={structured.lenf_nodu} 
                  onChange={e=>setStructured({...structured, lenf_nodu: e.target.value})} 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-purple-700 mb-1">Uzak Metastaz</label>
                <input 
                  className="w-full border border-purple-200 p-2 rounded focus:ring-2 focus:ring-purple-500" 
                  value={structured.uzak_met} 
                  onChange={e=>setStructured({...structured, uzak_met: e.target.value})} 
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-purple-700 mb-1">SUVmax</label>
                <input 
                  type="number"
                  className="w-full border border-purple-200 p-2 rounded focus:ring-2 focus:ring-purple-500" 
                  value={structured.SUVmax} 
                  onChange={e=>setStructured({...structured, SUVmax: Number(e.target.value)})} 
                />
              </div>
            </div>
          </div>

          {/* Cümle Seçenekleri */}
          <div className="bg-orange-50 p-4 rounded-lg">
            <h3 className="text-lg font-medium text-orange-800 mb-3">🎯 Cümle Seçenekleri</h3>
            <div className="flex gap-2 flex-wrap">
              {ALL.map(k => (
                <button 
                  key={k}
                  onClick={() => setChips(p => p.includes(k) ? p.filter(x => x !== k) : [...p, k])}
                  className={`px-3 py-1 rounded-full border transition-colors ${
                    chips.includes(k) 
                      ? "bg-black text-white border-black" 
                      : "bg-white text-gray-700 border-gray-300 hover:border-gray-400"
                  }`}
                >
                  {k.replace(/_/g, ' ')}
                </button>
              ))}
            </div>
          </div>

          {/* Üret Butonu */}
          <button 
            onClick={onGenerate} 
            disabled={loading} 
            className="w-full px-6 py-3 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 text-white font-semibold text-lg hover:from-blue-600 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200"
          >
            {loading ? '🔄 Rapor Üretiliyor...' : '🚀 TSNM Raporunu Üret'}
          </button>
        </div>

        {/* Sağ Kolon - Sonuç */}
        <div className="space-y-6">
          {/* Hata Mesajı */}
          {err && (
            <div className="bg-red-50 border border-red-200 p-4 rounded-lg">
              <pre className="text-red-600 text-sm">{err}</pre>
            </div>
          )}

          {/* Rapor Sonucu */}
          {out && (
            <div className="bg-gray-50 border border-gray-200 p-4 rounded-lg">
              <h3 className="text-lg font-medium text-gray-800 mb-3">📊 Üretilen Rapor</h3>
              <div className="bg-white p-4 rounded border overflow-auto max-h-96">
                <h4 className="font-medium mb-2">Rapor ID: {out.report_id}</h4>
                <h4 className="font-medium mb-2">Versiyon: {out.version}</h4>
                <h4 className="font-medium mb-2">Modalite: {out.modality}</h4>
                <hr className="my-3" />
                <div className="whitespace-pre-wrap text-sm">{out.body}</div>
              </div>
            </div>
          )}

          {/* Tabs */}
          {(body || diff) && (
            <div className="bg-white border border-gray-200 rounded-lg">
              <div className="border-b border-gray-200">
                <nav className="flex space-x-8 px-6" aria-label="Tabs">
                  <button
                    className={`py-2 px-1 border-b-2 font-medium text-sm ${
                      body && !diff ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-slate-700 hover:border-gray-300'
                    }`}
                  >
                    📝 Rapor Markdown
                  </button>
                  {diff && (
                    <button
                      className={`py-2 px-1 border-b-2 font-medium text-sm ${
                        diff ? 'border-blue-500 text-blue-600' : 'border-transparent text-gray-500 hover:text-slate-700 hover:border-gray-300'
                      }`}
                    >
                      🔄 Değişiklikler
                    </button>
                  )}
                </nav>
              </div>
              
              <div className="p-6">
                {body && !diff && (
                  <div className="whitespace-pre-wrap text-sm bg-gray-50 p-4 rounded border overflow-auto max-h-96">
                    {body}
                  </div>
                )}
                
                {diff && (
                  <div 
                    className="text-sm bg-gray-50 p-4 rounded border overflow-auto max-h-96"
                    dangerouslySetInnerHTML={{ __html: diff }}
                  />
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

