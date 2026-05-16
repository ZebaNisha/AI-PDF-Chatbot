'use client';

import React, { useEffect, useState, useRef } from 'react';
import { useRouter, usePathname } from 'next/navigation';
import { useAuthStore } from '@/store/useAuthStore';
import { AuthService } from '@/features/auth/services/auth.service';
import { ROUTES, AUTH_KEYS } from '@/config/constants';
import LoadingOverlay from '../shared/LoadingOverlay';

interface Props {
  children: React.ReactNode;
}

const LOADING_MESSAGES = [
  "Waking up the digital librarians...",
  "Scanning the matrix for your session...",
  "Bribing the servers with virtual cookies...",
  "Teaching the AI some manners...",
];

const AuthGuard: React.FC<Props> = ({ children }) => {
  const { isAuthenticated, isLoading, setLoading, clearAuth } = useAuthStore();
  const router = useRouter();
  const pathname = usePathname();
  const [mounted, setMounted] = useState(false);
  const [loadingMessage, setLoadingMessage] = useState(LOADING_MESSAGES[0]);
  
  // Track redirects to prevent infinite loops
  const redirectCount = useRef(0);
  const lastRedirectPath = useRef<string | null>(null);

  useEffect(() => {
    setMounted(true);
    
    const initAuth = async () => {
      const token = typeof window !== 'undefined' ? localStorage.getItem(AUTH_KEYS.ACCESS_TOKEN) : null;
      console.log('[AuthGuard] Initializing. Token found:', !!token);
      
      // CRITICAL: If no token, we are NOT authenticated. Period.
      if (!token) {
        console.log('[AuthGuard] No token found. Forcing clearAuth and redirect to login.');
        clearAuth();
        setLoading(false);
        return;
      }

      try {
        await AuthService.getMe();
        console.log('[AuthGuard] Session validated successfully');
      } catch (error) {
        console.error('[AuthGuard] Session validation failed:', error);
        clearAuth();
      } finally {
        setLoading(false);
      }
    };

    initAuth();
  }, []);

  useEffect(() => {
    if (!mounted || isLoading) return;

    const isPublicRoute = Object.values(ROUTES.PUBLIC).includes(pathname || '');
    const isProtectedRoute = Object.values(ROUTES.PROTECTED).includes(pathname || '') || pathname === '/';

    console.log('[AuthGuard] Logic Check:', { 
        pathname, 
        isAuthenticated, 
        isPublicRoute, 
        isProtectedRoute 
    });

    if (!isAuthenticated && isProtectedRoute) {
      if (pathname !== ROUTES.PUBLIC.LOGIN) {
        if (lastRedirectPath.current === ROUTES.PUBLIC.LOGIN && redirectCount.current > 5) {
            console.error('[AuthGuard] Infinite Loop Detected! Stopping redirect.');
            return;
        }
        console.log('[AuthGuard] Redirecting to LOGIN');
        lastRedirectPath.current = ROUTES.PUBLIC.LOGIN;
        redirectCount.current++;
        router.replace(ROUTES.PUBLIC.LOGIN);
      }
    } else if (isAuthenticated && isPublicRoute) {
      if (pathname !== ROUTES.PROTECTED.DASHBOARD) {
        if (lastRedirectPath.current === ROUTES.PROTECTED.DASHBOARD && redirectCount.current > 5) {
            console.error('[AuthGuard] Infinite Loop Detected! Stopping redirect.');
            return;
        }
        console.log('[AuthGuard] Redirecting to DASHBOARD');
        lastRedirectPath.current = ROUTES.PROTECTED.DASHBOARD;
        redirectCount.current++;
        router.replace(ROUTES.PROTECTED.DASHBOARD);
      }
    } else {
      redirectCount.current = 0;
      lastRedirectPath.current = null;
    }
  }, [isAuthenticated, isLoading, pathname, mounted, router]);

  if (!mounted || (isLoading && !isAuthenticated)) {
    return <LoadingOverlay fullScreen message={loadingMessage} />;
  }

  return <>{children}</>;
};

export default AuthGuard;
