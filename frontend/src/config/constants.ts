/**
 * Global application constants and configuration.
 */

export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  TIMEOUT: 30000, // 30 seconds
  HEADERS: {
    'Content-Type': 'application/json',
  },
};

export const ROUTES = {
  PUBLIC: {
    LOGIN: '/login',
    REGISTER: '/register',
  },
  PROTECTED: {
    DASHBOARD: '/',
    CHAT: '/chat',
    DOCUMENTS: '/documents',
    SETTINGS: '/settings',
  },
};

export const AUTH_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
};

export const CHAT_CONFIG = {
  MAX_HISTORY: 20,
  STREAM_TIMEOUT: 60000,
};

export const FILE_CONFIG = {
  MAX_SIZE_MB: 50,
  ALLOWED_TYPES: ['application/pdf'],
};
