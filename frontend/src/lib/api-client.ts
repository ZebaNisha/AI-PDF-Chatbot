import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { API_CONFIG, AUTH_KEYS } from '@/config/constants';
import { useAuthStore } from '@/store/useAuthStore';

/**
 * Standardized API error structure.
 */
export interface ApiError {
  message: string;
  status?: number;
  code?: string;
  detail?: any;
}

const apiClient = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT,
  headers: API_CONFIG.HEADERS,
});

/**
 * Request Interceptor: Attach JWT token if available.
 */
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = typeof window !== 'undefined' ? localStorage.getItem(AUTH_KEYS.ACCESS_TOKEN) : null;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

/**
 * Response Interceptor: Handle auth failures and standardized error parsing.
 */
apiClient.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const originalRequest = error.config;
    
    // Handle 401 Unauthorized (Expired or Invalid Token)
    if (error.response?.status === 401 && !originalRequest?.url?.includes('/login')) {
      // Future: Implement token refresh logic here
      if (typeof window !== 'undefined') {
        useAuthStore.getState().clearAuth();
        
        // Redirect to login if not already there
        if (window.location.pathname !== '/login') {
          window.location.href = '/login';
        }
      }
    }

    const apiError: ApiError = {
      message: (error.response?.data as any)?.detail || error.message || 'An unexpected error occurred',
      status: error.response?.status,
      code: (error.response?.data as any)?.code,
      detail: (error.response?.data as any)?.detail,
    };

    return Promise.reject(apiError);
  }
);

export default apiClient;
