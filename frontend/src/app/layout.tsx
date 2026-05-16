import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Providers from "@/components/Providers";
import ErrorBoundary from "@/components/shared/ErrorBoundary";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "AI PDF Chatbot | Premium RAG Experience",
  description: "Chat with your documents using advanced AI and semantic search.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${inter.variable} h-full antialiased dark`} suppressHydrationWarning>
      <body className="min-h-full bg-gray-950 text-gray-100 selection:bg-blue-500/30 selection:text-blue-200">
        <Providers>
          <div className="relative flex min-h-screen flex-col">
            {/* Background Gradient Orbs */}
            <div className="fixed inset-0 -z-10 overflow-hidden pointer-events-none">
              <div className="absolute -top-[10%] -left-[10%] h-[40%] w-[40%] bg-blue-600/10 blur-[120px] rounded-full animate-pulse" />
              <div className="absolute top-[20%] -right-[10%] h-[35%] w-[35%] bg-purple-600/10 blur-[120px] rounded-full animate-pulse" style={{ animationDelay: '2s' }} />
            </div>

            <ErrorBoundary>
              <main className="flex-1 flex flex-col">
                {children}
              </main>
            </ErrorBoundary>
          </div>
        </Providers>
      </body>
    </html>
  );
}
