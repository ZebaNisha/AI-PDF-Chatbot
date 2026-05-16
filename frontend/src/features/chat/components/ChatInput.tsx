'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Square, AlertCircle } from 'lucide-react';
import { clsx } from 'clsx';

interface Props {
  onSend: (message: string) => void;
  onStop: () => void;
  isStreaming: boolean;
  disabled?: boolean;
}

const MAX_TOKENS_ESTIMATE = 4000;

const ChatInput: React.FC<Props> = ({ onSend, onStop, isStreaming, disabled }) => {
  const [input, setInput] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 200)}px`;
    }
  }, [input]);

  const handleSend = () => {
    if (input.trim() && !disabled) {
      onSend(input.trim());
      setInput('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    } else if (e.key === 'Escape' && isStreaming) {
      onStop();
    }
  };

  // Simple token estimate (4 chars ~ 1 token)
  const isNearLimit = input.length > MAX_TOKENS_ESTIMATE * 3;

  return (
    <div className="relative w-full max-w-4xl mx-auto px-4 pb-8">
      <div className={clsx(
        "relative flex items-end gap-2 p-2 bg-gray-900/80 backdrop-blur-xl border rounded-2xl transition-all duration-300 shadow-2xl",
        isStreaming ? "border-blue-500/30 ring-1 ring-blue-500/10" : "border-gray-800 focus-within:border-gray-700 focus-within:ring-1 focus-within:ring-gray-700/50"
      )}>
        <textarea
          ref={textareaRef}
          rows={1}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about your documents..."
          className="flex-1 max-h-[200px] bg-transparent border-none focus:ring-0 text-gray-200 placeholder-gray-500 resize-none py-3 px-4 text-sm leading-relaxed scrollbar-hide"
          disabled={disabled}
        />

        <div className="flex items-center gap-2 pr-2 pb-1.5">
          {isStreaming ? (
            <button
              onClick={onStop}
              className="p-2.5 bg-gray-800 hover:bg-gray-700 text-red-400 rounded-xl transition-all active:scale-95 group"
              title="Stop generation (Esc)"
            >
              <Square className="h-4 w-4 fill-current" />
            </button>
          ) : (
            <button
              onClick={handleSend}
              disabled={!input.trim() || disabled}
              className={clsx(
                "p-2.5 rounded-xl transition-all active:scale-95",
                input.trim() && !disabled
                  ? "bg-blue-600 hover:bg-blue-500 text-white shadow-lg shadow-blue-600/20"
                  : "bg-gray-800 text-gray-600 cursor-not-allowed"
              )}
            >
              <Send className="h-4 w-4" />
            </button>
          )}
        </div>

        {isNearLimit && (
          <div className="absolute -top-8 left-2 flex items-center gap-1.5 text-[10px] text-amber-500 animate-in fade-in slide-in-from-bottom-1">
            <AlertCircle className="h-3 w-3" />
            Query is becoming very long
          </div>
        )}
      </div>
      
      <p className="mt-3 text-center text-[10px] text-gray-600 uppercase tracking-widest font-medium">
        Powered by AI RAG Engine • {isStreaming ? 'Generating response...' : 'Ready'}
      </p>
    </div>
  );
};

export default ChatInput;
