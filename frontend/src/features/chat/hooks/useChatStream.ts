import { useState, useRef, useCallback, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import { ChatMessage, Citation, ChatStreamDelta } from '@/types';
import { ChatService } from '../services/chat.service';
import { notify } from '@/lib/notifications';

/**
 * Custom hook to manage the lifecycle and state of a streaming RAG chat.
 */
export function useChatStream(sessionId: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [currentResponse, setCurrentResponse] = useState('');
  const abortControllerRef = useRef<AbortController | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const isAutoScrollEnabled = useRef(true);

  // Auto-scroll logic
  const scrollToBottom = useCallback((force = false) => {
    if (force || isAutoScrollEnabled.current) {
      scrollRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
  }, []);

  // Detect manual scroll up to disable auto-scroll
  const handleScroll = useCallback((e: React.UIEvent<HTMLDivElement>) => {
    const { scrollTop, scrollHeight, clientHeight } = e.currentTarget;
    const isAtBottom = scrollHeight - scrollTop <= clientHeight + 50;
    isAutoScrollEnabled.current = isAtBottom;
  }, []);

  const sendMessage = useCallback(async (query: string, documentIds?: string[]) => {
    if (isStreaming) return;

    const userMessage: ChatMessage = {
      id: uuidv4(),
      role: 'user',
      content: query,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setIsStreaming(true);
    setCurrentResponse('');
    isAutoScrollEnabled.current = true;

    const abortController = new AbortController();
    abortControllerRef.current = abortController;

    try {
      const stream = await ChatService.streamChat(query, sessionId, documentIds, abortController.signal);
      const reader = stream.getReader();
      
      let fullContent = '';
      let citations: Citation[] = [];

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        if (value.delta) {
          fullContent += value.delta;
          // Throttled UI update (batching)
          setCurrentResponse(fullContent);
          scrollToBottom();
        }

        if (value.is_final && value.citations) {
          citations = value.citations;
        }

        if (value.error) {
          throw new Error(value.error);
        }
      }

      const assistantMessage: ChatMessage = {
        id: uuidv4(),
        role: 'assistant',
        content: fullContent,
        citations,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setCurrentResponse('');

    } catch (error: any) {
      if (error.name === 'AbortError') {
        notify.success('Generation stopped');
      } else {
        notify.error(error.message || 'Failed to generate response');
      }
    } finally {
      setIsStreaming(false);
      abortControllerRef.current = null;
    }
  }, [isStreaming, sessionId, scrollToBottom]);

  const stopGeneration = useCallback(() => {
    abortControllerRef.current?.abort();
  }, []);

  return {
    messages,
    setMessages,
    isStreaming,
    currentResponse,
    sendMessage,
    stopGeneration,
    scrollRef,
    handleScroll,
  };
}
