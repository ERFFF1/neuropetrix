import { useEffect, useState } from 'react';

export default function Home() {
  const [msg, setMsg] = useState('Kontrol ediliyor...');

  useEffect(() => {
    const base = process.env.NEXT_PUBLIC_API_URL; // Vercel env'den gelecek
    fetch(`${base}/api/healthz`)
      .then(r => r.json())
      .then(d => setMsg(`Backend: ${d.neuropetrix} (${d.platform})`))
      .catch(() => setMsg('API bağlantı hatası!'));
  }, []);

  return (
    <main style={{padding:20, fontFamily:'sans-serif'}}>
      <h1>Neuropetrix</h1>
      <p>{msg}</p>
    </main>
  );
}