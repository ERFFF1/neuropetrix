import { useState, useEffect } from 'react';

export default function Home() {
  const [backendStatus, setBackendStatus] = useState('Checking...');
  const [apiStatus, setApiStatus] = useState('Checking...');

  useEffect(() => {
    // Vercel API endpoint'ini test et
    fetch('/api/health')
      .then(res => res.json())
      .then(data => setApiStatus(data.status))
      .catch(err => setApiStatus('Error: ' + err.message));
  }, []);

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>🚀 NeuroPETRIX Full-Stack App</h1>
      <p>Vercel Tek Platform - Backend + Frontend</p>
      
      <div style={{ marginTop: '20px' }}>
        <h2>📊 Status Check:</h2>
        <p>API Status: <strong>{apiStatus}</strong></p>
      </div>
      
      <div style={{ marginTop: '20px' }}>
        <h2>🔗 Available Endpoints:</h2>
        <ul>
          <li><a href="/api/health" target="_blank">Health Check: /api/health</a></li>
          <li><a href="/api/test" target="_blank">Test Endpoint: /api/test</a></li>
        </ul>
      </div>
      
      <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#f0f0f0', borderRadius: '5px' }}>
        <h3>✅ Vercel Tek Platform Avantajları:</h3>
        <ul>
          <li>🚀 Tek platform yönetimi</li>
          <li>⚡ Otomatik deploy (Git push)</li>
          <li>🔗 Backend + Frontend aynı yerde</li>
          <li>💰 Tek faturalandırma</li>
        </ul>
      </div>
    </div>
  );
}
