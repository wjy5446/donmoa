/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: ['@donmoa/shared'],
  experimental: {
    serverActions: true,
  },
}

module.exports = nextConfig

