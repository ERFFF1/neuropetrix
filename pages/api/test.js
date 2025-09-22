export default function handler(req, res) {
  res.status(200).json({ 
    message: 'NeuroPETRIX Test Endpoint',
    data: {
      neuropetrix: 'online',
      platform: 'Vercel',
      type: 'Full-Stack App',
      features: ['Backend API', 'Frontend UI', 'Serverless Functions']
    },
    timestamp: new Date().toISOString()
  });
}
