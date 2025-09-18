// Clinical Criteria Service - PERCIST, Deauville ve diğer klinik kriterler
export interface PERCISTCriteria {
  baselineSUV: number;
  currentSUV: number;
  changePercent: number;
  response: 'CR' | 'PR' | 'SD' | 'PD';
  confidence: number;
  reasoning: string;
  recommendations: string[];
}

export interface DeauvilleCriteria {
  score: 1 | 2 | 3 | 4 | 5;
  description: string;
  interpretation: string;
  recommendations: string[];
}

export interface ResponseAssessment {
  perCIST: PERCISTCriteria;
  deauville?: DeauvilleCriteria;
  overallResponse: 'Complete Response' | 'Partial Response' | 'Stable Disease' | 'Progressive Disease';
  confidence: number;
  nextSteps: string[];
}

class ClinicalCriteriaService {
  private isInitialized: boolean = false;

  async initialize(): Promise<void> {
    try {
      this.isInitialized = true;
      console.log('Clinical Criteria Service initialized successfully');
    } catch (error) {
      console.error('Clinical Criteria Service initialization failed:', error);
      throw error;
    }
  }

  async applyPERCISTCriteria(baselineSUV: number, currentSUV: number): Promise<PERCISTCriteria> {
    if (!this.isInitialized) {
      throw new Error('Clinical Criteria Service not initialized');
    }

    try {
      const changePercent = ((currentSUV - baselineSUV) / baselineSUV) * 100;
      
      let response: 'CR' | 'PR' | 'SD' | 'PD';
      let confidence: number;
      let reasoning: string;
      let recommendations: string[];

      if (currentSUV <= 1.5 && changePercent <= -30) {
        response = 'CR';
        confidence = 0.95;
        reasoning = 'SUV Max ≤ 1.5 ve %30\'dan fazla azalma - Tam yanıt';
        recommendations = [
          'Tedavi başarılı, takip planı yapılmalı',
          '3 ay sonra kontrol PET/CT önerilir',
          'Klinik bulgular ile korelasyon yapılmalı'
        ];
      } else if (changePercent <= -30) {
        response = 'PR';
        confidence = 0.85;
        reasoning = 'SUV Max %30\'dan fazla azalma - Kısmi yanıt';
        recommendations = [
          'Tedavi devam etmeli',
          '6 hafta sonra kontrol önerilir',
          'Yan etkiler değerlendirilmeli'
        ];
      } else if (changePercent >= 30) {
        response = 'PD';
        confidence = 0.90;
        reasoning = 'SUV Max %30\'dan fazla artma - Progresyon';
        recommendations = [
          'Tedavi değişikliği gerekli',
          'Alternatif tedavi seçenekleri değerlendirilmeli',
          'Hasta bilgilendirilmeli'
        ];
      } else {
        response = 'SD';
        confidence = 0.75;
        reasoning = 'SUV Max değişimi %30\'dan az - Stabil hastalık';
        recommendations = [
          'Mevcut tedavi devam etmeli',
          '8 hafta sonra kontrol önerilir',
          'Klinik bulgular yakın takip edilmeli'
        ];
      }

      return {
        baselineSUV,
        currentSUV,
        changePercent,
        response,
        confidence,
        reasoning,
        recommendations
      };
    } catch (error) {
      console.error('PERCIST criteria application failed:', error);
      throw error;
    }
  }

  async applyDeauvilleCriteria(suvLiver: number, suvLesion: number): Promise<DeauvilleCriteria> {
    if (!this.isInitialized) {
      throw new Error('Clinical Criteria Service not initialized');
    }

    try {
      const ratio = suvLesion / suvLiver;
      let score: 1 | 2 | 3 | 4 | 5;
      let description: string;
      let interpretation: string;
      let recommendations: string[];

      if (ratio < 0.5) {
        score = 1;
        description = 'SUV Max < Karaciğer SUV Max × 0.5';
        interpretation = 'Normal metabolik aktivite';
        recommendations = [
          'Tam yanıt göstergesi',
          'Tedavi başarılı',
          'Takip planı yapılmalı'
        ];
      } else if (ratio < 1.0) {
        score = 2;
        description = 'SUV Max < Karaciğer SUV Max';
        interpretation = 'Minimal metabolik aktivite';
        recommendations = [
          'Kısmi yanıt göstergesi',
          'Tedavi devam etmeli',
          'Kontrol önerilir'
        ];
      } else if (ratio < 1.5) {
        score = 3;
        description = 'SUV Max < Karaciğer SUV Max × 1.5';
        interpretation = 'Orta metabolik aktivite';
        recommendations = [
          'Belirsiz yanıt',
          'Klinik bulgular ile korelasyon',
          'Kısa süreli takip'
        ];
      } else if (ratio < 2.0) {
        score = 4;
        description = 'SUV Max < Karaciğer SUV Max × 2.0';
        interpretation = 'Yüksek metabolik aktivite';
        recommendations = [
          'Yetersiz yanıt',
          'Tedavi değişikliği gerekli',
          'Alternatif seçenekler değerlendirilmeli'
        ];
      } else {
        score = 5;
        description = 'SUV Max ≥ Karaciğer SUV Max × 2.0';
        interpretation = 'Çok yüksek metabolik aktivite';
        recommendations = [
          'Progresif hastalık',
          'Acil tedavi değişikliği',
          'Hasta bilgilendirilmeli'
        ];
      }

      return {
        score,
        description,
        interpretation,
        recommendations
      };
    } catch (error) {
      console.error('Deauville criteria application failed:', error);
      throw error;
    }
  }

  async assessOverallResponse(perCIST: PERCISTCriteria, deauville?: DeauvilleCriteria): Promise<ResponseAssessment> {
    if (!this.isInitialized) {
      throw new Error('Clinical Criteria Service not initialized');
    }

    try {
      let overallResponse: 'Complete Response' | 'Partial Response' | 'Stable Disease' | 'Progressive Disease';
      let confidence: number;
      let nextSteps: string[];

      // PERCIST ve Deauville kriterlerini birleştirerek genel yanıt değerlendirmesi
      if (perCIST.response === 'CR' && (!deauville || deauville.score <= 2)) {
        overallResponse = 'Complete Response';
        confidence = Math.min(perCIST.confidence, deauville?.confidence || 1.0);
        nextSteps = [
          'Tedavi tamamlandı',
          '3 ay sonra kontrol PET/CT',
          'Klinik takip planı'
        ];
      } else if (perCIST.response === 'PR' && (!deauville || deauville.score <= 3)) {
        overallResponse = 'Partial Response';
        confidence = Math.min(perCIST.confidence, deauville?.confidence || 1.0);
        nextSteps = [
          'Tedavi devam etmeli',
          '6 hafta sonra kontrol',
          'Yan etki takibi'
        ];
      } else if (perCIST.response === 'SD' && (!deauville || deauville.score <= 4)) {
        overallResponse = 'Stable Disease';
        confidence = Math.min(perCIST.confidence, deauville?.confidence || 1.0);
        nextSteps = [
          'Mevcut tedavi devam',
          '8 hafta sonra kontrol',
          'Klinik bulgu takibi'
        ];
      } else {
        overallResponse = 'Progressive Disease';
        confidence = Math.min(perCIST.confidence, deauville?.confidence || 1.0);
        nextSteps = [
          'Tedavi değişikliği gerekli',
          'Alternatif seçenekler',
          'Hasta bilgilendirme'
        ];
      }

      return {
        perCIST,
        deauville,
        overallResponse,
        confidence,
        nextSteps
      };
    } catch (error) {
      console.error('Overall response assessment failed:', error);
      throw error;
    }
  }

  async generateClinicalReport(assessment: ResponseAssessment): Promise<string> {
    if (!this.isInitialized) {
      throw new Error('Clinical Criteria Service not initialized');
    }

    try {
      const report = `
# Klinik Yanıt Değerlendirme Raporu

## PERCIST Kriterleri
- **Yanıt:** ${assessment.perCIST.response}
- **Güven:** ${(assessment.perCIST.confidence * 100).toFixed(1)}%
- **Açıklama:** ${assessment.perCIST.reasoning}

${assessment.deauville ? `
## Deauville Kriterleri
- **Skor:** ${assessment.deauville.score}/5
- **Açıklama:** ${assessment.deauville.description}
- **Yorum:** ${assessment.deauville.interpretation}
` : ''}

## Genel Değerlendirme
- **Yanıt:** ${assessment.overallResponse}
- **Güven:** ${(assessment.confidence * 100).toFixed(1)}%

## Öneriler
${assessment.nextSteps.map(step => `- ${step}`).join('\n')}

## Sonraki Adımlar
${assessment.perCIST.recommendations.map(rec => `- ${rec}`).join('\n')}

---
*Bu rapor otomatik olarak NeuroPETrix sistemi tarafından oluşturulmuştur.*
      `;

      return report.trim();
    } catch (error) {
      console.error('Clinical report generation failed:', error);
      throw error;
    }
  }
}

// Singleton instance
let clinicalCriteriaServiceInstance: ClinicalCriteriaService | null = null;

export const getClinicalCriteriaService = (): ClinicalCriteriaService => {
  if (!clinicalCriteriaServiceInstance) {
    clinicalCriteriaServiceInstance = new ClinicalCriteriaService();
  }
  return clinicalCriteriaServiceInstance;
};

export default ClinicalCriteriaService;


