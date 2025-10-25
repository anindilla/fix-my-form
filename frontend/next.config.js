/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ['localhost', 'your-r2-bucket.your-account.r2.cloudflarestorage.com'],
  },
}

module.exports = nextConfig
