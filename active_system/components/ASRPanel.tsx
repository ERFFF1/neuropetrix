import { useState } from 'react';
import { transcribe } from './api';

export default function ASRPanel() {
  const [text, setText] = useState<string>(''); const [busy, setBusy]=useState(false); const [err,setErr]=useState<string|null>(null);
  async function onFile(e: React.ChangeEvent<HTMLInputElement>) {
    const f=e.target.files?.[0]; if(!f) return; setBusy(true); setErr(null);
    try { const r=await transcribe(f); setText(r.transcript ?? JSON.stringify(r)); }
    catch(e:any){ setErr(e.message); } finally{ setBusy(false); }
  }
  return (
    <div className="p-4 max-w-3xl mx-auto space-y-3">
      <h2 className="text-xl font-semibold">ASR</h2>
      <input type="file" accept="audio/*" onChange={onFile}/>
      {busy && <div>Yükleniyor…</div>}
      {err && <pre className="text-red-600">{err}</pre>}
      {text && <pre className="bg-gray-50 p-3 rounded">{text}</pre>}
    </div>
  );
}


