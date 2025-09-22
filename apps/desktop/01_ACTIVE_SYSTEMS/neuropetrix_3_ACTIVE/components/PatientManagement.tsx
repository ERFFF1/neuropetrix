import React, { useState, useEffect } from 'react';

interface Patient {
  id: string;
  name: string;
  age: number;
  gender: string;
  diagnosis: string;
  icd_codes: string[];
  medications: string[];
  comorbidities: string[];
  clinical_goals: string[];
  created_at: string;
}

interface PatientCase {
  id: string;
  patient_id: string;
  case_type: string;
  clinical_context: string;
  imaging_data?: any;
  lab_data?: any;
  notes?: string;
  created_at: string;
}

interface PatientManagementProps {
  onPatientSelect: (patient: Patient) => void;
  onCaseSelect: (caseData: PatientCase) => void;
}

export default function PatientManagement({ onPatientSelect, onCaseSelect }: PatientManagementProps) {
  const [patients, setPatients] = useState<Patient[]>([]);
  const [selectedPatient, setSelectedPatient] = useState<Patient | null>(null);
  const [patientCases, setPatientCases] = useState<PatientCase[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'patients' | 'cases'>('patients');

  // Yeni hasta formu
  const [newPatient, setNewPatient] = useState({
    name: '',
    age: '',
    gender: '',
    diagnosis: '',
    icd_codes: '',
    medications: '',
    comorbidities: '',
    clinical_goals: ''
  });

  // Yeni vaka formu
  const [newCase, setNewCase] = useState({
    case_type: 'initial',
    clinical_context: '',
    notes: ''
  });

  useEffect(() => {
    loadPatients();
  }, []);

  const loadPatients = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/patients');
      if (response.ok) {
        const data = await response.json();
        setPatients(data);
      }
    } catch (error) {
      console.error('Hasta listesi yükleme hatası:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const loadPatientCases = async (patientId: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`/api/patients/${patientId}/cases`);
      if (response.ok) {
        const data = await response.json();
        setPatientCases(data);
      }
    } catch (error) {
      console.error('Vaka listesi yükleme hatası:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const createPatient = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await fetch('/api/patients', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: newPatient.name,
          age: parseInt(newPatient.age),
          gender: newPatient.gender,
          diagnosis: newPatient.diagnosis,
          icd_codes: newPatient.icd_codes.split(',').map(code => code.trim()),
          medications: newPatient.medications.split(',').map(med => med.trim()),
          comorbidities: newPatient.comorbidities.split(',').map(com => com.trim()),
          clinical_goals: newPatient.clinical_goals.split(',').map(goal => goal.trim())
        })
      });

      if (response.ok) {
        setNewPatient({
          name: '', age: '', gender: '', diagnosis: '',
          icd_codes: '', medications: '', comorbidities: '', clinical_goals: ''
        });
        loadPatients();
      }
    } catch (error) {
      console.error('Hasta oluşturma hatası:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const createCase = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedPatient) return;

    setIsLoading(true);
    try {
      const response = await fetch(`/api/patients/${selectedPatient.id}/cases`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          patient_id: selectedPatient.id,
          case_type: newCase.case_type,
          clinical_context: newCase.clinical_context,
          notes: newCase.notes
        })
      });

      if (response.ok) {
        setNewCase({ case_type: 'initial', clinical_context: '', notes: '' });
        loadPatientCases(selectedPatient.id);
      }
    } catch (error) {
      console.error('Vaka oluşturma hatası:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePatientSelect = (patient: Patient) => {
    setSelectedPatient(patient);
    onPatientSelect(patient);
    loadPatientCases(patient.id);
    setActiveTab('cases');
  };

  const handleCaseSelect = (caseData: PatientCase) => {
    onCaseSelect(caseData);
  };

  return (
    <div className="min-h-screen bg-medical-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-medical-900 mb-2">Hasta Yönetimi</h1>
          <p className="text-medical-600">Hasta kayıtları ve vaka yönetimi</p>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-white rounded-lg p-1 mb-6 shadow-sm">
          <button
            onClick={() => setActiveTab('patients')}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'patients'
                ? 'bg-medical-500 text-white'
                : 'text-medical-600 hover:text-medical-800'
            }`}
          >
            Hastalar
          </button>
          <button
            onClick={() => setActiveTab('cases')}
            disabled={!selectedPatient}
            className={`flex-1 py-2 px-4 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'cases'
                ? 'bg-medical-500 text-white'
                : selectedPatient
                ? 'text-medical-600 hover:text-medical-800'
                : 'text-gray-400 cursor-not-allowed'
            }`}
          >
            Vakalar
          </button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Sol Panel - Liste */}
          <div className="lg:col-span-2">
            {activeTab === 'patients' ? (
              <div className="bg-white rounded-lg shadow-sm border border-medical-200">
                <div className="p-6 border-b border-medical-200">
                  <h2 className="text-xl font-semibold text-medical-900">Hasta Listesi</h2>
                </div>
                
                {isLoading ? (
                  <div className="p-6 text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-medical-500 mx-auto"></div>
                  </div>
                ) : (
                  <div className="divide-y divide-medical-200">
                    {patients.map((patient) => (
                      <div
                        key={patient.id}
                        onClick={() => handlePatientSelect(patient)}
                        className="p-4 hover:bg-medical-50 cursor-pointer transition-colors"
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <h3 className="font-medium text-medical-900">{patient.name}</h3>
                            <p className="text-sm text-medical-600">
                              {patient.age} yaş, {patient.gender} • {patient.diagnosis}
                            </p>
                            <p className="text-xs text-medical-500 mt-1">
                              {new Date(patient.created_at).toLocaleDateString('tr-TR')}
                            </p>
                          </div>
                          <div className="text-right">
                            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-medical-100 text-medical-800">
                              {patient.icd_codes.length} ICD
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm border border-medical-200">
                <div className="p-6 border-b border-medical-200">
                  <h2 className="text-xl font-semibold text-medical-900">
                    {selectedPatient?.name} - Vakalar
                  </h2>
                </div>
                
                {isLoading ? (
                  <div className="p-6 text-center">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-medical-500 mx-auto"></div>
                  </div>
                ) : (
                  <div className="divide-y divide-medical-200">
                    {patientCases.map((caseData) => (
                      <div
                        key={caseData.id}
                        onClick={() => handleCaseSelect(caseData)}
                        className="p-4 hover:bg-medical-50 cursor-pointer transition-colors"
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <h3 className="font-medium text-medical-900">
                              {caseData.case_type === 'initial' ? 'İlk Değerlendirme' :
                               caseData.case_type === 'followup' ? 'Takip' : 'Karşılaştırma'}
                            </h3>
                            <p className="text-sm text-medical-600">{caseData.clinical_context}</p>
                            {caseData.notes && (
                              <p className="text-xs text-medical-500 mt-1">{caseData.notes}</p>
                            )}
                            <p className="text-xs text-medical-500 mt-1">
                              {new Date(caseData.created_at).toLocaleDateString('tr-TR')}
                            </p>
                          </div>
                          <div className="text-right">
                            <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                              caseData.case_type === 'initial' 
                                ? 'bg-blue-100 text-blue-800'
                                : caseData.case_type === 'followup'
                                ? 'bg-green-100 text-green-800'
                                : 'bg-purple-100 text-purple-800'
                            }`}>
                              {caseData.case_type}
                            </span>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Sağ Panel - Form */}
          <div className="space-y-6">
            {activeTab === 'patients' ? (
              <div className="bg-white rounded-lg shadow-sm border border-medical-200 p-6">
                <h3 className="text-lg font-semibold text-medical-900 mb-4">Yeni Hasta Ekle</h3>
                
                <form onSubmit={createPatient} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-medical-700 mb-1">
                      Ad Soyad
                    </label>
                    <input
                      type="text"
                      value={newPatient.name}
                      onChange={(e) => setNewPatient({...newPatient, name: e.target.value})}
                      className="w-full px-3 py-2 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500"
                      required
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-medical-700 mb-1">
                        Yaş
                      </label>
                      <input
                        type="number"
                        value={newPatient.age}
                        onChange={(e) => setNewPatient({...newPatient, age: e.target.value})}
                        className="w-full px-3 py-2 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-medical-700 mb-1">
                        Cinsiyet
                      </label>
                      <select
                        value={newPatient.gender}
                        onChange={(e) => setNewPatient({...newPatient, gender: e.target.value})}
                        className="w-full px-3 py-2 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500"
                        required
                      >
                        <option value="">Seçiniz</option>
                        <option value="Erkek">Erkek</option>
                        <option value="Kadın">Kadın</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-medical-700 mb-1">
                      Tanı
                    </label>
                    <input
                      type="text"
                      value={newPatient.diagnosis}
                      onChange={(e) => setNewPatient({...newPatient, diagnosis: e.target.value})}
                      className="w-full px-3 py-2 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-medical-700 mb-1">
                      ICD Kodları (virgülle ayırın)
                    </label>
                    <input
                      type="text"
                      value={newPatient.icd_codes}
                      onChange={(e) => setNewPatient({...newPatient, icd_codes: e.target.value})}
                      className="w-full px-3 py-2 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500"
                      placeholder="C34.90, C78.00"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-medical-700 mb-1">
                      İlaçlar (virgülle ayırın)
                    </label>
                    <input
                      type="text"
                      value={newPatient.medications}
                      onChange={(e) => setNewPatient({...newPatient, medications: e.target.value})}
                      className="w-full px-3 py-2 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500"
                      placeholder="Cisplatin, Pemetrexed"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-medical-700 mb-1">
                      Komorbiditeler (virgülle ayırın)
                    </label>
                    <input
                      type="text"
                      value={newPatient.comorbidities}
                      onChange={(e) => setNewPatient({...newPatient, comorbidities: e.target.value})}
                      className="w-full px-3 py-2 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500"
                      placeholder="Hipertansiyon, Diyabet"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-medical-700 mb-1">
                      Klinik Hedefler (virgülle ayırın)
                    </label>
                    <input
                      type="text"
                      value={newPatient.clinical_goals}
                      onChange={(e) => setNewPatient({...newPatient, clinical_goals: e.target.value})}
                      className="w-full px-3 py-2 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500"
                      placeholder="Tedavi yanıtı, Progresyon takibi"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full bg-medical-600 text-white py-2 px-4 rounded-md hover:bg-medical-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {isLoading ? 'Ekleniyor...' : 'Hasta Ekle'}
                  </button>
                </form>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow-sm border border-medical-200 p-6">
                <h3 className="text-lg font-semibold text-medical-900 mb-4">Yeni Vaka Ekle</h3>
                
                <form onSubmit={createCase} className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-medical-700 mb-1">
                      Vaka Tipi
                    </label>
                    <select
                      value={newCase.case_type}
                      onChange={(e) => setNewCase({...newCase, case_type: e.target.value})}
                      className="w-full px-3 py-2 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500"
                      required
                    >
                      <option value="initial">İlk Değerlendirme</option>
                      <option value="followup">Takip</option>
                      <option value="comparison">Karşılaştırma</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-medical-700 mb-1">
                      Klinik Bağlam
                    </label>
                    <input
                      type="text"
                      value={newCase.clinical_context}
                      onChange={(e) => setNewCase({...newCase, clinical_context: e.target.value})}
                      className="w-full px-3 py-2 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-medical-700 mb-1">
                      Notlar
                    </label>
                    <textarea
                      value={newCase.notes}
                      onChange={(e) => setNewCase({...newCase, notes: e.target.value})}
                      rows={3}
                      className="w-full px-3 py-2 border border-medical-300 rounded-md focus:outline-none focus:ring-2 focus:ring-medical-500"
                    />
                  </div>

                  <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full bg-medical-600 text-white py-2 px-4 rounded-md hover:bg-medical-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                  >
                    {isLoading ? 'Ekleniyor...' : 'Vaka Ekle'}
                  </button>
                </form>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
