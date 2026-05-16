import { API_CONFIG, AUTH_KEYS } from '@/config/constants';
import { ChatStreamDelta } from '@/types';

/**
 * Service for handling complex streaming chat interactions.
 * Uses native fetch for reliable readable stream processing.
 */
export class ChatService {
  /**
   * Execute a streaming RAG chat request.
   */
  static async streamChat(
    query: string,
    sessionId: string,
    documentIds?: string[],
    signal?: AbortSignal
  ): Promise<ReadableStream<ChatStreamDelta>> {
    const token = localStorage.getItem(AUTH_KEYS.ACCESS_TOKEN);

    const response = await fetch(`${API_CONFIG.BASE_URL}/chat/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        query,
        session_id: sessionId,
        document_ids: documentIds,
        stream: true,
      }),
      signal,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(errorData.detail || 'Failed to start chat stream');
    }

    if (!response.body) {
      throw new Error('Response body is empty');
    }

    return response.body.pipeThrough(new TextDecoderStream()).pipeThrough(
      new TransformStream({
        transform(chunk, controller) {
          // Backend sends NDJSON or server-sent events
          // We'll parse the raw chunk here
          const lines = chunk.split('\n');
          for (const line of lines) {
            const trimmedLine = line.trim();
            if (!trimmedLine) continue;

            // Handle SSE "data: " prefix
            if (trimmedLine.startsWith('data: ')) {
              const jsonStr = trimmedLine.replace('data: ', '');
              try {
                const data: ChatStreamDelta = JSON.parse(jsonStr);
                controller.enqueue(data);
              } catch (e) {
                console.error('Failed to parse stream chunk:', jsonStr);
              }
            }
          }
        },
      })
    );
  }
}
