
export const clinicalRules = {
  version: "2.0.0",
  guidelineVersion: "Oncology-2024.v1",

  templates: {
    lung: {
      label: "Oncology - Lung Cancer",
      DIAGNOSIS: {},
      PROGNOSIS: {},
      TX_RESPONSE: {
        percistDeltaSUV: { progression: 30, response: -30 }
      },
      TREATMENT: {},
    },
    lymphoma: {
      label: "Oncology - Lymphoma",
      DIAGNOSIS: {},
      PROGNOSIS: {},
      TX_RESPONSE: {}, // Uses Deauville, not simple delta
      TREATMENT: {},
    },
    ent_sinusitis: {
      label: "ENT – Sinusitis",
      DIAGNOSIS: {
        prohibitedTerms: ["mg","tablet","antibiotik","amoxicillin","oseltamivir","osimertinib"],
        requireDiagnosticSteps: true,
        defaultDiagnosticSteps: [
          { name:"Nazal endoskopi", rationale:"Akıntı tipi/ostial tıkanıklık değerlendirmesi" },
          { name:"Kontrastlı Sinüs BT (komplike/atipik/tedavi başarısızlığı varsa)", rationale:"Komplikasyon/variante anatomi" }
        ]
      },
      TREATMENT: {
        prohibitedTerms: [] 
      },
      PROGNOSIS: {},
      TX_RESPONSE: {},
    },
    General: {
        label: "General",
        DIAGNOSIS: {},
        PROGNOSIS: {},
        TX_RESPONSE: {},
        TREATMENT: {},
    }
  },

  goals: {
    DIAGNOSIS: { 
      prohibitedTerms: ["mg","tablet","dose","antibiotik","amoxicillin","osimertinib", "tedavi", "kemoterapi", "ilaç"], 
      requireDiagnosticSteps: true 
    },
    TX_RESPONSE: { prohibitedTerms: [] },
    PROGNOSIS: { prohibitedTerms: [] },
    TREATMENT: { prohibitedTerms: [] },
  },

  qcPolicies: { 
    failedAddsRepeatScan: true 
  },

  thresholds: {
    deltaSUVPercent: { progression: 30, response: -30 },
    nearZeroPreviousSUV: 0.5,
  }
} as const;

export type ClinicalRules = typeof clinicalRules;
