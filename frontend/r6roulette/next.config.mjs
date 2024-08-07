/** @type {import('next').NextConfig} */
const isProd = process.env.NODE_ENV === "production";

const nextConfig = {
    basePath: isProd ? "/r6roulette" : '',
    output: 'export',
    distDir: 'dist',
    reactStrictMode: true,
};

export default nextConfig;
