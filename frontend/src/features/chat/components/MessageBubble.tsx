'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { User, Bot, Copy, Check } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import DOMPurify from 'dompurify';

import { ChatMessage, Citation } from '@/types';
import CitationList from './CitationList';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface Props {
  message: ChatMessage | { role: 'assistant'; content: string; citations?: Citation[] };
  isStreaming?: boolean;
  onCitationClick?: (citation: Citation) => void;
}

const MessageBubble: React.FC<Props> = ({ message, isStreaming, onCitationClick }) => {
  const isAssistant = message.role === 'assistant';
  const [copied, setCopied] = React.useState(false);

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Sanitize content if it contains raw HTML (though react-markdown usually handles this)
  const sanitizedContent = typeof window !== 'undefined' ? DOMPurify.sanitize(message.content) : message.content;

  return (
    <div className={cn(
      "flex w-full gap-4 p-6 transition-colors duration-200",
      isAssistant ? "bg-gray-900/40 border-y border-gray-800/50" : "bg-transparent"
    )}>
      <div className="flex-shrink-0">
        <div className={cn(
          "flex h-9 w-9 items-center justify-center rounded-lg shadow-lg",
          isAssistant ? "bg-blue-600/20 text-blue-400 border border-blue-500/20" : "bg-purple-600/20 text-purple-400 border border-purple-500/20"
        )}>
          {isAssistant ? <Bot className="h-5 w-5" /> : <User className="h-5 w-5" />}
        </div>
      </div>

      <div className="flex-1 min-w-0 space-y-4">
        <div className="prose prose-invert prose-blue max-w-none break-words leading-relaxed">
          <ReactMarkdown
            remarkPlugins={[remarkGfm]}
            components={{
              code({ node, inline, className, children, ...props }: any) {
                const match = /language-(\w+)/.exec(className || '');
                const codeValue = String(children).replace(/\n$/, '');
                
                return !inline && match ? (
                  <div className="group relative my-4 rounded-xl overflow-hidden border border-gray-700/50 shadow-2xl">
                    <div className="flex items-center justify-between px-4 py-2 bg-gray-800/80 border-b border-gray-700/50">
                      <span className="text-xs font-mono text-gray-400 uppercase tracking-wider">{match[1]}</span>
                      <button
                        onClick={() => handleCopy(codeValue)}
                        className="p-1 hover:text-blue-400 transition-colors"
                        title="Copy code"
                      >
                        {copied ? <Check className="h-3.5 w-3.5" /> : <Copy className="h-3.5 w-3.5" />}
                      </button>
                    </div>
                    <SyntaxHighlighter
                      style={oneDark}
                      language={match[1]}
                      PreTag="div"
                      className="!m-0 !bg-gray-900/90 !p-4"
                      {...props}
                    >
                      {codeValue}
                    </SyntaxHighlighter>
                  </div>
                ) : (
                  <code className={cn("px-1.5 py-0.5 rounded-md bg-gray-800 text-blue-300 font-mono text-sm", className)} {...props}>
                    {children}
                  </code>
                );
              },
              p: ({ children }) => <p className="mb-4 last:mb-0 text-gray-200">{children}</p>,
              ul: ({ children }) => <ul className="mb-4 list-disc list-inside space-y-1 text-gray-200">{children}</ul>,
              ol: ({ children }) => <ol className="mb-4 list-decimal list-inside space-y-1 text-gray-200">{children}</ol>,
            }}
          >
            {sanitizedContent}
          </ReactMarkdown>
          
          {isStreaming && (
            <span className="inline-block h-4 w-1.5 bg-blue-500 animate-pulse ml-1 align-middle" />
          )}
        </div>

        {'citations' in message && message.citations && message.citations.length > 0 && (
          <div className="pt-2 animate-in fade-in slide-in-from-bottom-2 duration-500">
             <CitationList citations={message.citations} onCitationClick={onCitationClick} />
          </div>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
