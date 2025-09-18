import React, { useState, useEffect } from 'react';
import { ComplianceData, DataAccessLog, ModificationLog, ExportLog } from '../types';

interface CompliancePanelProps {
  patientCase: any;
}

export default function CompliancePanel({ patientCase }: CompliancePanelProps) {
  const [complianceData, setComplianceData] = useState<ComplianceData | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'privacy' | 'regulatory' | 'audit'>('overview');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    loadComplianceData();
  }, [patientCase.id]);

  const loadComplianceData = async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/compliance/${patientCase.id}`);
      const data = await response.json();
      setComplianceData(data);
    } catch (error) {
      console.error('Uyum verileri yüklenemedi:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const updatePrivacySettings = async (settings: any) => {
    try {
      const response = await fetch(`/api/compliance/privacy/${patientCase.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(settings)
      });

      if (response.ok) {
        await loadComplianceData();
      }
    } catch (error) {
      console.error('Gizlilik ayarları güncellenemedi:', error);
    }
  };

  const exportAuditTrail = async () => {
    try {
      const response = await fetch(`/api/compliance/audit-export/${patientCase.id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `audit-trail-${patientCase.id}-${new Date().toISOString().split('T')[0]}.csv`;
        a.click();
      }
    } catch (error) {
      console.error('Denetim izi dışa aktarılamadı:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2">Uyum verileri yükleniyor...</span>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Başlık */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-slate-800">
            ⚖️ Uyum Paneli
          </h1>
          <p className="text-slate-600 mt-2">
            KVKK, HIPAA, GDPR uyumluluğu ve denetim izi
          </p>
        </div>

        {/* Ana İçerik */}
        <div className="bg-white rounded-lg shadow-md border border-slate-200">
          <div className="border-b border-slate-200">
            <nav className="flex space-x-8 px-6">
              {[
                { key: 'overview', label: 'Genel Bakış', icon: '📊' },
                { key: 'privacy', label: 'Veri Gizliliği', icon: '🔒' },
                { key: 'regulatory', label: 'Regülasyonlar', icon: '⚖️' },
                { key: 'audit', label: 'Denetim İzi', icon: '📋' }
              ].map((tab) => (
                <button
                  key={tab.key}
                  onClick={() => setActiveTab(tab.key as any)}
                  className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm ${
                    activeTab === tab.key
                      ? 'border-blue-500 text-blue-600'
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
            {/* Overview Tab */}
            {activeTab === 'overview' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-slate-800">Uyum Genel Bakışı</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                  <div className="bg-green-50 p-4 rounded-lg border border-green-200">
                    <div className="flex items-center">
                      <div className="text-green-600 text-2xl mr-3">✅</div>
                      <div>
                        <h3 className="font-semibold text-green-800">Veri Gizliliği</h3>
                        <p className="text-sm text-green-600">
                          {complianceData?.dataPrivacy?.anonymizationLevel === 'full' ? 'Tam Anonimleştirme' : 'Kısmi Anonimleştirme'}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-blue-50 p-4 rounded-lg border border-blue-200">
                    <div className="flex items-center">
                      <div className="text-blue-600 text-2xl mr-3">⚖️</div>
                      <div>
                        <h3 className="font-semibold text-blue-800">Regülasyon Uyumu</h3>
                        <p className="text-sm text-blue-600">
                          {Object.values(complianceData?.regulatoryCompliance || {}).filter(Boolean).length}/5 Standart
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="bg-purple-50 p-4 rounded-lg border border-purple-200">
                    <div className="flex items-center">
                      <div className="text-purple-600 text-2xl mr-3">📋</div>
                      <div>
                        <h3 className="font-semibold text-purple-800">Denetim İzi</h3>
                        <p className="text-sm text-purple-600">
                          {complianceData?.auditTrail?.dataAccess?.length || 0} Erişim Kaydı
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-slate-50 p-4 rounded-lg border border-slate-200">
                  <h3 className="font-semibold mb-3 text-slate-800">Hızlı Eylemler</h3>
                  <div className="flex space-x-4">
                    <button
                      onClick={() => setActiveTab('privacy')}
                      className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 text-sm transition-colors duration-200"
                    >
                      Gizlilik Ayarları
                    </button>
                    <button
                      onClick={exportAuditTrail}
                      className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 text-sm transition-colors duration-200"
                    >
                      Denetim İzini Dışa Aktar
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Privacy Tab */}
            {activeTab === 'privacy' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-slate-800">Veri Gizliliği Yönetimi</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-slate-800">Anonimleştirme Seviyesi</h3>
                    <div className="space-y-3">
                      {[
                        { value: 'full', label: 'Tam Anonimleştirme', description: 'Tüm kişisel tanımlayıcılar kaldırılır' },
                        { value: 'partial', label: 'Kısmi Anonimleştirme', description: 'Bazı tanımlayıcılar korunur' },
                        { value: 'none', label: 'Anonimleştirme Yok', description: 'Orijinal veri korunur' }
                      ].map((level) => (
                        <label key={level.value} className="flex items-start space-x-3">
                          <input
                            type="radio"
                            name="anonymizationLevel"
                            value={level.value}
                            checked={complianceData?.dataPrivacy?.anonymizationLevel === level.value}
                            onChange={(e) => updatePrivacySettings({ anonymizationLevel: e.target.value })}
                            className="mt-1"
                          />
                          <div>
                            <div className="font-medium text-slate-700">{level.label}</div>
                            <div className="text-sm text-slate-600">{level.description}</div>
                          </div>
                        </label>
                      ))}
                    </div>
                  </div>

                  <div className="space-y-4">
                    <h3 className="text-lg font-semibold text-slate-800">Güvenlik Ayarları</h3>
                    <div className="space-y-3">
                      <label className="flex items-center space-x-3">
                        <input
                          type="checkbox"
                          checked={complianceData?.dataPrivacy?.maskingApplied || false}
                          onChange={(e) => updatePrivacySettings({ maskingApplied: e.target.checked })}
                          className="rounded"
                        />
                        <span className="text-slate-700">Otomatik Maskeleme Uygula</span>
                      </label>

                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">
                          Şifreleme Seviyesi
                        </label>
                        <select
                          value={complianceData?.dataPrivacy?.encryptionLevel || 'standard'}
                          onChange={(e) => updatePrivacySettings({ encryptionLevel: e.target.value })}
                          className="w-full p-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        >
                          <option value="standard">Standart</option>
                          <option value="high">Yüksek</option>
                          <option value="military">Askeri Seviye</option>
                        </select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-slate-700 mb-2">
                          Veri Saklama Politikası
                        </label>
                        <input
                          type="text"
                          value={complianceData?.dataPrivacy?.retentionPolicy || ''}
                          onChange={(e) => updatePrivacySettings({ retentionPolicy: e.target.value })}
                          placeholder="örn: 7 yıl sonra otomatik silme"
                          className="w-full p-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                        />
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Regulatory Tab */}
            {activeTab === 'regulatory' && (
              <div className="space-y-6">
                <h2 className="text-2xl font-bold text-slate-800">Regülasyon Uyumu</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {[
                    { key: 'kvkk', label: 'KVKK (Türkiye)', description: 'Kişisel Verilerin Korunması Kanunu' },
                    { key: 'hipaa', label: 'HIPAA (ABD)', description: 'Health Insurance Portability and Accountability Act' },
                    { key: 'gdpr', label: 'GDPR (AB)', description: 'General Data Protection Regulation' },
                    { key: 'ceMdr', label: 'CE-MDR (AB)', description: 'Medical Device Regulation' },
                    { key: 'fda510k', label: 'FDA 510(k)', description: 'Food and Drug Administration' }
                  ].map((regulation) => (
                    <div key={regulation.key} className="border border-slate-200 rounded-lg p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="font-semibold text-slate-800">{regulation.label}</h3>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          complianceData?.regulatoryCompliance?.[regulation.key as keyof typeof complianceData.regulatoryCompliance]
                            ? 'bg-green-100 text-green-800'
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {complianceData?.regulatoryCompliance?.[regulation.key as keyof typeof complianceData.regulatoryCompliance] ? 'Uyumlu' : 'Uyumsuz'}
                        </span>
                      </div>
                      <p className="text-sm text-slate-600 mb-3">{regulation.description}</p>
                      <button
                        className="text-blue-600 text-sm hover:text-blue-800 transition-colors duration-200"
                        onClick={() => {/* Compliance details */}}
                      >
                        Detayları Görüntüle →
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Audit Tab */}
            {activeTab === 'audit' && (
              <div className="space-y-6">
                <div className="flex justify-between items-center">
                  <h2 className="text-2xl font-bold text-slate-800">Denetim İzi</h2>
                  <button
                    onClick={exportAuditTrail}
                    className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 transition-colors duration-200"
                  >
                    CSV İndir
                  </button>
                </div>

                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-slate-800">Veri Erişim Kayıtları</h3>
                  <div className="bg-slate-50 rounded-lg p-4 max-h-64 overflow-y-auto border border-slate-200">
                    {complianceData?.auditTrail?.dataAccess?.map((log, index) => (
                      <div key={index} className="border-b border-slate-200 py-2 last:border-b-0">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="font-medium text-slate-800">{log.action}</div>
                            <div className="text-sm text-slate-600">{log.dataType}</div>
                          </div>
                          <div className="text-right">
                            <div className="text-sm text-slate-600">{new Date(log.timestamp).toLocaleString('tr-TR')}</div>
                            <div className="text-xs text-slate-500">{log.userId}</div>
                          </div>
                        </div>
                      </div>
                    )) || (
                      <div className="text-slate-500 text-center py-4">Henüz erişim kaydı yok</div>
                    )}
                  </div>

                  <h3 className="text-lg font-semibold text-slate-800">Değişiklik Kayıtları</h3>
                  <div className="bg-slate-50 rounded-lg p-4 max-h-64 overflow-y-auto border border-slate-200">
                    {complianceData?.auditTrail?.modifications?.map((log, index) => (
                      <div key={index} className="border-b border-slate-200 py-2 last:border-b-0">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="font-medium text-slate-800">{log.field} alanı değiştirildi</div>
                            <div className="text-sm text-slate-600">{log.reason}</div>
                          </div>
                          <div className="text-right">
                            <div className="text-sm text-slate-600">{new Date(log.timestamp).toLocaleString('tr-TR')}</div>
                            <div className="text-xs text-slate-500">{log.userId}</div>
                          </div>
                        </div>
                      </div>
                    )) || (
                      <div className="text-slate-500 text-center py-4">Henüz değişiklik kaydı yok</div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}


