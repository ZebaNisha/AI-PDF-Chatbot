import apiClient from '@/lib/api-client';
import { Document } from '@/types';

/**
 * Service for handling document-related API interactions.
 */
export class DocumentService {
  /**
   * Upload a PDF document.
   */
  static async upload(file: File): Promise<Document> {
    const formData = new FormData();
    formData.append('file', file);

    const res = await apiClient.post<Document>('/documents/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return res.data;
  }

  /**
   * List all documents for the current user.
   */
  static async list(): Promise<Document[]> {
    const res = await apiClient.get<Document[]>('/documents');
    return res.data;
  }

  /**
   * Get a single document by ID (useful for polling).
   */
  static async get(id: string): Promise<Document> {
    const res = await apiClient.get<Document>(`/documents/${id}`);
    return res.data;
  }

  /**
   * Delete a document.
   */
  static async delete(id: string): Promise<void> {
    await apiClient.delete(`/documents/${id}`);
  }
}
