/** @type {import('next').NextConfig} */
const nextConfig = {
  transpilePackages: ["three", "@react-three/fiber", "@react-three/drei"],
  reactStrictMode: false, // Prevents duplicate render cycles in Three.js Canvas
};

export default nextConfig;
