import { useState, useEffect } from 'react';

export default function Home() {
  const [backendStatus, setBackendStatus] = useState('Checking...');
  const [backendUrl] = useState('https://neuropetrix.onrender.com');

  useEffect(() => {
    fetch(`${backendUrl}/healthz`)
      .then(res => res.json())
      .then(data => setBackendStatus(data.status))
      .catch(err => setBackendStatus('Error: ' + err.message));
  }, [backendUrl]);

  return (
    <div style={{ padding: '20px', fontFamily: 'Arial, sans-serif' }}>
      <h1>NeuroPETRIX Frontend</h1>
      <p>Backend Status: <strong>{backendStatus}</strong></p>
      <p>Backend URL: <a href={backendUrl} target="_blank">{backendUrl}</a></p>
      <div style={{ marginTop: '20px' }}>
        <h2>Available Endpoints:</h2>
        <ul>
          <li><a href={`${backendUrl}/`} target="_blank">Root: {backendUrl}/</a></li>
          <li><a href={`${backendUrl}/healthz`} target="_blank">Health: {backendUrl}/healthz</a></li>
        </ul>
      </div>
    </div>
  );
}
