/** @type {import('next').NextConfig} */
const nextConfig = {
	images: {
		domains: ["localhost"],
	},
	env: {
		NEXT_PUBLIC_APP_NAME: process.env.NEXT_PUBLIC_APP_NAME || "AI Chat App",
		NEXT_PUBLIC_APP_VERSION: process.env.NEXT_PUBLIC_APP_VERSION || "0.1.0",
	},
	async rewrites() {
		return [
			{
				source: "/api/:path*",
				destination: `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/:path*`,
			},
		];
	},
};

module.exports = nextConfig;
