'use client';

import React, { useState } from 'react';
import { v4 as uuidv4 } from 'uuid';
import ChatWindow from '@/features/chat/components/ChatWindow';
import DocumentSelector from '@/features/documents/components/DocumentSelector';

export default function ChatPage() {
  // In a real app, we might fetch the latest session or generate one
  const [sessionId] = useState(() => uuidv4());
  const [selectedDocumentIds, setSelectedDocumentIds] = useState<string[]>([]);

  return (
    <div className="flex h-screen w-full bg-gray-950 overflow-hidden">
      {/* Sidebar - Context Selection */}
      <DocumentSelector 
        selectedIds={selectedDocumentIds} 
        onChange={setSelectedDocumentIds} 
      />

      {/* Main Content - Chat Area */}
      <div className="flex-1 relative flex flex-col min-w-0">
        <header className="h-16 flex items-center justify-between px-8 border-b border-gray-800/50 bg-gray-950/50 backdrop-blur-md z-10">
          <div className="flex items-center gap-3">
            <div className="h-2 w-2 bg-green-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(34,197,94,0.5)]" />
            <h1 className="text-sm font-bold text-white tracking-tight">AI Assistant</h1>
            <span className="text-[10px] text-gray-500 font-mono bg-gray-900 px-2 py-0.5 rounded border border-gray-800">
              RAG-v1.0
            </span>
          </div>
          
          <div className="flex items-center gap-4">
             {/* Future: User profile, session settings */}
             <button className="text-xs text-gray-500 hover:text-gray-300 transition-colors">
               Session Settings
             </button>
          </div>
        </header>

        <ChatWindow 
          sessionId={sessionId} 
          selectedDocumentIds={selectedDocumentIds.length > 0 ? selectedDocumentIds : undefined} 
        />
      </div>
    </div>
  );
}
