import type { NextConfig } from "next";

const API_BASE = process.env.API_BASE || "http://localhost:8080";

const nextConfig: NextConfig = {
  async rewrites() {
    // /api-proxy/* -> API_BASE/*
    return [{ source: "/api-proxy/:path*", destination: `${API_BASE}/:path*` }];
  },
};

export default nextConfig;
