'use client';

import React from 'react';
import { useChatStream } from '../hooks/useChatStream';
import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';
import CitationViewer from './CitationViewer';
import { Sparkles } from 'lucide-react';
import { Citation } from '@/types';
import { API_CONFIG } from '@/config/constants';

interface Props {
  sessionId: string;
  selectedDocumentIds?: string[];
}

const ChatWindow: React.FC<Props> = ({ sessionId, selectedDocumentIds }) => {
  const {
    messages,
    isStreaming,
    currentResponse,
    sendMessage,
    stopGeneration,
    scrollRef,
    handleScroll,
  } = useChatStream(sessionId);

  const [activeCitation, setActiveCitation] = React.useState<Citation | null>(null);

  const isEmpty = messages.length === 0 && !isStreaming;

  return (
    <div className="flex flex-col h-full w-full max-w-5xl mx-auto overflow-hidden">
      {/* Messages Area */}
      <div 
        className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-800 scrollbar-track-transparent"
        onScroll={handleScroll}
      >
        {isEmpty ? (
          <div className="h-full flex flex-col items-center justify-center p-12 text-center animate-in fade-in duration-700">
            <div className="mb-6 p-4 bg-blue-600/10 rounded-3xl border border-blue-500/20">
              <Sparkles className="h-12 w-12 text-blue-500" />
            </div>
            <h2 className="text-2xl font-bold text-white mb-2">How can I help you today?</h2>
            <p className="text-gray-400 max-w-md">
              Ask any question about your uploaded documents. I'll search through them and provide precise answers with citations.
            </p>
            
            <div className="mt-12 grid grid-cols-1 md:grid-cols-2 gap-4 w-full max-w-2xl">
              {[
                "What are the key takeaways from this PDF?",
                "Summarize the second section for me.",
                "Find any mentions of financial risks.",
                "How does the author define 'RAG'?"
              ].map((suggestion) => (
                <button
                  key={suggestion}
                  onClick={() => sendMessage(suggestion, selectedDocumentIds)}
                  className="p-4 bg-gray-900/50 hover:bg-gray-800 border border-gray-800 rounded-2xl text-left text-sm text-gray-300 transition-all hover:border-gray-700 active:scale-[0.98]"
                >
                  {suggestion}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <div className="flex flex-col pb-32">
            {messages.map((msg) => (
              <MessageBubble 
                key={msg.id} 
                message={msg} 
                onCitationClick={setActiveCitation} 
              />
            ))}
            
            {isStreaming && currentResponse && (
              <MessageBubble 
                message={{ role: 'assistant', content: currentResponse }} 
                isStreaming={true} 
                onCitationClick={setActiveCitation}
              />
            )}
            
            {isStreaming && !currentResponse && (
              <div className="flex gap-4 p-6 bg-gray-900/40 animate-pulse">
                 <div className="h-9 w-9 rounded-lg bg-blue-600/10" />
                 <div className="flex-1 space-y-2 pt-2">
                   <div className="h-3 w-1/4 bg-gray-800 rounded" />
                   <div className="h-3 w-1/2 bg-gray-800 rounded" />
                 </div>
              </div>
            )}
            
            <div ref={scrollRef} className="h-4" />
          </div>
        )}
      </div>

      {/* Input Area */}
      <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-gray-950 via-gray-950/90 to-transparent pt-12">
        <ChatInput 
          onSend={(val) => sendMessage(val, selectedDocumentIds)} 
          onStop={stopGeneration}
          isStreaming={isStreaming}
        />
      </div>

      <CitationViewer
        isOpen={!!activeCitation}
        onClose={() => setActiveCitation(null)}
        url={activeCitation ? `${API_CONFIG.BASE_URL}/documents/${activeCitation.document_id}/view` : ''}
        title={activeCitation?.document_title || 'Document View'}
        initialPage={activeCitation?.start_page || 1}
      />
    </div>
  );
};

export default ChatWindow;
