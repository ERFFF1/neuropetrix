import React from 'react';

const HomePage = () => {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>🚀 NeuroPETRIX Full-Stack App</h1>
      <p>Vercel Tek Platform - Backend + Frontend</p>
      
      <h2>📊 Status Check:</h2>
      <p>API Status: <span style={{color: 'green'}}>ok</span></p>
      
      <h2>🔗 Available Endpoints:</h2>
      <ul>
        <li>
          <a href="/api/health" target="_blank" rel="noopener noreferrer">
            Health Check: /api/health
          </a>
        </li>
        <li>
          <a href="/api/test" target="_blank" rel="noopener noreferrer">
            Test Endpoint: /api/test
          </a>
        </li>
      </ul>
      
      <div style={{backgroundColor: '#f0f0f0', padding: '15px', marginTop: '20px'}}>
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
};

export default HomePage;
