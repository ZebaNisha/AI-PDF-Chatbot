import apiClient from '@/lib/api-client';
import { AuthResponse, User } from '@/types';
import { useAuthStore } from '@/store/useAuthStore';

/**
 * Service for handling authentication API interactions.
 */
export class AuthService {
  /**
   * Log in a user and persist the session.
   */
  static async login(credentials: Record<string, string>): Promise<AuthResponse> {
    const formData = new URLSearchParams();
    formData.append('username', credentials.email);
    formData.append('password', credentials.password);

    const res = await apiClient.post<AuthResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    const { user, access_token } = res.data;
    
    // Update store
    useAuthStore.getState().setAuth(user, access_token);
    
    return res.data;
  }

  /**
   * Register a new user.
   */
  static async register(data: Record<string, string>): Promise<AuthResponse> {
    const res = await apiClient.post<AuthResponse>('/auth/register', data);
    const { user, access_token } = res.data;
    
    // Update store
    useAuthStore.getState().setAuth(user, access_token);
    
    return res.data;
  }

  /**
   * Get the current user profile using the stored token.
   */
  static async getMe(): Promise<User> {
    const res = await apiClient.get<User>('/auth/me');
    
    // Update store
    useAuthStore.getState().setAuth(res.data, localStorage.getItem('access_token') || '');
    
    return res.data;
  }

  /**
   * Log out and clear the session.
   */
  static async logout(): Promise<void> {
    // Optional: Call backend to invalidate token
    useAuthStore.getState().clearAuth();
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
  }
}
