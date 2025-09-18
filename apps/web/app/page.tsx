'use client';
import { useEffect, useState } from 'react';

export default function Home() {
  const [apiStatus, setApiStatus] = useState<'...' | 'ok' | 'fail'>('...');
  const [legacyStatus, setLegacyStatus] = useState<'...' | 'ok' | 'fail'>('...');
  const [v1Status, setV1Status] = useState<'...' | 'ok' | 'fail'>('...');

  useEffect(() => {
    // API health check
    fetch('/api-proxy/healthz')
      .then(r => r.json())
      .then(() => setApiStatus('ok'))
      .catch(() => setApiStatus('fail'));

    // Legacy health check
    fetch('/api-proxy/legacy/health')
      .then(r => r.json())
      .then(() => setLegacyStatus('ok'))
      .catch(() => setLegacyStatus('fail'));

    // V1 health check
    fetch('/api-proxy/v1/health')
      .then(r => r.json())
      .then(() => setV1Status('ok'))
      .catch(() => setV1Status('fail'));
  }, []);

  return (
    <main style={{ padding: 24, fontFamily: 'sans-serif' }}>
      <h1>🧠 NeuroPETRIX v3.0</h1>
      <p>AI-Powered Medical Imaging Analysis Platform</p>
      
      <div style={{ display: 'flex', gap: 20, marginTop: 20, flexWrap: 'wrap' }}>
        <div style={{ padding: 16, border: '1px solid #ccc', borderRadius: 8, minWidth: 200 }}>
          <h3>API Status</h3>
          <p>{apiStatus === 'ok' ? '✅ OK' : apiStatus === 'fail' ? '❌ FAIL' : '⏳ Loading...'}</p>
        </div>
        
        <div style={{ padding: 16, border: '1px solid #ccc', borderRadius: 8, minWidth: 200 }}>
          <h3>Legacy System</h3>
          <p>{legacyStatus === 'ok' ? '✅ OK' : legacyStatus === 'fail' ? '❌ FAIL' : '⏳ Loading...'}</p>
        </div>
        
        <div style={{ padding: 16, border: '1px solid #ccc', borderRadius: 8, minWidth: 200 }}>
          <h3>V1 API</h3>
          <p>{v1Status === 'ok' ? '✅ OK' : v1Status === 'fail' ? '❌ FAIL' : '⏳ Loading...'}</p>
        </div>
      </div>

      <div style={{ marginTop: 30 }}>
        <h3>Access Systems:</h3>
        <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
          <a 
            href="/legacy" 
            style={{ 
              padding: 12, 
              background: '#0070f3', 
              color: 'white', 
              textDecoration: 'none', 
              borderRadius: 6,
              display: 'inline-block'
            }}
          >
            🏥 Legacy System
          </a>
          <a 
            href="/v1" 
            style={{ 
              padding: 12, 
              background: '#0070f3', 
              color: 'white', 
              textDecoration: 'none', 
              borderRadius: 6,
              display: 'inline-block'
            }}
          >
            🚀 New API
          </a>
          <a 
            href="http://localhost:8501" 
            target="_blank"
            style={{ 
              padding: 12, 
              background: '#ff6b35', 
              color: 'white', 
              textDecoration: 'none', 
              borderRadius: 6,
              display: 'inline-block'
            }}
          >
            📊 Streamlit Desktop
          </a>
        </div>
      </div>

      <div style={{ marginTop: 30, padding: 16, background: '#f5f5f5', borderRadius: 8 }}>
        <h4>System Information:</h4>
        <ul>
          <li><strong>API Base:</strong> {process.env.NEXT_PUBLIC_API_BASE || '/api-proxy'}</li>
          <li><strong>Version:</strong> 3.0.0</li>
          <li><strong>Features:</strong> AI Analysis, DICOM Processing, Report Generation</li>
        </ul>
      </div>
    </main>
  );
}
