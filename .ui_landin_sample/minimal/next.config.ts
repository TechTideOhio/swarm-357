import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Disable source maps in production to prevent easy code inspection
  productionBrowserSourceMaps: false,
  // Additional optimizations
  compiler: {
    // Remove console.log in production
    removeConsole: process.env.NODE_ENV === "production",
  },
};

export default nextConfig;
