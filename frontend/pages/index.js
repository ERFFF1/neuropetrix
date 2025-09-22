import React, { useState, useEffect } from 'react';

const HomePage = () => {
  const [apiStatus, setApiStatus] = useState('Checking...');
  const [backendUrl, setBackendUrl] = useState(process.env.NEXT_PUBLIC_API_URL || 'https://neuropetrix-backend-fzy0h9wrz-erfff1s-projects.vercel.app');

  useEffect(() => {
    // Backend API status kontrolü
    fetch(`${backendUrl}/api/healthz`)
      .then(response => response.json())
      .then(data => {
        setApiStatus('Connected ✅');
      })
      .catch(error => {
        setApiStatus('Disconnected ❌');
        console.error('API Error:', error);
      });
  }, [backendUrl]);

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif', maxWidth: '1200px', margin: '0 auto' }}>
      <header style={{ textAlign: 'center', marginBottom: '40px', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '10px' }}>
        <h1 style={{ color: '#2c3e50', marginBottom: '10px' }}>🚀 NeuroPETRIX Full-Stack App</h1>
        <p style={{ color: '#7f8c8d', fontSize: '18px' }}>Vercel Tek Platform - Backend + Frontend</p>
        <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#e8f5e8', borderRadius: '5px' }}>
          <strong>API Status:</strong> <span style={{ color: apiStatus.includes('✅') ? 'green' : 'red' }}>{apiStatus}</span>
        </div>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px', marginBottom: '40px' }}>
        {/* Status Check Card */}
        <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '10px', backgroundColor: '#fff' }}>
          <h2 style={{ color: '#2c3e50', marginBottom: '15px' }}>📊 System Status</h2>
          <div style={{ marginBottom: '10px' }}>
            <strong>Frontend:</strong> <span style={{ color: 'green' }}>Online ✅</span>
          </div>
          <div style={{ marginBottom: '10px' }}>
            <strong>Backend API:</strong> <span style={{ color: apiStatus.includes('✅') ? 'green' : 'red' }}>{apiStatus}</span>
          </div>
          <div style={{ marginBottom: '10px' }}>
            <strong>Platform:</strong> Vercel Serverless
          </div>
        </div>

        {/* API Endpoints Card */}
        <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '10px', backgroundColor: '#fff' }}>
          <h2 style={{ color: '#2c3e50', marginBottom: '15px' }}>🔗 API Endpoints</h2>
          <div style={{ marginBottom: '10px' }}>
            <a 
              href={`${backendUrl}/api/healthz`} 
              target="_blank" 
              rel="noopener noreferrer"
              style={{ color: '#3498db', textDecoration: 'none', display: 'block', padding: '5px 0' }}
            >
              Health Check: /api/healthz
            </a>
          </div>
          <div style={{ marginBottom: '10px' }}>
            <a 
              href={`${backendUrl}/api/test`} 
              target="_blank" 
              rel="noopener noreferrer"
              style={{ color: '#3498db', textDecoration: 'none', display: 'block', padding: '5px 0' }}
            >
              Test Endpoint: /api/test
            </a>
          </div>
        </div>

        {/* NeuroPETRIX Features Card */}
        <div style={{ padding: '20px', border: '1px solid #ddd', borderRadius: '10px', backgroundColor: '#fff' }}>
          <h2 style={{ color: '#2c3e50', marginBottom: '15px' }}>🧠 NeuroPETRIX Features</h2>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            <li style={{ marginBottom: '8px' }}>🔬 DICOM Processing</li>
            <li style={{ marginBottom: '8px' }}>📊 TSNM Reporting</li>
            <li style={{ marginBottom: '8px' }}>🤖 AI Integration</li>
            <li style={{ marginBottom: '8px' }}>📋 Clinical Decision Support</li>
          </ul>
        </div>
      </div>

      {/* Vercel Advantages */}
      <div style={{ backgroundColor: '#f0f0f0', padding: '20px', borderRadius: '10px', marginBottom: '20px' }}>
        <h3 style={{ color: '#2c3e50', marginBottom: '15px' }}>✅ Vercel Tek Platform Avantajları:</h3>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '15px' }}>
          <div>🚀 Tek platform yönetimi</div>
          <div>⚡ Otomatik deploy (Git push)</div>
          <div>🔗 Backend + Frontend aynı yerde</div>
          <div>💰 Tek faturalandırma</div>
        </div>
      </div>

      {/* Development Info */}
      <div style={{ backgroundColor: '#e8f4f8', padding: '20px', borderRadius: '10px', textAlign: 'center' }}>
        <h3 style={{ color: '#2c3e50', marginBottom: '10px' }}>🛠️ Development Status</h3>
        <p style={{ color: '#7f8c8d', margin: '5px 0' }}>
          <strong>Repository:</strong> ERFFF1/neuropetrix
        </p>
        <p style={{ color: '#7f8c8d', margin: '5px 0' }}>
          <strong>Branch:</strong> ops/vercel-only
        </p>
        <p style={{ color: '#7f8c8d', margin: '5px 0' }}>
          <strong>Last Deploy:</strong> {new Date().toLocaleString('tr-TR')}
        </p>
      </div>
    </div>
  );
};

export default HomePage;