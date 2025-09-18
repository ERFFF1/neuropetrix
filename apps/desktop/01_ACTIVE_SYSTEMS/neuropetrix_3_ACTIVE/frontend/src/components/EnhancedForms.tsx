import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Checkbox } from '@/components/ui/checkbox';
import { RadioGroup, RadioGroupItem } from '@/components/ui/radio-group';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Badge } from '@/components/ui/badge';
import { 
  User, 
  Calendar, 
  FileText, 
  Upload, 
  Save, 
  Send, 
  Eye, 
  Edit,
  Trash2,
  Plus,
  Search,
  Filter,
  Download
} from 'lucide-react';

interface PatientFormData {
  id: string;
  firstName: string;
  lastName: string;
  dateOfBirth: string;
  gender: 'male' | 'female' | 'other';
  phone: string;
  email: string;
  address: string;
  medicalHistory: string;
  allergies: string[];
  emergencyContact: {
    name: string;
    phone: string;
    relationship: string;
  };
}

interface ReportFormData {
  id: string;
  patientId: string;
  reportType: 'pet-ct' | 'pet-mri' | 'spect' | 'other';
  studyDate: string;
  findings: string;
  impression: string;
  recommendations: string;
  attachments: File[];
}

const EnhancedForms: React.FC = () => {
  const [activeTab, setActiveTab] = useState('patient');
  const [patientForm, setPatientForm] = useState<PatientFormData>({
    id: '',
    firstName: '',
    lastName: '',
    dateOfBirth: '',
    gender: 'male',
    phone: '',
    email: '',
    address: '',
    medicalHistory: '',
    allergies: [],
    emergencyContact: {
      name: '',
      phone: '',
      relationship: ''
    }
  });

  const [reportForm, setReportForm] = useState<ReportFormData>({
    id: '',
    patientId: '',
    reportType: 'pet-ct',
    studyDate: '',
    findings: '',
    impression: '',
    recommendations: '',
    attachments: []
  });

  const [formErrors, setFormErrors] = useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const validatePatientForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!patientForm.firstName.trim()) {
      errors.firstName = 'Ad gereklidir';
    }
    if (!patientForm.lastName.trim()) {
      errors.lastName = 'Soyad gereklidir';
    }
    if (!patientForm.dateOfBirth) {
      errors.dateOfBirth = 'Doğum tarihi gereklidir';
    }
    if (!patientForm.phone.trim()) {
      errors.phone = 'Telefon numarası gereklidir';
    }
    if (!patientForm.email.trim()) {
      errors.email = 'E-posta adresi gereklidir';
    } else if (!/\S+@\S+\.\S+/.test(patientForm.email)) {
      errors.email = 'Geçerli bir e-posta adresi giriniz';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const validateReportForm = (): boolean => {
    const errors: Record<string, string> = {};

    if (!reportForm.patientId.trim()) {
      errors.patientId = 'Hasta seçimi gereklidir';
    }
    if (!reportForm.studyDate) {
      errors.studyDate = 'Çalışma tarihi gereklidir';
    }
    if (!reportForm.findings.trim()) {
      errors.findings = 'Bulgular gereklidir';
    }
    if (!reportForm.impression.trim()) {
      errors.impression = 'İmpresyon gereklidir';
    }

    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handlePatientSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validatePatientForm()) return;

    setIsSubmitting(true);
    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      console.log('Patient form submitted:', patientForm);
      alert('Hasta kaydı başarıyla oluşturuldu!');
    } catch (error) {
      console.error('Patient form error:', error);
      alert('Hasta kaydı oluşturulurken hata oluştu!');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleReportSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!validateReportForm()) return;

    setIsSubmitting(true);
    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 2000));
      console.log('Report form submitted:', reportForm);
      alert('Rapor başarıyla oluşturuldu!');
    } catch (error) {
      console.error('Report form error:', error);
      alert('Rapor oluşturulurken hata oluştu!');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    setReportForm(prev => ({
      ...prev,
      attachments: [...prev.attachments, ...files]
    }));
  };

  const removeAttachment = (index: number) => {
    setReportForm(prev => ({
      ...prev,
      attachments: prev.attachments.filter((_, i) => i !== index)
    }));
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Gelişmiş Formlar</h1>
          <p className="text-gray-600">Hasta kayıtları ve rapor oluşturma</p>
        </div>
        <div className="flex gap-2">
          <Button variant="outline">
            <Download className="h-4 w-4 mr-2" />
            Şablon İndir
          </Button>
          <Button>
            <Plus className="h-4 w-4 mr-2" />
            Yeni Kayıt
          </Button>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList className="grid w-full grid-cols-2">
          <TabsTrigger value="patient" className="flex items-center gap-2">
            <User className="h-4 w-4" />
            Hasta Kaydı
          </TabsTrigger>
          <TabsTrigger value="report" className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            Rapor Oluştur
          </TabsTrigger>
        </TabsList>

        <TabsContent value="patient" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="h-5 w-5" />
                Yeni Hasta Kaydı
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handlePatientSubmit} className="space-y-6">
                {/* Personal Information */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Kişisel Bilgiler</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="firstName">Ad *</Label>
                      <Input
                        id="firstName"
                        value={patientForm.firstName}
                        onChange={(e) => setPatientForm(prev => ({ ...prev, firstName: e.target.value }))}
                        className={formErrors.firstName ? 'border-red-500' : ''}
                      />
                      {formErrors.firstName && (
                        <p className="text-sm text-red-500">{formErrors.firstName}</p>
                      )}
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="lastName">Soyad *</Label>
                      <Input
                        id="lastName"
                        value={patientForm.lastName}
                        onChange={(e) => setPatientForm(prev => ({ ...prev, lastName: e.target.value }))}
                        className={formErrors.lastName ? 'border-red-500' : ''}
                      />
                      {formErrors.lastName && (
                        <p className="text-sm text-red-500">{formErrors.lastName}</p>
                      )}
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="dateOfBirth">Doğum Tarihi *</Label>
                      <Input
                        id="dateOfBirth"
                        type="date"
                        value={patientForm.dateOfBirth}
                        onChange={(e) => setPatientForm(prev => ({ ...prev, dateOfBirth: e.target.value }))}
                        className={formErrors.dateOfBirth ? 'border-red-500' : ''}
                      />
                      {formErrors.dateOfBirth && (
                        <p className="text-sm text-red-500">{formErrors.dateOfBirth}</p>
                      )}
                    </div>
                    <div className="space-y-2">
                      <Label>Cinsiyet *</Label>
                      <RadioGroup
                        value={patientForm.gender}
                        onValueChange={(value) => setPatientForm(prev => ({ ...prev, gender: value as any }))}
                        className="flex gap-4"
                      >
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="male" id="male" />
                          <Label htmlFor="male">Erkek</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="female" id="female" />
                          <Label htmlFor="female">Kadın</Label>
                        </div>
                        <div className="flex items-center space-x-2">
                          <RadioGroupItem value="other" id="other" />
                          <Label htmlFor="other">Diğer</Label>
                        </div>
                      </RadioGroup>
                    </div>
                  </div>
                </div>

                {/* Contact Information */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">İletişim Bilgileri</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="phone">Telefon *</Label>
                      <Input
                        id="phone"
                        value={patientForm.phone}
                        onChange={(e) => setPatientForm(prev => ({ ...prev, phone: e.target.value }))}
                        className={formErrors.phone ? 'border-red-500' : ''}
                      />
                      {formErrors.phone && (
                        <p className="text-sm text-red-500">{formErrors.phone}</p>
                      )}
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="email">E-posta *</Label>
                      <Input
                        id="email"
                        type="email"
                        value={patientForm.email}
                        onChange={(e) => setPatientForm(prev => ({ ...prev, email: e.target.value }))}
                        className={formErrors.email ? 'border-red-500' : ''}
                      />
                      {formErrors.email && (
                        <p className="text-sm text-red-500">{formErrors.email}</p>
                      )}
                    </div>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="address">Adres</Label>
                    <Textarea
                      id="address"
                      value={patientForm.address}
                      onChange={(e) => setPatientForm(prev => ({ ...prev, address: e.target.value }))}
                      rows={3}
                    />
                  </div>
                </div>

                {/* Medical Information */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Tıbbi Bilgiler</h3>
                  <div className="space-y-2">
                    <Label htmlFor="medicalHistory">Tıbbi Geçmiş</Label>
                    <Textarea
                      id="medicalHistory"
                      value={patientForm.medicalHistory}
                      onChange={(e) => setPatientForm(prev => ({ ...prev, medicalHistory: e.target.value }))}
                      rows={4}
                      placeholder="Hastalıklar, ameliyatlar, kullanılan ilaçlar..."
                    />
                  </div>
                  <div className="space-y-2">
                    <Label>Bilinen Alerjiler</Label>
                    <div className="flex flex-wrap gap-2">
                      {patientForm.allergies.map((allergy, index) => (
                        <Badge key={index} variant="secondary" className="flex items-center gap-1">
                          {allergy}
                          <button
                            type="button"
                            onClick={() => setPatientForm(prev => ({
                              ...prev,
                              allergies: prev.allergies.filter((_, i) => i !== index)
                            }))}
                            className="ml-1 hover:text-red-500"
                          >
                            ×
                          </button>
                        </Badge>
                      ))}
                      <Input
                        placeholder="Alerji ekle..."
                        onKeyPress={(e) => {
                          if (e.key === 'Enter') {
                            e.preventDefault();
                            const input = e.target as HTMLInputElement;
                            if (input.value.trim()) {
                              setPatientForm(prev => ({
                                ...prev,
                                allergies: [...prev.allergies, input.value.trim()]
                              }));
                              input.value = '';
                            }
                          }
                        }}
                        className="w-32"
                      />
                    </div>
                  </div>
                </div>

                {/* Emergency Contact */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Acil Durum İletişim</h3>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="emergencyName">Ad Soyad</Label>
                      <Input
                        id="emergencyName"
                        value={patientForm.emergencyContact.name}
                        onChange={(e) => setPatientForm(prev => ({
                          ...prev,
                          emergencyContact: { ...prev.emergencyContact, name: e.target.value }
                        }))}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="emergencyPhone">Telefon</Label>
                      <Input
                        id="emergencyPhone"
                        value={patientForm.emergencyContact.phone}
                        onChange={(e) => setPatientForm(prev => ({
                          ...prev,
                          emergencyContact: { ...prev.emergencyContact, phone: e.target.value }
                        }))}
                      />
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="emergencyRelationship">Yakınlık</Label>
                      <Input
                        id="emergencyRelationship"
                        value={patientForm.emergencyContact.relationship}
                        onChange={(e) => setPatientForm(prev => ({
                          ...prev,
                          emergencyContact: { ...prev.emergencyContact, relationship: e.target.value }
                        }))}
                        placeholder="Eş, Anne, Baba, vb."
                      />
                    </div>
                  </div>
                </div>

                {/* Form Actions */}
                <div className="flex justify-end gap-2 pt-4 border-t">
                  <Button type="button" variant="outline">
                    <Eye className="h-4 w-4 mr-2" />
                    Önizleme
                  </Button>
                  <Button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Kaydediliyor...
                      </>
                    ) : (
                      <>
                        <Save className="h-4 w-4 mr-2" />
                        Kaydet
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="report" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <FileText className="h-5 w-5" />
                Yeni Rapor Oluştur
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleReportSubmit} className="space-y-6">
                {/* Report Information */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Rapor Bilgileri</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="patientId">Hasta *</Label>
                      <Select
                        value={reportForm.patientId}
                        onValueChange={(value) => setReportForm(prev => ({ ...prev, patientId: value }))}
                      >
                        <SelectTrigger className={formErrors.patientId ? 'border-red-500' : ''}>
                          <SelectValue placeholder="Hasta seçiniz" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="1">Ahmet Yılmaz (ID: 001)</SelectItem>
                          <SelectItem value="2">Ayşe Demir (ID: 002)</SelectItem>
                          <SelectItem value="3">Mehmet Kaya (ID: 003)</SelectItem>
                        </SelectContent>
                      </Select>
                      {formErrors.patientId && (
                        <p className="text-sm text-red-500">{formErrors.patientId}</p>
                      )}
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="reportType">Rapor Türü</Label>
                      <Select
                        value={reportForm.reportType}
                        onValueChange={(value) => setReportForm(prev => ({ ...prev, reportType: value as any }))}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="pet-ct">PET/CT</SelectItem>
                          <SelectItem value="pet-mri">PET/MRI</SelectItem>
                          <SelectItem value="spect">SPECT</SelectItem>
                          <SelectItem value="other">Diğer</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="studyDate">Çalışma Tarihi *</Label>
                      <Input
                        id="studyDate"
                        type="date"
                        value={reportForm.studyDate}
                        onChange={(e) => setReportForm(prev => ({ ...prev, studyDate: e.target.value }))}
                        className={formErrors.studyDate ? 'border-red-500' : ''}
                      />
                      {formErrors.studyDate && (
                        <p className="text-sm text-red-500">{formErrors.studyDate}</p>
                      )}
                    </div>
                  </div>
                </div>

                {/* Report Content */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Rapor İçeriği</h3>
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="findings">Bulgular *</Label>
                      <Textarea
                        id="findings"
                        value={reportForm.findings}
                        onChange={(e) => setReportForm(prev => ({ ...prev, findings: e.target.value }))}
                        rows={6}
                        className={formErrors.findings ? 'border-red-500' : ''}
                        placeholder="Detaylı bulguları buraya yazınız..."
                      />
                      {formErrors.findings && (
                        <p className="text-sm text-red-500">{formErrors.findings}</p>
                      )}
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="impression">İmpresyon *</Label>
                      <Textarea
                        id="impression"
                        value={reportForm.impression}
                        onChange={(e) => setReportForm(prev => ({ ...prev, impression: e.target.value }))}
                        rows={4}
                        className={formErrors.impression ? 'border-red-500' : ''}
                        placeholder="İmpresyon ve değerlendirme..."
                      />
                      {formErrors.impression && (
                        <p className="text-sm text-red-500">{formErrors.impression}</p>
                      )}
                    </div>
                    <div className="space-y-2">
                      <Label htmlFor="recommendations">Öneriler</Label>
                      <Textarea
                        id="recommendations"
                        value={reportForm.recommendations}
                        onChange={(e) => setReportForm(prev => ({ ...prev, recommendations: e.target.value }))}
                        rows={3}
                        placeholder="Öneriler ve takip planı..."
                      />
                    </div>
                  </div>
                </div>

                {/* File Attachments */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold">Ek Dosyalar</h3>
                  <div className="space-y-4">
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                      <Upload className="h-8 w-8 mx-auto text-gray-400 mb-2" />
                      <p className="text-sm text-gray-600 mb-2">Dosyaları buraya sürükleyin veya seçin</p>
                      <Input
                        type="file"
                        multiple
                        accept=".pdf,.jpg,.jpeg,.png,.dcm"
                        onChange={handleFileUpload}
                        className="max-w-xs mx-auto"
                      />
                    </div>
                    {reportForm.attachments.length > 0 && (
                      <div className="space-y-2">
                        <Label>Eklenen Dosyalar</Label>
                        <div className="space-y-2">
                          {reportForm.attachments.map((file, index) => (
                            <div key={index} className="flex items-center justify-between p-2 border rounded">
                              <div className="flex items-center gap-2">
                                <FileText className="h-4 w-4" />
                                <span className="text-sm">{file.name}</span>
                                <Badge variant="outline">
                                  {(file.size / 1024 / 1024).toFixed(2)} MB
                                </Badge>
                              </div>
                              <Button
                                type="button"
                                variant="outline"
                                size="sm"
                                onClick={() => removeAttachment(index)}
                              >
                                <Trash2 className="h-4 w-4" />
                              </Button>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Form Actions */}
                <div className="flex justify-end gap-2 pt-4 border-t">
                  <Button type="button" variant="outline">
                    <Eye className="h-4 w-4 mr-2" />
                    Önizleme
                  </Button>
                  <Button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                        Oluşturuluyor...
                      </>
                    ) : (
                      <>
                        <Send className="h-4 w-4 mr-2" />
                        Rapor Oluştur
                      </>
                    )}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default EnhancedForms;
