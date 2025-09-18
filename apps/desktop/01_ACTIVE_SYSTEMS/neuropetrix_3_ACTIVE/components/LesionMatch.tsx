import { useState } from "react";
const API = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export default function LesionMatch() {
  const [pid, setPid] = useState("P-0001");
  const [prevDate, setPrev] = useState("2025-07-01");
  const [currDate, setCurr] = useState("2025-08-01");
  const [pairs, setPairs] = useState<any[]>([
    { prev: "L1_RUL", curr: "L1_RUL", confidence: 0.91, id: 1, corrected: false },
    { prev: "L2_LLL", curr: "L3_LLL", confidence: 0.62, id: 2, corrected: false },
    { prev: "L3_RML", curr: "L3_RML", confidence: 0.87, id: 3, corrected: false },
    { prev: "L4_RLL", curr: "L4_RLL", confidence: 0.94, id: 4, corrected: false },
  ]);

  async function saveAuto() {
    try {
      await fetch(`${API}/lesion/match/auto`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          patient_id: pid,
          prev_study_date: prevDate,
          curr_study_date: currDate,
          suggestions: pairs.map(p => ({
            prev_lesion_key: p.prev,
            curr_lesion_key: p.curr,
            confidence: p.confidence
          }))
        })
      });
      alert("✅ Auto eşleştirme kaydedildi.");
    } catch (error) {
      console.error("Auto eşleştirme hatası:", error);
      alert("⚠️ Demo mod: Auto eşleştirme simüle edildi.");
    }
  }

  async function correct(ids: number[]) {
    try {
      await fetch(`${API}/lesion/match/correct`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ids })
      });
      alert("✅ Düzeltme işaretlendi.");
    } catch (error) {
      console.error("Düzeltme hatası:", error);
      alert("⚠️ Demo mod: Düzeltme simüle edildi.");
    }
    
    // Local state güncelle
    setPairs(pairs.map(p => 
      ids.includes(p.id) ? { ...p, corrected: true } : p
    ));
  }

  const autoMatchCount = pairs.filter(p => p.confidence >= 0.85).length;
  const manualCorrectionCount = pairs.filter(p => p.confidence < 0.85).length;

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-semibold text-gray-800">🔍 Lezyon Eşleşme & Düzeltme</h2>
        <div className="flex items-center gap-4">
          <div className="text-sm text-gray-600">
            <span className="font-medium">Auto:</span> {autoMatchCount} | 
            <span className="font-medium ml-2">Manuel:</span> {manualCorrectionCount}
          </div>
        </div>
      </div>

      {/* Input Controls */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="text-lg font-medium text-blue-800 mb-3">📋 Çalışma Parametreleri</h3>
        <div className="grid grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-blue-700 mb-1">Hasta ID</label>
            <input 
              value={pid} 
              onChange={e => setPid(e.target.value)} 
              className="w-full border border-blue-200 rounded px-3 py-2 focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-blue-700 mb-1">Önceki Çalışma</label>
            <input 
              type="date"
              value={prevDate} 
              onChange={e => setPrev(e.target.value)} 
              className="w-full border border-blue-200 rounded px-3 py-2 focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-blue-700 mb-1">Mevcut Çalışma</label>
            <input 
              type="date"
              value={currDate} 
              onChange={e => setCurr(e.target.value)} 
              className="w-full border border-blue-200 rounded px-3 py-2 focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="flex items-end">
            <button 
              onClick={saveAuto} 
              className="w-full px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 focus:ring-2 focus:ring-blue-500"
            >
              💾 Kaydet (Auto)
            </button>
          </div>
        </div>
      </div>

      {/* Eşleşme Tablosu */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-800">📊 Lezyon Eşleşme Sonuçları</h3>
          <p className="text-sm text-gray-600 mt-1">
            %85+ güven: Auto eşleşme | %85- güven: Manuel düzeltme gerekli
          </p>
        </div>
        
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Önceki Lezyon
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Mevcut Lezyon
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Güven
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Durum
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  İşlem
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {pairs.map((pair, index) => (
                <tr 
                  key={pair.id} 
                  className={`hover:bg-gray-50 ${
                    pair.confidence >= 0.85 ? 'bg-green-50' : 'bg-yellow-50'
                  }`}
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {pair.prev}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {pair.curr}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        pair.confidence >= 0.85 
                          ? 'bg-green-100 text-green-800' 
                          : pair.confidence >= 0.70 
                          ? 'bg-yellow-100 text-yellow-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {Math.round(pair.confidence * 100)}%
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <div className="flex items-center">
                      {pair.confidence >= 0.85 ? (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          ✅ Auto Eşleşme
                        </span>
                      ) : (
                        <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                          ⚠️ Manuel Düzeltme
                        </span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    {pair.corrected ? (
                      <span className="text-green-600">✅ Düzeltildi</span>
                    ) : (
                      <button 
                        className="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50 focus:ring-2 focus:ring-blue-500"
                        onClick={() => correct([pair.id])}
                      >
                        Düzelt
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Özet İstatistikler */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-green-600">{autoMatchCount}</div>
          <div className="text-sm text-green-700">Auto Eşleşme</div>
          <div className="text-xs text-green-600">%85+ güven</div>
        </div>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-yellow-600">{manualCorrectionCount}</div>
          <div className="text-sm text-yellow-700">Manuel Düzeltme</div>
          <div className="text-xs text-yellow-600">%85- güven</div>
        </div>
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
          <div className="text-2xl font-bold text-blue-600">{Math.round((autoMatchCount / pairs.length) * 100)}%</div>
          <div className="text-sm text-blue-700">Auto Başarı</div>
          <div className="text-xs text-blue-600">Toplam eşleşme</div>
        </div>
      </div>

      {/* Kullanım Talimatları */}
      <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
        <h3 className="text-lg font-medium text-gray-800 mb-2">ℹ️ Kullanım Talimatları</h3>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• <strong>%85+ güven:</strong> Otomatik eşleşme, hekim onayı gerekmez</li>
          <li>• <strong>%85- güven:</strong> Manuel düzeltme gerekli, "Düzelt" butonuna tıklayın</li>
          <li>• <strong>Auto eşleştirme:</strong> AI modeli önerileri kaydeder</li>
          <li>• <strong>Manuel düzeltme:</strong> Hekim düzeltmeleri işaretlenir</li>
          <li>• <strong>Gerçek veri için:</strong> Backend'de /lesion/match/auto endpoint'i kullanın</li>
        </ul>
      </div>
    </div>
  );
}
