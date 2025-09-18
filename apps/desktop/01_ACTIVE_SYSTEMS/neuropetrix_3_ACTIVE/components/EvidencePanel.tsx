import React, { useState } from 'react';

interface PatientCase {
  id: string;
  name: string;
  age: number;
  gender: string;
  diagnosis: string;
}

interface EvidencePanelProps {
  patientCase: PatientCase | null;
}

export default function EvidencePanel({ patientCase }: EvidencePanelProps) {
  const [activeTab, setActiveTab] = useState<'pico' | 'search' | 'appraisal' | 'recommendations'>('pico');
  const [picoQuestion, setPicoQuestion] = useState({
    population: '',
    intervention: '',
    comparison: '',
    outcome: ''
  });
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [selectedEvidence, setSelectedEvidence] = useState<any>(null);

  const handlePICOGeneration = () => {
    // Mock PICO generation
    setPicoQuestion({
      population: '65 yaş üstü akciğer kanseri hastaları',
      intervention: 'PET/CT ile erken tanı',
      comparison: 'Standart görüntüleme yöntemleri',
      outcome: 'Survival ve yaşam kalitesi'
    });
  };

  const handleEvidenceSearch = () => {
    // Mock search results
    setSearchResults([
      {
        id: 1,
        title: 'PET/CT in Early Lung Cancer Detection',
        authors: 'Smith et al.',
        journal: 'Journal of Nuclear Medicine',
        year: 2023,
        evidenceLevel: 'Level 1',
        relevance: 'High',
        abstract: 'Systematic review of PET/CT effectiveness in early lung cancer detection...'
      },
      {
        id: 2,
        title: 'Comparative Analysis of Imaging Modalities',
        authors: 'Johnson et al.',
        journal: 'Radiology',
        year: 2022,
        evidenceLevel: 'Level 2',
        relevance: 'Medium',
        abstract: 'Meta-analysis comparing PET/CT with other imaging modalities...'
      }
    ]);
  };

  return (
    <div className="p-6 bg-medical-50 min-h-full">
      <div className="max-w-7xl mx-auto">
        {/* Başlık */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-800 mb-2">
            🔬 Evidence Panel
          </h1>
          <p className="text-slate-600">
            Kanıta dayalı tıp araçları ve literatür analizi
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="bg-white rounded-lg shadow-md border border-medical-200 mb-6">
          <div className="border-b border-medical-200">
            <nav className="flex space-x-8 px-6">
              {[
                { key: 'pico', label: 'PICO Soru', icon: '🔍' },
                { key: 'search', label: 'Literatür Arama', icon: '📚' },
                { key: 'appraisal', label: 'Eleştirel Değerlendirme', icon: '🔬' },
                { key: 'recommendations', label: 'Öneriler', icon: '💡' }
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key as any)}
                  className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.key
                      ? 'border-medical-500 text-medical-600'
                      : 'border-transparent text-slate-500 hover:text-slate-700 hover:border-slate-300'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {/* PICO Soru Tab */}
            {activeTab === 'pico' && (
              <div className="space-y-6">
                <h3 className="text-xl font-semibold text-slate-800">🔍 PICO Soru Oluşturma</h3>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Population (Popülasyon)</label>
                    <textarea
                      value={picoQuestion.population}
                      onChange={(e) => setPicoQuestion({...picoQuestion, population: e.target.value})}
                      className="w-full p-3 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500 focus:border-medical-500"
                      rows={3}
                      placeholder="Hasta popülasyonu tanımı..."
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Intervention (Müdahale)</label>
                    <textarea
                      value={picoQuestion.intervention}
                      onChange={(e) => setPicoQuestion({...picoQuestion, intervention: e.target.value})}
                      className="w-full p-3 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500 focus:border-medical-500"
                      rows={3}
                      placeholder="Tedavi/müdahale tanımı..."
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Comparison (Karşılaştırma)</label>
                    <textarea
                      value={picoQuestion.comparison}
                      onChange={(e) => setPicoQuestion({...picoQuestion, comparison: e.target.value})}
                      className="w-full p-3 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500 focus:border-medical-500"
                      rows={3}
                      placeholder="Karşılaştırma grubu..."
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-slate-700 mb-2">Outcome (Sonuç)</label>
                    <textarea
                      value={picoQuestion.outcome}
                      onChange={(e) => setPicoQuestion({...picoQuestion, outcome: e.target.value})}
                      className="w-full p-3 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500 focus:border-medical-500"
                      rows={3}
                      placeholder="Beklenen sonuç..."
                    />
                  </div>
                </div>

                <div className="flex space-x-4">
                  <button
                    onClick={handlePICOGeneration}
                    className="bg-medical-600 text-white px-6 py-3 rounded-md hover:bg-medical-700 transition-colors duration-200"
                  >
                    AI ile PICO Oluştur
                  </button>
                  <button
                    onClick={() => setActiveTab('search')}
                    className="bg-success-600 text-white px-6 py-3 rounded-md hover:bg-success-700 transition-colors duration-200"
                  >
                    Literatür Ara
                  </button>
                </div>
              </div>
            )}

            {/* Literatür Arama Tab */}
            {activeTab === 'search' && (
              <div className="space-y-6">
                <h3 className="text-xl font-semibold text-slate-800">📚 Literatür Arama</h3>
                
                <div className="bg-medical-50 p-4 rounded-lg">
                  <h4 className="font-medium text-slate-700 mb-2">Arama Kriterleri:</h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-slate-600">Veritabanı</label>
                      <select className="w-full p-2 border border-medical-300 rounded-md">
                        <option>PubMed</option>
                        <option>Cochrane</option>
                        <option>Embase</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-600">Tarih Aralığı</label>
                      <select className="w-full p-2 border border-medical-300 rounded-md">
                        <option>Son 5 yıl</option>
                        <option>Son 10 yıl</option>
                        <option>Tümü</option>
                      </select>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-slate-600">Kanıt Seviyesi</label>
                      <select className="w-full p-2 border border-medical-300 rounded-md">
                        <option>Tümü</option>
                        <option>Level 1</option>
                        <option>Level 2</option>
                        <option>Level 3</option>
                      </select>
                    </div>
                  </div>
                </div>

                <button
                  onClick={handleEvidenceSearch}
                  className="bg-medical-600 text-white px-6 py-3 rounded-md hover:bg-medical-700 transition-colors duration-200"
                >
                  Arama Başlat
                </button>

                {searchResults.length > 0 && (
                  <div className="space-y-4">
                    <h4 className="font-medium text-slate-700">Arama Sonuçları:</h4>
                    {searchResults.map((result) => (
                      <div key={result.id} className="border border-medical-200 rounded-lg p-4 hover:bg-medical-50 cursor-pointer">
                        <div className="flex justify-between items-start mb-2">
                          <h5 className="font-medium text-slate-800">{result.title}</h5>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            result.evidenceLevel === 'Level 1' ? 'bg-success-100 text-success-700' :
                            result.evidenceLevel === 'Level 2' ? 'bg-warning-100 text-warning-700' :
                            'bg-slate-100 text-slate-700'
                          }`}>
                            {result.evidenceLevel}
                          </span>
                        </div>
                        <p className="text-sm text-slate-600 mb-2">{result.authors} - {result.journal} ({result.year})</p>
                        <p className="text-sm text-slate-700">{result.abstract}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Eleştirel Değerlendirme Tab */}
            {activeTab === 'appraisal' && (
              <div className="space-y-6">
                <h3 className="text-xl font-semibold text-slate-800">🔬 Eleştirel Değerlendirme</h3>
                
                <div className="bg-medical-50 p-4 rounded-lg">
                  <h4 className="font-medium text-slate-700 mb-4">GRADE Kriterleri:</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <div className="flex items-center">
                        <input type="checkbox" className="mr-2" />
                        <span className="text-sm">Randomizasyon</span>
                      </div>
                      <div className="flex items-center">
                        <input type="checkbox" className="mr-2" />
                        <span className="text-sm">Blinding</span>
                      </div>
                      <div className="flex items-center">
                        <input type="checkbox" className="mr-2" />
                        <span className="text-sm">Allocation Concealment</span>
                      </div>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center">
                        <input type="checkbox" className="mr-2" />
                        <span className="text-sm">Incomplete Outcome Data</span>
                      </div>
                      <div className="flex items-center">
                        <input type="checkbox" className="mr-2" />
                        <span className="text-sm">Selective Reporting</span>
                      </div>
                      <div className="flex items-center">
                        <input type="checkbox" className="mr-2" />
                        <span className="text-sm">Other Bias</span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-white border border-medical-200 rounded-lg p-4">
                  <h4 className="font-medium text-slate-700 mb-2">Değerlendirme Sonucu:</h4>
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <span className="text-sm text-slate-600">Kalite Skoru:</span>
                      <div className="text-lg font-bold text-medical-600">8/10</div>
                    </div>
                    <div>
                      <span className="text-sm text-slate-600">Öneri Gücü:</span>
                      <div className="text-lg font-bold text-success-600">Güçlü</div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Öneriler Tab */}
            {activeTab === 'recommendations' && (
              <div className="space-y-6">
                <h3 className="text-xl font-semibold text-slate-800">💡 Klinik Öneriler</h3>
                
                <div className="bg-success-50 border border-success-200 rounded-lg p-4">
                  <h4 className="font-medium text-success-800 mb-2">Önerilen Yaklaşım:</h4>
                  <p className="text-success-700">
                    PET/CT incelemesi akciğer kanseri şüphesi olan hastalarda erken tanı için önerilir. 
                    Yüksek duyarlılık ve özgüllük değerleri nedeniyle standart görüntüleme yöntemlerine 
                    üstünlük sağlar.
                  </p>
                </div>

                <div className="bg-warning-50 border border-warning-200 rounded-lg p-4">
                  <h4 className="font-medium text-warning-800 mb-2">Dikkat Edilmesi Gerekenler:</h4>
                  <ul className="text-warning-700 space-y-1">
                    <li>• Yanlış pozitif sonuçlar için dikkatli olunmalı</li>
                    <li>• Maliyet-etkinlik analizi yapılmalı</li>
                    <li>• Radyasyon maruziyeti değerlendirilmeli</li>
                  </ul>
                </div>

                <div className="bg-medical-50 border border-medical-200 rounded-lg p-4">
                  <h4 className="font-medium text-medical-800 mb-2">Uygulama Planı:</h4>
                  <ol className="text-medical-700 space-y-1">
                    <li>1. Hasta onamı alınması</li>
                    <li>2. PET/CT protokolü belirlenmesi</li>
                    <li>3. İnceleme sonrası değerlendirme</li>
                    <li>4. Sonuçların hasta ile paylaşılması</li>
                  </ol>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Hızlı Eylemler */}
        <div className="bg-white rounded-lg shadow-md border border-medical-200 p-6">
          <h3 className="text-lg font-semibold text-slate-800 mb-4">⚡ Hızlı Eylemler</h3>
          
          <div className="flex flex-wrap gap-4">
            <button className="bg-medical-600 text-white px-4 py-2 rounded-md hover:bg-medical-700 transition-colors duration-200">
              📊 Rapor Oluştur
            </button>
            <button className="bg-success-600 text-white px-4 py-2 rounded-md hover:bg-success-700 transition-colors duration-200">
              📚 Literatür Özeti
            </button>
            <button className="bg-warning-600 text-white px-4 py-2 rounded-md hover:bg-warning-700 transition-colors duration-200">
              🔄 Güncelle
            </button>
            <button className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700 transition-colors duration-200">
              💾 Kaydet
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
