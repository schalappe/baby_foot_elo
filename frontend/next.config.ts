import type { NextConfig } from "next";
import path from "path";

const nextConfig: NextConfig = {
  webpack: (config, { buildId, dev, isServer, defaultLoaders, webpack }) => {
    // Add the path aliases
    config.resolve.alias = {
      ...config.resolve.alias, // Preserve any existing aliases
      '@/app': path.resolve(__dirname, '../app'),
      '@/components': path.resolve(__dirname, '../components'),
      '@/hooks': path.resolve(__dirname, '../hooks'),
      '@/lib': path.resolve(__dirname, '../lib'),
      '@/services': path.resolve(__dirname, '../services'),
      '@/types': path.resolve(__dirname, '../types'),
      '@/public': path.resolve(__dirname, '../public'),
    };
    
    // Important: return the modified config
    return config;
  },
  /* other config options can go here */
};

export default nextConfig;
