import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { User } from '@/types';
import { AUTH_KEYS } from '@/config/constants';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  
  // Actions
  setAuth: (user: User, token: string) => void;
  clearAuth: () => void;
  setLoading: (isLoading: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: true,

      setAuth: (user, token) => {
        if (typeof window !== 'undefined') {
          localStorage.setItem(AUTH_KEYS.ACCESS_TOKEN, token);
        }
        set({ user, isAuthenticated: true, isLoading: false });
      },

      clearAuth: () => {
        if (typeof window !== 'undefined') {
          localStorage.removeItem(AUTH_KEYS.ACCESS_TOKEN);
        }
        set({ user: null, isAuthenticated: false, isLoading: false });
      },

      setLoading: (isLoading) => set({ isLoading }),
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
);
