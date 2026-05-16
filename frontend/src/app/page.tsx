'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/useAuthStore';
import { ROUTES } from '@/config/constants';
import UploadDropzone from '@/features/documents/components/UploadDropzone';
import DocumentLibrary from '@/features/documents/components/DocumentLibrary';
import { LayoutDashboard, MessageSquare, LogOut, FileText, Sparkles, Layers } from 'lucide-react';
import { AuthService } from '@/features/auth/services/auth.service';

export default function DashboardPage() {
  const { user } = useAuthStore();
  const router = useRouter();

  return (
    <div className="flex h-screen bg-gray-950 text-white overflow-hidden">
      {/* Sidebar */}
      <aside className="w-64 border-r border-gray-800 bg-gray-900/50 flex flex-col">
        <div className="p-6 border-b border-gray-800 flex items-center gap-3">
          <div className="h-8 w-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <Sparkles className="h-5 w-5 text-white" />
          </div>
          <span className="font-bold text-lg tracking-tight">PDF AI</span>
        </div>

        <nav className="flex-1 p-4 space-y-2">
          <button 
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl bg-blue-600/10 text-blue-400 border border-blue-500/20 transition-all"
          >
            <LayoutDashboard className="h-5 w-5" />
            <span className="font-medium text-sm">Dashboard</span>
          </button>
          
          <button 
            onClick={() => router.push(ROUTES.PROTECTED.CHAT)}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-gray-400 hover:bg-gray-800 transition-all"
          >
            <MessageSquare className="h-5 w-5" />
            <span className="font-medium text-sm">Chat Assistant</span>
          </button>
        </nav>

        <div className="p-4 border-t border-gray-800">
          <div className="flex items-center gap-3 px-4 py-3 mb-2">
            <div className="h-8 w-8 rounded-full bg-gradient-to-tr from-blue-500 to-purple-500 flex items-center justify-center text-xs font-bold">
              {user?.email?.charAt(0).toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-xs font-medium truncate">{user?.email}</p>
              <p className="text-[10px] text-gray-500">Free Plan</p>
            </div>
          </div>
          <button 
            onClick={() => AuthService.logout()}
            className="w-full flex items-center gap-3 px-4 py-2.5 rounded-xl text-gray-500 hover:text-red-400 hover:bg-red-400/5 transition-all text-sm"
          >
            <LogOut className="h-4 w-4" />
            <span>Sign Out</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-900/10 via-gray-950 to-gray-950">
        <header className="h-16 px-8 flex items-center justify-between border-b border-gray-800/50 backdrop-blur-sm sticky top-0 z-10">
          <h2 className="text-sm font-semibold text-gray-300 uppercase tracking-widest">Document Management</h2>
          <div className="flex items-center gap-4">
             <button 
               onClick={() => router.push(ROUTES.PROTECTED.CHAT)}
               className="px-4 py-1.5 bg-blue-600 hover:bg-blue-500 text-white rounded-lg text-xs font-semibold transition-all shadow-lg shadow-blue-600/20"
             >
               Start Chatting
             </button>
          </div>
        </header>

        <div className="max-w-5xl mx-auto p-8 space-y-8">
          {/* Welcome Section */}
          <section>
            <h1 className="text-3xl font-bold tracking-tight">Welcome back!</h1>
            <p className="text-gray-400 mt-2">Upload your PDF documents to start your AI-powered analysis.</p>
          </section>

          {/* Upload Section */}
          <section className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            <div className="lg:col-span-1">
              <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
                <FileText className="h-5 w-5 text-blue-500" />
                Upload New
              </h3>
              <p className="text-xs text-gray-500 leading-relaxed">
                Supports standard PDF files up to 50MB. Once uploaded, our AI will automatically extract and index the content for retrieval.
              </p>
            </div>
            <div className="lg:col-span-2">
              <UploadDropzone />
            </div>
          </section>

          {/* List Section */}
          <section className="space-y-4">
            <h3 className="text-lg font-semibold flex items-center gap-2">
              <Layers className="h-5 w-5 text-purple-500" />
              Your Library
            </h3>
            <DocumentLibrary />
          </section>
        </div>
      </main>
    </div>
  );
}


