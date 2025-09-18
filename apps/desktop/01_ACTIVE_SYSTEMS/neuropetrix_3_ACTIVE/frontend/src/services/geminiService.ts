import { GoogleGenerativeAI } from '@google/generative-ai';
import { PatientData, AnalysisResult, ChatMessage } from '../types';

class GeminiService {
  private genAI: GoogleGenerativeAI | null = null;
  private model: any = null;

  constructor() {
    const apiKey = import.meta.env.VITE_GEMINI_API_KEY;
    if (apiKey) {
      this.genAI = new GoogleGenerativeAI(apiKey);
      this.model = this.genAI.getGenerativeModel({ model: 'gemini-2.0-flash-exp' });
    }
  }

  private isAvailable(): boolean {
    return this.genAI !== null && this.model !== null;
  }

  async analyzePatientData(patientData: PatientData): Promise<AnalysisResult> {
    if (!this.isAvailable()) {
      throw new Error('Gemini API key not configured');
    }

    const prompt = `
Sen bir klinik karar destek sistemi AI'sısın. Aşağıdaki hasta verilerini analiz et ve JSON formatında yanıt ver.

Hasta Verileri:
- Yaş: ${patientData.age}
- Cinsiyet: ${patientData.gender}
- Başvuru Şikayeti: ${patientData.chiefComplaint}
- Tıbbi Geçmiş: ${patientData.medicalHistory}
- Mevcut İlaçlar: ${patientData.currentMedications}
- Vital Bulgular:
  - Kan Basıncı: ${patientData.vitals.bloodPressure}
  - Kalp Hızı: ${patientData.vitals.heartRate} bpm
  - Vücut Sıcaklığı: ${patientData.vitals.temperature}°C
  - Solunum Hızı: ${patientData.vitals.respiratoryRate} /dk
  - Oksijen Saturasyonu: ${patientData.vitals.oxygenSaturation}%
- Ek Notlar: ${patientData.additionalNotes || 'Yok'}

Lütfen aşağıdaki JSON formatında yanıt ver:
{
  "summary": "Hastanın genel durumunun kısa özeti",
  "differentialDiagnosis": ["Olası tanı 1", "Olası tanı 2", "Olası tanı 3"],
  "suggestions": ["Öneri 1", "Öneri 2", "Öneri 3"],
  "confidence": 0.85,
  "processingTime": 2.1,
  "modelVersion": "gemini-2.0-flash-exp"
}

Yanıtını sadece JSON formatında ver, başka açıklama ekleme.
    `;

    try {
      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();
      
      // JSON'u parse et
      const analysis = JSON.parse(text);
      
      return {
        summary: analysis.summary || 'Analiz tamamlandı',
        differentialDiagnosis: analysis.differentialDiagnosis || [],
        suggestions: analysis.suggestions || [],
        confidence: analysis.confidence || 0.8,
        processingTime: analysis.processingTime || 2.0,
        modelVersion: analysis.modelVersion || 'gemini-2.0-flash-exp'
      };
    } catch (error) {
      console.error('Gemini analysis error:', error);
      throw new Error('AI analizi sırasında hata oluştu');
    }
  }

  async continueChat(
    caseId: string, 
    message: string, 
    patientData: PatientData, 
    chatHistory: ChatMessage[]
  ): Promise<string> {
    if (!this.isAvailable()) {
      throw new Error('Gemini API key not configured');
    }

    const systemPrompt = `
Sen bir klinik karar destek sistemi AI'sısın. Aşağıdaki hasta verilerini ve sohbet geçmişini kullanarak kullanıcının sorusunu yanıtla.

Hasta Verileri:
- Yaş: ${patientData.age}
- Cinsiyet: ${patientData.gender}
- Başvuru Şikayeti: ${patientData.chiefComplaint}
- Tıbbi Geçmiş: ${patientData.medicalHistory}
- Mevcut İlaçlar: ${patientData.currentMedications}
- Vital Bulgular:
  - Kan Basıncı: ${patientData.vitals.bloodPressure}
  - Kalp Hızı: ${patientData.vitals.heartRate} bpm
  - Vücut Sıcaklığı: ${patientData.vitals.temperature}°C
  - Solunum Hızı: ${patientData.vitals.respiratoryRate} /dk
  - Oksijen Saturasyonu: ${patientData.vitals.oxygenSaturation}%

Sohbet Geçmişi:
${chatHistory.map(msg => `${msg.role}: ${msg.content}`).join('\n')}

Kullanıcı Sorusu: ${message}

Lütfen kısa, net ve klinik olarak doğru bir yanıt ver. Eğer kesin bir tanı koyamıyorsan, olasılıkları belirt ve ek testler öner.
    `;

    try {
      const result = await this.model.generateContent(systemPrompt);
      const response = await result.response;
      return response.text();
    } catch (error) {
      console.error('Gemini chat error:', error);
      throw new Error('Sohbet sırasında hata oluştu');
    }
  }

  async generateFollowUpQuestions(analysis: AnalysisResult): Promise<string[]> {
    if (!this.isAvailable()) {
      return [
        'Hastanın şikayetleri nasıl gelişti?',
        'Ek semptomlar var mı?',
        'İlaç kullanımı nasıl?'
      ];
    }

    const prompt = `
Aşağıdaki AI analiz sonucuna dayanarak, doktorun hastayı daha iyi değerlendirmesi için 3-5 takip sorusu öner:

Analiz Özeti: ${analysis.summary}
Ayırıcı Tanılar: ${analysis.differentialDiagnosis.join(', ')}
Öneriler: ${analysis.suggestions.join(', ')}

Lütfen kısa, net sorular ver. Her satırda bir soru olsun.
    `;

    try {
      const result = await this.model.generateContent(prompt);
      const response = await result.response;
      const text = response.text();
      
      return text.split('\n')
        .map(q => q.trim())
        .filter(q => q.length > 0)
        .slice(0, 5);
    } catch (error) {
      console.error('Gemini follow-up questions error:', error);
      return [
        'Hastanın şikayetleri nasıl gelişti?',
        'Ek semptomlar var mı?',
        'İlaç kullanımı nasıl?'
      ];
    }
  }
}

export const geminiService = new GeminiService();
export default geminiService;
