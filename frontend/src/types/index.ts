/**
 * Authentication related types.
 */
export interface User {
  id: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

/**
 * Document related types.
 */
export enum DocumentStatus {
  PENDING = "PENDING",
  UPLOADED = "UPLOADED",
  EXTRACTING = "EXTRACTING",
  CHUNKING = "CHUNKING",
  EMBEDDING = "EMBEDDING",
  STORING = "STORING",
  COMPLETED = "COMPLETED",
  FAILED = "FAILED",
}

export interface Document {
  id: string;
  user_id: string;
  original_filename: string;
  stored_filename: string;
  storage_url?: string;
  file_size: number;
  mime_type: string;
  status: DocumentStatus;
  failure_reason?: string;
  processing_started_at?: string;
  processing_completed_at?: string;
  created_at: string;
  updated_at: string;
}

/**
 * Retrieval & Chat types.
 */
export interface Citation {
  document_id: string;
  document_title?: string;
  start_page: int;
  end_page: int;
  chunk_id: string;
}

export interface RetrievalResult {
  text: string;
  score: number;
  citation: Citation;
  chunk_index: number;
  token_count: number;
}

export interface ChatMessage {
  id: string;
  role: 'system' | 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  created_at: string;
}

export interface ChatStreamDelta {
  delta?: string;
  is_final: boolean;
  citations?: Citation[];
  error?: string;
}
