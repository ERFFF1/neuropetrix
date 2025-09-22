'use client';
import { useEffect, useState } from 'react';

export default function Home() {
  const [apiStatus, setApiStatus] = useState<'...' | 'ok' | 'fail'>('...');
  const [legacyStatus, setLegacyStatus] = useState<'...' | 'ok' | 'fail'>('...');
  const [v1Status, setV1Status] = useState<'...' | 'ok' | 'fail'>('...');
  const [streamlitStatus, setStreamlitStatus] = useState<'...' | 'ok' | 'fail'>('...');
  const [activeTab, setActiveTab] = useState<'dashboard' | 'streamlit' | 'api'>('dashboard');

  useEffect(() => {
    // API health check
    fetch('http://localhost:8000/healthz')
      .then(r => r.json())
      .then(() => setApiStatus('ok'))
      .catch(() => setApiStatus('fail'));

    // Legacy health check
    fetch('http://localhost:8000/legacy/health')
      .then(r => r.json())
      .then(() => setLegacyStatus('ok'))
      .catch(() => setLegacyStatus('fail'));

    // V1 health check
    fetch('http://localhost:8000/v1/health')
      .then(r => r.json())
      .then(() => setV1Status('ok'))
      .catch(() => setV1Status('fail'));

    // Streamlit health check
    fetch('http://localhost:8501')
      .then(() => setStreamlitStatus('ok'))
      .catch(() => setStreamlitStatus('fail'));
  }, []);

  return (
    <main style={{ padding: 24, fontFamily: 'sans-serif', height: '100vh', display: 'flex', flexDirection: 'column' }}>
      <h1>🧠 NeuroPETRIX v3.0 - Entegre Sistem</h1>
      <p>AI-Powered Medical Imaging Analysis Platform</p>
      
      {/* Tab Navigation */}
      <div style={{ display: 'flex', gap: 10, marginTop: 20, borderBottom: '1px solid #ccc' }}>
        <button 
          onClick={() => setActiveTab('dashboard')}
          style={{ 
            padding: '10px 20px', 
            background: activeTab === 'dashboard' ? '#0070f3' : '#f0f0f0',
            color: activeTab === 'dashboard' ? 'white' : 'black',
            border: 'none',
            borderRadius: '6px 6px 0 0',
            cursor: 'pointer'
          }}
        >
          📊 Dashboard
        </button>
        <button 
          onClick={() => setActiveTab('streamlit')}
          style={{ 
            padding: '10px 20px', 
            background: activeTab === 'streamlit' ? '#0070f3' : '#f0f0f0',
            color: activeTab === 'streamlit' ? 'white' : 'black',
            border: 'none',
            borderRadius: '6px 6px 0 0',
            cursor: 'pointer'
          }}
        >
          🏥 Streamlit Desktop
        </button>
        <button 
          onClick={() => setActiveTab('api')}
          style={{ 
            padding: '10px 20px', 
            background: activeTab === 'api' ? '#0070f3' : '#f0f0f0',
            color: activeTab === 'api' ? 'white' : 'black',
            border: 'none',
            borderRadius: '6px 6px 0 0',
            cursor: 'pointer'
          }}
        >
          🚀 API Test
        </button>
      </div>

      {/* Tab Content */}
      {activeTab === 'dashboard' && (
        <div style={{ flex: 1, padding: 20 }}>
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

            <div style={{ padding: 16, border: '1px solid #ccc', borderRadius: 8, minWidth: 200 }}>
              <h3>Streamlit Desktop</h3>
              <p>{streamlitStatus === 'ok' ? '✅ OK' : streamlitStatus === 'fail' ? '❌ FAIL' : '⏳ Loading...'}</p>
            </div>
          </div>

          <div style={{ marginTop: 30, padding: 16, background: '#f5f5f5', borderRadius: 8 }}>
            <h4>System Information:</h4>
            <ul>
              <li><strong>Frontend:</strong> http://localhost:3001 (Next.js)</li>
              <li><strong>Backend:</strong> http://localhost:8000 (FastAPI)</li>
              <li><strong>Streamlit:</strong> http://localhost:8501 (Desktop App)</li>
              <li><strong>Version:</strong> 3.0.0</li>
              <li><strong>Features:</strong> AI Analysis, DICOM Processing, Report Generation</li>
            </ul>
          </div>
        </div>
      )}

      {activeTab === 'streamlit' && (
        <div style={{ flex: 1, padding: 20 }}>
          <h3>🏥 Streamlit Desktop - Entegre Görünüm</h3>
          <div style={{ border: '1px solid #ccc', borderRadius: 8, height: '70vh', overflow: 'hidden' }}>
            <iframe 
              src="http://localhost:8501" 
              width="100%" 
              height="100%"
              style={{ border: 'none' }}
              title="Streamlit Desktop"
            />
          </div>
        </div>
      )}

      {activeTab === 'api' && (
        <div style={{ flex: 1, padding: 20 }}>
          <h3>🚀 API Test - Entegre Görünüm</h3>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
            <div>
              <h4>API Endpoints:</h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                <button 
                  onClick={() => fetch('http://localhost:8000/healthz').then(r => r.json()).then(console.log)}
                  style={{ padding: 10, background: '#0070f3', color: 'white', border: 'none', borderRadius: 4 }}
                >
                  Test /healthz
                </button>
                <button 
                  onClick={() => fetch('http://localhost:8000/legacy/health').then(r => r.json()).then(console.log)}
                  style={{ padding: 10, background: '#0070f3', color: 'white', border: 'none', borderRadius: 4 }}
                >
                  Test /legacy/health
                </button>
                <button 
                  onClick={() => fetch('http://localhost:8000/v1/health').then(r => r.json()).then(console.log)}
                  style={{ padding: 10, background: '#0070f3', color: 'white', border: 'none', borderRadius: 4 }}
                >
                  Test /v1/health
                </button>
              </div>
            </div>
            <div>
              <h4>API Response:</h4>
              <div id="api-response" style={{ 
                background: '#f5f5f5', 
                padding: 10, 
                borderRadius: 4, 
                minHeight: 200,
                fontFamily: 'monospace',
                fontSize: 12,
                overflow: 'auto'
              }}>
                Click a button to test API endpoints...
              </div>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}
