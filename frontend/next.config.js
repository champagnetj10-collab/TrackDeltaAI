/** @type {import('next').NextConfig} */
const nextConfig = {
  // Enable strict mode for catching potential issues early
  reactStrictMode: true,

  // Environment variables exposed to the browser
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  },

  // Redirect root to dashboard if authenticated (handled in middleware)
  async redirects() {
    return [];
  },
};

module.exports = nextConfig;
