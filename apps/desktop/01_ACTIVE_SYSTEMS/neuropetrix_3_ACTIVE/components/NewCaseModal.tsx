import React, { useState } from 'react';
import { PatientCase, QualityControl, ENTComplaint } from '../types';
import { clinicalRules } from './clinical-rules';

interface NewCaseModalProps {
  onClose: () => void;
  onSave: (newCaseData: Omit<PatientCase, 'id' | 'status'>) => void;
}

const NewCaseModal: React.FC<NewCaseModalProps> = ({ onClose, onSave }) => {
  const [formData, setFormData] = useState({
    name: '',
    age: '',
    gender: 'Male',
    diagnosis: '',
    clinicalTemplate: 'lung' as PatientCase['clinicalTemplate'],
    clinicalNotes: '',
    currentSUVmax: '',
    previousSUVmax: '',
    previousScanDate: '',
    qualityControl: 'PASSED' as QualityControl,
  });

  const [entData, setEntData] = useState<ENTComplaint>({});
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleEntChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
      const { name, value, type } = e.target;
      const checked = (e.target as HTMLInputElement).checked;
      
      const [field, subfield] = name.split('.');

      if (subfield) {
          setEntData(prev => ({
              ...prev,
              [field]: {
                  ...(prev[field as keyof ENTComplaint] as object),
                  [subfield]: type === 'checkbox' ? checked : value
              }
          }));
      } else {
          setEntData(prev => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
      }
  };


  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const previousMeasurements = [];
    if (formData.previousScanDate && formData.previousSUVmax) {
        previousMeasurements.push({
            dateISO: formData.previousScanDate,
            suvMax: parseFloat(formData.previousSUVmax)
        });
    }

    const newCaseData: Omit<PatientCase, 'id' | 'status'> = {
        patientInfo: {
            name: formData.name,
            age: parseInt(formData.age, 10),
            gender: formData.gender as 'Male' | 'Female' | 'Other',
            admissionDate: new Date().toISOString().split('T')[0],
        },
        diagnosis: formData.diagnosis,
        clinicalTemplate: formData.clinicalTemplate,
        clinicalNotes: formData.clinicalNotes,
        previousMeasurements: previousMeasurements,
        currentSUVmax: formData.currentSUVmax ? parseFloat(formData.currentSUVmax) : undefined,
        qualityControl: formData.qualityControl,
        ent: formData.clinicalTemplate === 'ent_sinusitis' ? entData : undefined,
    };
    onSave(newCaseData);
  };

  const renderENTForm = () => (
      <div className="col-span-full border-t border-slate-200 mt-2 pt-6">
          <h4 className="text-base font-semibold leading-6 text-slate-900">ENT - Sinusitis Specifics</h4>
           <div className="mt-4 grid grid-cols-1 gap-x-6 gap-y-6 sm:grid-cols-6">
                <div className="sm:col-span-2">
                    <label className="block text-sm font-medium">Complaint Duration (days)</label>
                    <input type="number" name="durationDays" onChange={handleEntChange} className="mt-1 block w-full rounded-md border-0 py-1.5 ring-1 ring-inset ring-slate-300"/>
                </div>
                <div className="sm:col-span-2">
                    <label className="block text-sm font-medium">Rhinorrhea</label>
                    <select name="rhinorrhea" onChange={handleEntChange} className="mt-1 block w-full rounded-md border-0 py-1.5 ring-1 ring-inset ring-slate-300">
                        <option value="none">None</option>
                        <option value="serous">Serous</option>
                        <option value="mucous">Mucous</option>
                        <option value="purulent">Purulent</option>
                    </select>
                </div>
                 <div className="sm:col-span-2 flex items-end">
                    <div className="flex items-center h-full">
                        <input id="facialPainPressure" type="checkbox" name="facialPainPressure" onChange={handleEntChange} className="h-4 w-4 rounded border-gray-300 text-blue-600"/>
                        <label htmlFor="facialPainPressure" className="ml-2 block text-sm text-slate-900">Facial Pain/Pressure</label>
                    </div>
                </div>
                <div className="col-span-full">
                     <h5 className="text-sm font-semibold">Red Flags</h5>
                     <div className="flex space-x-4 mt-2">
                        <div className="flex items-center">
                           <input id="orbitalSwelling" type="checkbox" name="redFlags.orbitalSwelling" onChange={handleEntChange} className="h-4 w-4 rounded"/>
                           <label htmlFor="orbitalSwelling" className="ml-2 text-sm">Orbital Swelling</label>
                        </div>
                         <div className="flex items-center">
                           <input id="visionChange" type="checkbox" name="redFlags.visionChange" onChange={handleEntChange} className="h-4 w-4 rounded"/>
                           <label htmlFor="visionChange" className="ml-2 text-sm">Vision Change</label>
                        </div>
                         <div className="flex items-center">
                           <input id="severeHeadache" type="checkbox" name="redFlags.severeHeadache" onChange={handleEntChange} className="h-4 w-4 rounded"/>
                           <label htmlFor="severeHeadache" className="ml-2 text-sm">Severe Headache</label>
                        </div>
                     </div>
                </div>
           </div>
      </div>
  );

  return (
    <div className="relative z-20" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>
      <div className="fixed inset-0 z-10 w-screen overflow-y-auto">
        <div className="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
          <div className="relative transform overflow-hidden rounded-lg bg-white text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-2xl">
            <form onSubmit={handleSubmit}>
              <div className="bg-white px-4 pb-4 pt-5 sm:p-6 sm:pb-4">
                <div className="">
                    <h3 className="text-xl font-semibold leading-6 text-slate-900" id="modal-title">Add New Patient Case</h3>
                    <div className="mt-6 grid grid-cols-1 gap-x-6 gap-y-6 sm:grid-cols-6">
                        {/* Patient Info */}
                        <div className="sm:col-span-3">
                            <label htmlFor="name" className="block text-sm font-medium leading-6 text-slate-900">Patient Name</label>
                            <input type="text" name="name" id="name" required value={formData.name} onChange={handleChange} className="mt-2 block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300"/>
                        </div>
                         <div className="sm:col-span-1">
                            <label htmlFor="age" className="block text-sm font-medium leading-6 text-slate-900">Age</label>
                            <input type="number" name="age" id="age" required value={formData.age} onChange={handleChange} className="mt-2 block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300"/>
                        </div>
                         <div className="sm:col-span-2">
                            <label htmlFor="gender" className="block text-sm font-medium leading-6 text-slate-900">Gender</label>
                            <select id="gender" name="gender" value={formData.gender} onChange={handleChange} className="mt-2 block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300">
                                <option>Male</option>
                                <option>Female</option>
                                <option>Other</option>
                            </select>
                        </div>
                        <div className="sm:col-span-3">
                            <label htmlFor="diagnosis" className="block text-sm font-medium leading-6 text-slate-900">Diagnosis</label>
                            <input type="text" name="diagnosis" id="diagnosis" placeholder="e.g., NSCLC Stage III" value={formData.diagnosis} onChange={handleChange} className="mt-2 block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300"/>
                        </div>
                        <div className="sm:col-span-3">
                            <label htmlFor="clinicalTemplate" className="block text-sm font-medium leading-6 text-slate-900">Clinical Template / Disease Type</label>
                            <select id="clinicalTemplate" name="clinicalTemplate" value={formData.clinicalTemplate} onChange={handleChange} className="mt-2 block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300">
                                {Object.entries(clinicalRules.templates).map(([key, value]) => (
                                    <option key={key} value={key}>{value.label}</option>
                                ))}
                            </select>
                        </div>
                         <div className="col-span-full">
                          <label htmlFor="clinicalNotes" className="block text-sm font-medium leading-6 text-slate-900">Clinical Notes</label>
                          <textarea id="clinicalNotes" name="clinicalNotes" rows={3} value={formData.clinicalNotes} onChange={handleChange} className="mt-2 block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300"></textarea>
                        </div>
                        
                        {formData.clinicalTemplate === 'ent_sinusitis' && renderENTForm()}

                        {/* Quantitative Data */}
                        <div className="col-span-full border-t border-slate-200 mt-2 pt-6">
                             <h4 className="text-base font-semibold leading-6 text-slate-900">Quantitative Data (Oncology)</h4>
                             <div className="mt-4 grid grid-cols-1 gap-x-6 gap-y-6 sm:grid-cols-6">
                                <div className="sm:col-span-3">
                                    <label htmlFor="currentSUVmax" className="block text-sm font-medium leading-6 text-slate-900">Current SUVmax</label>
                                    <input type="number" step="0.1" name="currentSUVmax" id="currentSUVmax" value={formData.currentSUVmax} onChange={handleChange} className="mt-2 block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300"/>
                                </div>
                                 <div className="sm:col-span-3">
                                    <label htmlFor="qualityControl" className="block text-sm font-medium leading-6 text-slate-900">Image Quality Control</label>
                                    <select id="qualityControl" name="qualityControl" required value={formData.qualityControl} onChange={handleChange} className="mt-2 block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300">
                                        <option value="PASSED">Passed</option>
                                        <option value="BORDERLINE">Borderline</option>
                                        <option value="FAILED">Failed</option>
                                    </select>
                                </div>
                             </div>
                        </div>

                        {/* Previous Study Data */}
                        <div className="col-span-full border-t border-slate-200 mt-2 pt-6">
                           <h4 className="text-base font-semibold leading-6 text-slate-900">Previous Study Data (for Trend Analysis)</h4>
                           <div className="mt-4 grid grid-cols-1 gap-x-6 gap-y-6 sm:grid-cols-6">
                               <div className="sm:col-span-3">
                                    <label htmlFor="previousSUVmax" className="block text-sm font-medium leading-6 text-slate-900">Previous SUVmax</label>
                                    <input type="number" step="0.1" name="previousSUVmax" id="previousSUVmax" value={formData.previousSUVmax} onChange={handleChange} className="mt-2 block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300"/>
                                </div>
                               <div className="sm:col-span-3">
                                    <label htmlFor="previousScanDate" className="block text-sm font-medium leading-6 text-slate-900">Previous Scan Date</label>
                                    <input type="date" name="previousScanDate" id="previousScanDate" value={formData.previousScanDate} onChange={handleChange} className="mt-2 block w-full rounded-md border-0 py-1.5 text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300"/>
                                </div>
                           </div>
                        </div>
                    </div>
                </div>
              </div>
              <div className="bg-slate-50 px-4 py-3 sm:flex sm:flex-row-reverse sm:px-6">
                <button type="submit" className="inline-flex w-full justify-center rounded-md bg-blue-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-blue-500 sm:ml-3 sm:w-auto">Save Case</button>
                <button type="button" onClick={onClose} className="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-slate-900 shadow-sm ring-1 ring-inset ring-slate-300 hover:bg-slate-50 sm:mt-0 sm:w-auto">Cancel</button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NewCaseModal;
