const API_BASE = process.env.API_BASE || 'https://neuropetrix.onrender.com';

const nextConfig = {
  async rewrites() {
    return [
      { source: '/api-proxy/:path*', destination: `${API_BASE}/:path*` },
      { source: '/legacy/:path*', destination: `${API_BASE}/legacy/:path*` }
    ];
  },
  async headers() {
    return [
      {
        source: '/api-proxy/:path*',
        headers: [
          { key: 'Access-Control-Allow-Origin', value: '*' },
          { key: 'Access-Control-Allow-Methods', value: 'GET, POST, PUT, DELETE, OPTIONS' },
          { key: 'Access-Control-Allow-Headers', value: 'Content-Type, Authorization' }
        ]
      }
    ];
  }
};

export default nextConfig;
