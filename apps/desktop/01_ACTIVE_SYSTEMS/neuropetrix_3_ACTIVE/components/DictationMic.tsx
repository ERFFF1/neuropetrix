import { useEffect, useRef, useState } from "react";

interface DictationMicProps {
  onText: (text: string) => void;
}

export default function DictationMic({ onText }: DictationMicProps) {
  const [rec, setRec] = useState<any>(null);
  const [active, setActive] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const buffer = useRef<string>("");

  useEffect(() => {
    // Web Speech API desteğini kontrol et
    const SR: any = (window as any).webkitSpeechRecognition || (window as any).SpeechRecognition;
    if (!SR) {
      setIsSupported(false);
      setError("Tarayıcınız dikte özelliğini desteklemiyor");
      return;
    }

    setIsSupported(true);
    const recognition = new SR();
    
    // Türkçe dil desteği
    recognition.lang = "tr-TR";
    recognition.continuous = true;
    recognition.interimResults = true;
    
    recognition.onresult = (event: any) => {
      let transcript = "";
      for (let i = event.resultIndex; i < event.results.length; i++) {
        transcript += event.results[i][0].transcript;
      }
      buffer.current = transcript;
      onText(transcript);
    };
    
    recognition.onend = () => {
      setActive(false);
    };
    
    recognition.onerror = (event: any) => {
      console.error("Dikte hatası:", event.error);
      setError(`Dikte hatası: ${event.error}`);
      setActive(false);
    };
    
    setRec(recognition);
  }, [onText]);

  function toggle() {
    if (!isSupported) {
      alert("Tarayıcınız dikte özelliğini desteklemiyor. Chrome, Edge veya Safari kullanın.");
      return;
    }
    
    if (!rec) {
      alert("Dikte başlatılamadı. Sayfayı yenileyin.");
      return;
    }
    
    if (active) {
      rec.stop();
      setActive(false);
    } else {
      buffer.current = "";
      setError(null);
      try {
        rec.start();
        setActive(true);
      } catch (err) {
        console.error("Dikte başlatma hatası:", err);
        setError("Dikte başlatılamadı");
      }
    }
  }

  if (!isSupported) {
    return (
      <div className="flex items-center gap-2">
        <button 
          disabled 
          className="px-3 py-2 rounded border border-gray-300 bg-gray-100 text-gray-500 cursor-not-allowed"
          title="Tarayıcınız dikte özelliğini desteklemiyor"
        >
          🎤 Dikte (Desteklenmiyor)
        </button>
        <span className="text-xs text-gray-500">
          Chrome/Edge/Safari gerekli
        </span>
      </div>
    );
  }

  return (
    <div className="flex items-center gap-2">
      <button 
        onClick={toggle} 
        className={`px-3 py-2 rounded transition-all duration-200 focus:ring-2 focus:ring-blue-500 ${
          active 
            ? 'bg-red-500 text-white hover:bg-red-600 shadow-lg' 
            : 'border border-gray-300 hover:border-gray-400 hover:bg-gray-50'
        }`}
        title={active ? "Dikteyi durdur" : "Dikteyi başlat"}
      >
        {active ? "● Kayıt" : "🎤 Dikte"}
      </button>
      
      {error && (
        <span className="text-xs text-red-600 max-w-xs">
          ⚠️ {error}
        </span>
      )}
      
      {active && (
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div>
          <span className="text-xs text-gray-600">Kayıt yapılıyor...</span>
        </div>
      )}
    </div>
  );
}
