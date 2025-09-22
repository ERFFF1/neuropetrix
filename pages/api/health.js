export default function handler(req, res) {
  res.status(200).json({ 
    status: 'ok',
    message: 'NeuroPETRIX API is running on Vercel',
    timestamp: new Date().toISOString(),
    platform: 'Vercel Serverless'
  });
}
