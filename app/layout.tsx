import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import QueryProvider from "@/components/providers/QueryProvider";
import AgGridProvider from "@/components/providers/AgGridProvider";
import Link from "next/link";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "NBA Betting Analytics",
  description: "AI-powered NBA betting predictions using machine learning",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        <nav className="bg-blue-600 text-white shadow-lg">
          <div className="container mx-auto px-4">
            <div className="flex justify-between items-center py-4">
              <Link href="/" className="text-2xl font-bold">
                NBA Betting Analytics
              </Link>
              <div className="space-x-6">
                <Link href="/" className="hover:text-blue-200 transition-colors">
                  Dashboard
                </Link>
                <Link href="/predictions" className="hover:text-blue-200 transition-colors">
                  Predictions
                </Link>
                <Link href="/betting" className="hover:text-blue-200 transition-colors">
                  My Bets
                </Link>
                <Link href="/data-tables" className="hover:text-blue-200 transition-colors">
                  Data Tables
                </Link>
              </div>
            </div>
          </div>
        </nav>
        <main className="min-h-screen bg-gray-50">
          <QueryProvider>
            <AgGridProvider>
              {children}
            </AgGridProvider>
          </QueryProvider>
        </main>
      </body>
    </html>
  );
}
