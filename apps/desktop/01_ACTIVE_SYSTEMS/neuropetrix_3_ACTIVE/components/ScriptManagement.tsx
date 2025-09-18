import React, { useState } from 'react';

interface Script {
  id: string;
  name: string;
  description: string;
  category: 'AI/ML' | 'Veri İşleme' | 'Rapor Üretimi' | 'Sistem Yönetimi';
  status: 'active' | 'inactive' | 'error';
  lastRun: string;
  fileSize: string;
  dependencies: string[];
}

const ScriptManagement: React.FC = () => {
  const [scripts, setScripts] = useState<Script[]>([
    {
      id: '1',
      name: 'whisper_transkript.py',
      description: 'Ses dosyalarını metne çeviren Whisper AI entegrasyonu',
      category: 'AI/ML',
      status: 'active',
      lastRun: '2024-08-24 15:30:00',
      fileSize: '45.2 KB',
      dependencies: ['whisper', 'torch', 'numpy']
    },
    {
      id: '2',
      name: 'gpt_log_service.py',
      description: 'GPT API çağrılarını loglayan ve yöneten servis',
      category: 'AI/ML',
      status: 'active',
      lastRun: '2024-08-24 14:45:00',
      fileSize: '32.1 KB',
      dependencies: ['openai', 'sqlite3', 'fastapi']
    },
    {
      id: '3',
      name: 'pet_rapor_service.py',
      description: 'PET/CT raporları otomatik oluşturan servis',
      category: 'Rapor Üretimi',
      status: 'active',
      lastRun: '2024-08-24 13:20:00',
      fileSize: '67.8 KB',
      dependencies: ['pydicom', 'reportlab', 'jinja2']
    },
    {
      id: '4',
      name: 'dicom_processor.py',
      description: 'DICOM dosyalarını işleyen ve analiz eden modül',
      category: 'Veri İşleme',
      status: 'active',
      lastRun: '2024-08-24 12:15:00',
      fileSize: '28.9 KB',
      dependencies: ['pydicom', 'numpy', 'matplotlib']
    },
    {
      id: '5',
      name: 'ai_pipeline.py',
      description: 'AI modellerini sırayla çalıştıran pipeline',
      category: 'AI/ML',
      status: 'inactive',
      lastRun: '2024-08-23 18:00:00',
      fileSize: '89.3 KB',
      dependencies: ['torch', 'transformers', 'scikit-learn']
    }
  ]);

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedStatus, setSelectedStatus] = useState<string>('all');
  const [showAddForm, setShowAddForm] = useState(false);
  const [newScript, setNewScript] = useState<Omit<Script, 'id' | 'lastRun' | 'status'>>({
    name: '',
    description: '',
    category: 'AI/ML',
    fileSize: '',
    dependencies: []
  });

  // Script'leri filtrele
  const filteredScripts = scripts.filter(script => {
    const matchesSearch = script.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         script.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesCategory = selectedCategory === 'all' || script.category === selectedCategory;
    const matchesStatus = selectedStatus === 'all' || script.status === selectedStatus;
    
    return matchesSearch && matchesCategory && matchesStatus;
  });

  // Script çalıştır
  const runScript = async (scriptId: string) => {
    const script = scripts.find(s => s.id === scriptId);
    if (!script) return;

    try {
      // Mock script execution
      console.log(`Çalıştırılıyor: ${script.name}`);
      
      // Status'u güncelle
      setScripts(prev => prev.map(s => 
        s.id === scriptId 
          ? { ...s, status: 'active', lastRun: new Date().toLocaleString('tr-TR') }
          : s
      ));

      alert(`${script.name} başarıyla çalıştırıldı!`);
    } catch (error) {
      console.error('Script çalıştırma hatası:', error);
      alert('Script çalıştırılırken hata oluştu');
    }
  };

  // Script düzenle
  const editScript = (scriptId: string) => {
    const script = scripts.find(s => s.id === scriptId);
    if (!script) return;

    setNewScript({
      name: script.name,
      description: script.description,
      category: script.category,
      fileSize: script.fileSize,
      dependencies: script.dependencies
    });
    setShowAddForm(true);
  };

  // Script sil
  const deleteScript = (scriptId: string) => {
    if (confirm('Bu script\'i silmek istediğinizden emin misiniz?')) {
      setScripts(prev => prev.filter(s => s.id !== scriptId));
    }
  };

  // Yeni script ekle
  const addScript = () => {
    if (!newScript.name || !newScript.description) {
      alert('Lütfen tüm alanları doldurun');
      return;
    }

    const script: Script = {
      ...newScript,
      id: Date.now().toString(),
      status: 'inactive',
      lastRun: 'Hiç çalıştırılmadı'
    };

    setScripts(prev => [...prev, script]);
    setNewScript({ name: '', description: '', category: 'AI/ML', fileSize: '', dependencies: [] });
    setShowAddForm(false);
  };

  // Toplu işlem
  const bulkAction = (action: 'run' | 'stop' | 'delete') => {
    const selectedScripts = filteredScripts.filter(s => s.status === 'active');
    
    if (selectedScripts.length === 0) {
      alert('İşlem yapılacak aktif script bulunamadı');
      return;
    }

    switch (action) {
      case 'run':
        selectedScripts.forEach(script => runScript(script.id));
        break;
      case 'stop':
        setScripts(prev => prev.map(s => 
          selectedScripts.some(selected => selected.id === s.id) 
            ? { ...s, status: 'inactive' }
            : s
        ));
        break;
      case 'delete':
        if (confirm(`${selectedScripts.length} script'i silmek istediğinizden emin misiniz?`)) {
          setScripts(prev => prev.filter(s => !selectedScripts.some(selected => selected.id === s.id)));
        }
        break;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'inactive': return 'bg-gray-100 text-gray-800';
      case 'error': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'active': return 'Aktif';
      case 'inactive': return 'Pasif';
      case 'error': return 'Hata';
      default: return 'Bilinmiyor';
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'AI/ML': return 'bg-purple-100 text-purple-800';
      case 'Veri İşleme': return 'bg-blue-100 text-blue-800';
      case 'Rapor Üretimi': return 'bg-green-100 text-green-800';
      case 'Sistem Yönetimi': return 'bg-orange-100 text-orange-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Başlık */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-800">
            Script Yönetimi
          </h1>
          <p className="text-slate-600 mt-2">
            Proje script'lerini organize et ve yönet
          </p>
        </div>

        {/* Kontrol Paneli */}
        <div className="bg-white rounded-lg shadow-md border border-slate-200 mb-6">
          <div className="p-6">
            <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between">
              <div className="flex flex-col lg:flex-row gap-4 flex-1">
                {/* Arama */}
                <div className="flex-1">
                  <input
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Script adı veya açıklama ara..."
                    className="w-full p-3 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                {/* Kategori Filtresi */}
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="p-3 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">Tüm Kategoriler</option>
                  <option value="AI/ML">AI/ML</option>
                  <option value="Veri İşleme">Veri İşleme</option>
                  <option value="Rapor Üretimi">Rapor Üretimi</option>
                  <option value="Sistem Yönetimi">Sistem Yönetimi</option>
                </select>

                {/* Durum Filtresi */}
                <select
                  value={selectedStatus}
                  onChange={(e) => setSelectedStatus(e.target.value)}
                  className="p-3 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">Tüm Durumlar</option>
                  <option value="active">Aktif</option>
                  <option value="inactive">Pasif</option>
                  <option value="error">Hata</option>
                </select>
              </div>

              {/* Yeni Script Ekle */}
              <button
                onClick={() => setShowAddForm(true)}
                className="bg-blue-600 text-white px-4 py-3 rounded-md hover:bg-blue-700"
              >
                Yeni Script Ekle
              </button>
            </div>

            {/* Toplu İşlem Butonları */}
            <div className="mt-4 flex flex-wrap gap-2">
              <button
                onClick={() => bulkAction('run')}
                className="bg-green-600 text-white px-3 py-2 rounded-md hover:bg-green-700 text-sm"
              >
                Seçili Script'leri Çalıştır
              </button>
              <button
                onClick={() => bulkAction('stop')}
                className="bg-yellow-600 text-white px-3 py-2 rounded-md hover:bg-yellow-700 text-sm"
              >
                Seçili Script'leri Durdur
              </button>
              <button
                onClick={() => bulkAction('delete')}
                className="bg-red-600 text-white px-3 py-2 rounded-md hover:bg-red-700 text-sm"
              >
                Seçili Script'leri Sil
              </button>
            </div>
          </div>
        </div>

        {/* Script Listesi */}
        <div className="bg-white rounded-lg shadow-md border border-slate-200 mb-6">
          <div className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold text-slate-800">
                Script'ler ({filteredScripts.length})
              </h3>
              <button
                onClick={() => console.log('Log görüntüleme özelliği geliştirilecek')}
                className="bg-slate-100 text-slate-700 px-3 py-2 rounded-md hover:bg-slate-200 text-sm"
              >
                Log Görüntüle
              </button>
            </div>

            {filteredScripts.length === 0 ? (
              <div className="text-center py-12">
                <p className="text-slate-500">Arama kriterlerine uygun script bulunamadı</p>
              </div>
            ) : (
              <div className="space-y-4">
                {filteredScripts.map((script) => (
                  <div
                    key={script.id}
                    className="border border-slate-200 rounded-lg p-4 hover:border-slate-300 transition-colors"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center space-x-3 mb-2">
                          <h4 className="text-lg font-semibold text-slate-800">{script.name}</h4>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(script.status)}`}>
                            {getStatusText(script.status)}
                          </span>
                          <span className={`px-2 py-1 rounded text-xs font-medium ${getCategoryColor(script.category)}`}>
                            {script.category}
                          </span>
                        </div>
                        
                        <p className="text-slate-600 mb-3">{script.description}</p>
                        
                        <div className="flex items-center space-x-6 text-sm text-slate-500">
                          <span>Son Çalışma: {script.lastRun}</span>
                          <span>Boyut: {script.fileSize}</span>
                          <span>Bağımlılıklar: {script.dependencies.join(', ')}</span>
                        </div>
                      </div>

                      <div className="flex space-x-2 ml-4">
                        <button
                          onClick={() => runScript(script.id)}
                          disabled={script.status === 'active'}
                          className="bg-green-600 text-white px-3 py-2 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                        >
                          Çalıştır
                        </button>
                        <button
                          onClick={() => editScript(script.id)}
                          className="bg-blue-600 text-white px-3 py-2 rounded-md hover:bg-blue-700 text-sm"
                        >
                          Düzenle
                        </button>
                        <button
                          onClick={() => deleteScript(script.id)}
                          className="bg-red-600 text-white px-3 py-2 rounded-md hover:bg-red-700 text-sm"
                        >
                          Sil
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Yeni Script Ekleme Formu */}
        {showAddForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
              <h3 className="text-lg font-semibold text-slate-800 mb-4">Yeni Script Ekle</h3>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Script Adı</label>
                  <input
                    type="text"
                    value={newScript.name}
                    onChange={(e) => setNewScript(prev => ({ ...prev, name: e.target.value }))}
                    className="w-full p-3 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="script_name.py"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Açıklama</label>
                  <textarea
                    value={newScript.description}
                    onChange={(e) => setNewScript(prev => ({ ...prev, description: e.target.value }))}
                    className="w-full p-3 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    rows={3}
                    placeholder="Script'in ne yaptığını açıklayın..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Kategori</label>
                  <select
                    value={newScript.category}
                    onChange={(e) => setNewScript(prev => ({ ...prev, category: e.target.value as any }))}
                    className="w-full p-3 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="AI/ML">AI/ML</option>
                    <option value="Veri İşleme">Veri İşleme</option>
                    <option value="Rapor Üretimi">Rapor Üretimi</option>
                    <option value="Sistem Yönetimi">Sistem Yönetimi</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Dosya Boyutu</label>
                  <input
                    type="text"
                    value={newScript.fileSize}
                    onChange={(e) => setNewScript(prev => ({ ...prev, fileSize: e.target.value }))}
                    className="w-full p-3 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="45.2 KB"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-2">Bağımlılıklar</label>
                  <input
                    type="text"
                    value={newScript.dependencies.join(', ')}
                    onChange={(e) => setNewScript(prev => ({ ...prev, dependencies: e.target.value.split(',').map(s => s.trim()) }))}
                    className="w-full p-3 border border-slate-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="numpy, pandas, matplotlib"
                  />
                </div>
              </div>

              <div className="flex space-x-3 mt-6">
                <button
                  onClick={addScript}
                  className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700"
                >
                  Ekle
                </button>
                <button
                  onClick={() => setShowAddForm(false)}
                  className="flex-1 bg-slate-100 text-slate-700 py-2 px-4 rounded-md hover:bg-slate-200"
                >
                  İptal
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ScriptManagement;















