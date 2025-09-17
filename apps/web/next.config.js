/** @type {import('next').NextConfig} */
const API_BASE = process.env.API_BASE || 'http://localhost:8080';
const nextConfig = {
  async rewrites() {
    return [{ source: '/api-proxy/:path*', destination: `${API_BASE}/:path*` }];
  }
}
module.exports = nextConfig;
