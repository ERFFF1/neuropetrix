const API_BASE = process.env.API_BASE || 'https://neuropetrix.onrender.com';

const nextConfig = {
  async rewrites() {
    return [
      { source: '/api-proxy/:path*', destination: `${API_BASE}/:path*` },
      { source: '/legacy/:path*', destination: `${API_BASE}/legacy/:path*` }
    ];
  },
};

export default nextConfig;
