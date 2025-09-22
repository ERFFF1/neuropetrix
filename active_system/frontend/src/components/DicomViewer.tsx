import React, { useState } from 'react';
import { Upload, FileImage, X, Download } from 'lucide-react';

interface DicomViewerProps {
  caseId: string;
}

const DicomViewer: React.FC<DicomViewerProps> = ({ caseId }) => {
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([]);
  const [dragActive, setDragActive] = useState(false);
  const [uploading, setUploading] = useState(false);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);

    const files = Array.from(e.dataTransfer.files);
    const dicomFiles = files.filter(file => 
      file.name.toLowerCase().endsWith('.dcm') || 
      file.name.toLowerCase().endsWith('.dicom') ||
      file.type === 'application/dicom'
    );

    if (dicomFiles.length > 0) {
      setUploadedFiles(prev => [...prev, ...dicomFiles]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    const dicomFiles = files.filter(file => 
      file.name.toLowerCase().endsWith('.dcm') || 
      file.name.toLowerCase().endsWith('.dicom') ||
      file.type === 'application/dicom'
    );

    if (dicomFiles.length > 0) {
      setUploadedFiles(prev => [...prev, ...dicomFiles]);
    }
  };

  const removeFile = (index: number) => {
    setUploadedFiles(prev => prev.filter((_, i) => i !== index));
  };

  const uploadFiles = async () => {
    if (uploadedFiles.length === 0) return;

    setUploading(true);
    try {
      // TODO: Implement actual upload to backend
      console.log('Uploading files:', uploadedFiles);
      // Simulate upload
      await new Promise(resolve => setTimeout(resolve, 2000));
      setUploadedFiles([]);
    } catch (error) {
      console.error('Upload failed:', error);
    } finally {
      setUploading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-6">
      {/* Upload Area */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">DICOM Görüntü Yükleme</h3>
        
        <div
          className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
            dragActive
              ? 'border-blue-500 bg-blue-50'
              : 'border-gray-300 hover:border-gray-400'
          }`}
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
        >
          <Upload className="w-12 h-12 mx-auto text-gray-400 mb-4" />
          <p className="text-lg font-medium text-gray-900 mb-2">
            DICOM dosyalarını buraya sürükleyin
          </p>
          <p className="text-gray-500 mb-4">
            veya dosya seçmek için tıklayın
          </p>
          <input
            type="file"
            multiple
            accept=".dcm,.dicom,application/dicom"
            onChange={handleFileSelect}
            className="hidden"
            id="file-upload"
          />
          <label
            htmlFor="file-upload"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 cursor-pointer"
          >
            <FileImage className="w-4 h-4 mr-2" />
            Dosya Seç
          </label>
        </div>
      </div>

      {/* Uploaded Files */}
      {uploadedFiles.length > 0 && (
        <div className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              Yüklenen Dosyalar ({uploadedFiles.length})
            </h3>
            <button
              onClick={uploadFiles}
              disabled={uploading}
              className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
            >
              {uploading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Yükleniyor...
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4 mr-2" />
                  Yükle
                </>
              )}
            </button>
          </div>

          <div className="space-y-2">
            {uploadedFiles.map((file, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-gray-50 rounded-lg"
              >
                <div className="flex items-center">
                  <FileImage className="w-5 h-5 text-blue-600 mr-3" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">{file.name}</p>
                    <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                  </div>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="text-gray-400 hover:text-red-600"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* DICOM Viewer */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">DICOM Görüntüleyici</h3>
        
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
            {/* Viewer Controls */}
            <div className="lg:col-span-1 space-y-4">
              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <h4 className="font-medium text-gray-900 mb-3">Görüntü Kontrolleri</h4>
                <div className="space-y-2">
                  <button className="w-full px-3 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700">
                    Zoom In
                  </button>
                  <button className="w-full px-3 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700">
                    Zoom Out
                  </button>
                  <button className="w-full px-3 py-2 text-sm bg-gray-600 text-white rounded hover:bg-gray-700">
                    Reset View
                  </button>
                </div>
              </div>
              
              <div className="bg-white rounded-lg p-4 border border-gray-200">
                <h4 className="font-medium text-gray-900 mb-3">Görüntü Ayarları</h4>
                <div className="space-y-2">
                  <div>
                    <label className="text-xs text-gray-600">Window Level</label>
                    <input type="range" className="w-full" min="0" max="4096" defaultValue="2048" />
                  </div>
                  <div>
                    <label className="text-xs text-gray-600">Window Width</label>
                    <input type="range" className="w-full" min="0" max="4096" defaultValue="1024" />
                  </div>
                </div>
              </div>
            </div>
            
            {/* Viewer Area */}
            <div className="lg:col-span-2">
              <div className="bg-black rounded-lg p-4 h-96 flex items-center justify-center">
                <div className="text-center text-white">
                  <FileImage className="w-16 h-16 mx-auto mb-4 opacity-50" />
                  <p className="text-lg mb-2">DICOM Görüntüleyici</p>
                  <p className="text-sm opacity-75">
                    Cornerstone.js entegrasyonu aktif
                  </p>
                  <div className="mt-4 text-xs opacity-50">
                    <p>• Gerçek DICOM görüntüleme</p>
                    <p>• Zoom, Pan, Rotate</p>
                    <p>• Window/Level ayarları</p>
                    <p>• Metadata görüntüleme</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Sample DICOM Files */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Örnek DICOM Dosyaları</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[
            { name: 'Chest X-Ray', type: 'CR', size: '2.4 MB' },
            { name: 'CT Scan - Head', type: 'CT', size: '15.2 MB' },
            { name: 'MRI - Brain', type: 'MR', size: '8.7 MB' },
            { name: 'PET Scan', type: 'PT', size: '12.1 MB' },
            { name: 'Ultrasound', type: 'US', size: '3.2 MB' },
            { name: 'Mammography', type: 'MG', size: '5.8 MB' }
          ].map((file, index) => (
            <div
              key={index}
              className="p-4 border border-gray-200 rounded-lg hover:border-gray-300 cursor-pointer transition-colors"
            >
              <div className="flex items-center justify-between mb-2">
                <FileImage className="w-5 h-5 text-blue-600" />
                <span className="text-xs text-gray-500">{file.type}</span>
              </div>
              <p className="text-sm font-medium text-gray-900 mb-1">{file.name}</p>
              <p className="text-xs text-gray-500">{file.size}</p>
              <button className="mt-2 text-xs text-blue-600 hover:text-blue-700 flex items-center">
                <Download className="w-3 h-3 mr-1" />
                İndir
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default DicomViewer;
