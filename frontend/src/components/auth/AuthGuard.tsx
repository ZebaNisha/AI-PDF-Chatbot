'use client';

import React, { useEffect } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuthStore } from '@/store/useAuthStore';
import { AuthService } from '@/features/auth/services/auth.service';
import { ROUTES, AUTH_KEYS } from '@/config/constants';
import LoadingOverlay from '../shared/LoadingOverlay';

interface Props {
  children: React.ReactNode;
}

/**
 * Route protection system.
 * Redirects unauthenticated users to login for protected routes,
 * and authenticated users to dashboard for public routes (login/register).
 */
const AuthGuard: React.FC<Props> = ({ children }) => {
  const { isAuthenticated, isLoading, setLoading, clearAuth } = useAuthStore();
  const router = useRouter();
  const pathname = usePathname();

  // Initial Session Check
  useEffect(() => {
    const initAuth = async () => {
      const token = typeof window !== 'undefined' ? localStorage.getItem(AUTH_KEYS.ACCESS_TOKEN) : null;
      
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        await AuthService.getMe();
      } catch (error) {
        console.error('Session validation failed:', error);
        clearAuth();
      } finally {
        setLoading(false);
      }
    };

    initAuth();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (isLoading) return;

    const isPublicRoute = Object.values(ROUTES.PUBLIC).includes(pathname);
    const isProtectedRoute = Object.values(ROUTES.PROTECTED).includes(pathname) || pathname === '/';

    if (!isAuthenticated && isProtectedRoute) {
      router.push(ROUTES.PUBLIC.LOGIN);
    } else if (isAuthenticated && isPublicRoute) {
      router.push(ROUTES.PROTECTED.DASHBOARD);
    }
  }, [isAuthenticated, isLoading, pathname, router]);

  if (isLoading) {
    return <LoadingOverlay fullScreen message="Checking session..." />;
  }

  // To prevent flash of content, we could add more logic here,
  // but for now, we just return the children.
  return <>{children}</>;
};

export default AuthGuard;
