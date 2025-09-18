import React, { useState } from 'react';
import { PatientData } from '../types';

interface PatientDataFormProps {
  onSubmit: (patientData: PatientData) => void;
  onCancel: () => void;
}

const PatientDataForm: React.FC<PatientDataFormProps> = ({ onSubmit, onCancel }) => {
  const [formData, setFormData] = useState<PatientData>({
    age: 0,
    gender: 'male',
    chiefComplaint: '',
    medicalHistory: '',
    currentMedications: '',
    vitals: {
      bloodPressure: '',
      heartRate: 0,
      temperature: 0,
      respiratoryRate: 0,
      oxygenSaturation: 0
    },
    additionalNotes: ''
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};

    if (!formData.chiefComplaint.trim()) {
      newErrors.chiefComplaint = 'Başvuru şikayeti gereklidir';
    }

    if (formData.age < 0 || formData.age > 150) {
      newErrors.age = 'Yaş 0-150 arasında olmalıdır';
    }

    if (formData.vitals.heartRate < 0 || formData.vitals.heartRate > 300) {
      newErrors.heartRate = 'Kalp hızı 0-300 arasında olmalıdır';
    }

    if (formData.vitals.temperature < 30 || formData.vitals.temperature > 45) {
      newErrors.temperature = 'Vücut sıcaklığı 30-45°C arasında olmalıdır';
    }

    if (formData.vitals.respiratoryRate < 0 || formData.vitals.respiratoryRate > 60) {
      newErrors.respiratoryRate = 'Solunum hızı 0-60 arasında olmalıdır';
    }

    if (formData.vitals.oxygenSaturation < 0 || formData.vitals.oxygenSaturation > 100) {
      newErrors.oxygenSaturation = 'Oksijen saturasyonu 0-100% arasında olmalıdır';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      onSubmit(formData);
    }
  };

  const handleInputChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  const handleVitalsChange = (field: string, value: any) => {
    setFormData(prev => ({
      ...prev,
      vitals: {
        ...prev.vitals,
        [field]: value
      }
    }));
    
    // Clear error when user starts typing
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }));
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Basic Info */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Yaş *
          </label>
          <input
            type="number"
            value={formData.age}
            onChange={(e) => handleInputChange('age', parseInt(e.target.value) || 0)}
            className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
              errors.age ? 'border-red-500' : 'border-gray-300'
            }`}
            placeholder="Yaş"
          />
          {errors.age && <p className="text-red-500 text-xs mt-1">{errors.age}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Cinsiyet *
          </label>
          <select
            value={formData.gender}
            onChange={(e) => handleInputChange('gender', e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="male">Erkek</option>
            <option value="female">Kadın</option>
            <option value="other">Diğer</option>
          </select>
        </div>
      </div>

      {/* Chief Complaint */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Başvuru Şikayeti *
        </label>
        <textarea
          value={formData.chiefComplaint}
          onChange={(e) => handleInputChange('chiefComplaint', e.target.value)}
          className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
            errors.chiefComplaint ? 'border-red-500' : 'border-gray-300'
          }`}
          rows={3}
          placeholder="Hastanın başvuru şikayeti..."
        />
        {errors.chiefComplaint && <p className="text-red-500 text-xs mt-1">{errors.chiefComplaint}</p>}
      </div>

      {/* Medical History */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Tıbbi Geçmiş
        </label>
        <textarea
          value={formData.medicalHistory}
          onChange={(e) => handleInputChange('medicalHistory', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows={3}
          placeholder="Önceki hastalıklar, ameliyatlar, alerjiler..."
        />
      </div>

      {/* Current Medications */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Mevcut İlaçlar
        </label>
        <textarea
          value={formData.currentMedications}
          onChange={(e) => handleInputChange('currentMedications', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows={2}
          placeholder="Kullandığı ilaçlar..."
        />
      </div>

      {/* Vitals */}
      <div>
        <h3 className="text-lg font-medium text-gray-900 mb-3">Vital Bulgular</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Kan Basıncı
            </label>
            <input
              type="text"
              value={formData.vitals.bloodPressure}
              onChange={(e) => handleVitalsChange('bloodPressure', e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="120/80"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Kalp Hızı (bpm)
            </label>
            <input
              type="number"
              value={formData.vitals.heartRate}
              onChange={(e) => handleVitalsChange('heartRate', parseInt(e.target.value) || 0)}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.heartRate ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="72"
            />
            {errors.heartRate && <p className="text-red-500 text-xs mt-1">{errors.heartRate}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Vücut Sıcaklığı (°C)
            </label>
            <input
              type="number"
              step="0.1"
              value={formData.vitals.temperature}
              onChange={(e) => handleVitalsChange('temperature', parseFloat(e.target.value) || 0)}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.temperature ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="36.5"
            />
            {errors.temperature && <p className="text-red-500 text-xs mt-1">{errors.temperature}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Solunum Hızı (/dk)
            </label>
            <input
              type="number"
              value={formData.vitals.respiratoryRate}
              onChange={(e) => handleVitalsChange('respiratoryRate', parseInt(e.target.value) || 0)}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.respiratoryRate ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="16"
            />
            {errors.respiratoryRate && <p className="text-red-500 text-xs mt-1">{errors.respiratoryRate}</p>}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Oksijen Saturasyonu (%)
            </label>
            <input
              type="number"
              value={formData.vitals.oxygenSaturation}
              onChange={(e) => handleVitalsChange('oxygenSaturation', parseInt(e.target.value) || 0)}
              className={`w-full px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 ${
                errors.oxygenSaturation ? 'border-red-500' : 'border-gray-300'
              }`}
              placeholder="98"
            />
            {errors.oxygenSaturation && <p className="text-red-500 text-xs mt-1">{errors.oxygenSaturation}</p>}
          </div>
        </div>
      </div>

      {/* Additional Notes */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Ek Notlar
        </label>
        <textarea
          value={formData.additionalNotes}
          onChange={(e) => handleInputChange('additionalNotes', e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows={3}
          placeholder="Ek bilgiler, gözlemler..."
        />
      </div>

      {/* Buttons */}
      <div className="flex justify-end space-x-3 pt-4 border-t border-gray-200">
        <button
          type="button"
          onClick={onCancel}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          İptal
        </button>
        <button
          type="submit"
          className="px-4 py-2 text-sm font-medium text-white bg-blue-600 border border-transparent rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Vaka Oluştur
        </button>
      </div>
    </form>
  );
};

export default PatientDataForm;
