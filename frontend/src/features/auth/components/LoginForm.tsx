'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Mail, Lock, Loader2, LogIn, AlertCircle } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

import { AuthService } from '../services/auth.service';
import { notify } from '@/lib/notifications';
import { ROUTES } from '@/config/constants';

const loginSchema = z.object({
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
});

type LoginFormValues = z.infer<typeof loginSchema>;

const LoginForm: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginFormValues>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormValues) => {
    setIsLoading(true);
    try {
      await AuthService.login(data);
      notify.success('Welcome back!');
      router.push(ROUTES.PROTECTED.DASHBOARD);
    } catch (error: any) {
      notify.error(error.message || 'Login failed. Please check your credentials.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md space-y-8 p-8 bg-gray-900/50 backdrop-blur-xl rounded-3xl border border-gray-800 shadow-2xl animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="text-center">
        <div className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-600/10 border border-blue-500/20 mb-6">
          <LogIn className="h-6 w-6 text-blue-500" />
        </div>
        <h2 className="text-3xl font-bold text-white tracking-tight">Login</h2>
        <p className="mt-2 text-sm text-gray-400">Welcome back to AI PDF Chatbot</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-6">
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 ml-1">Email Address</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-500">
                <Mail className="h-4 w-4" />
              </div>
              <input
                {...register('email')}
                type="email"
                className="block w-full pl-11 pr-4 py-3 bg-gray-800/50 border border-gray-700 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-white placeholder-gray-500 transition-all outline-none"
                placeholder="you@example.com"
              />
            </div>
            {errors.email && (
              <p className="mt-1.5 ml-1 flex items-center gap-1.5 text-xs text-red-500 font-medium animate-in fade-in slide-in-from-left-1">
                <AlertCircle className="h-3 w-3" />
                {errors.email.message}
              </p>
            )}
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 ml-1">Password</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-500">
                <Lock className="h-4 w-4" />
              </div>
              <input
                {...register('password')}
                type="password"
                className="block w-full pl-11 pr-4 py-3 bg-gray-800/50 border border-gray-700 rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:border-blue-500 text-white placeholder-gray-500 transition-all outline-none"
                placeholder="••••••••"
              />
            </div>
            {errors.password && (
              <p className="mt-1.5 ml-1 flex items-center gap-1.5 text-xs text-red-500 font-medium animate-in fade-in slide-in-from-left-1">
                <AlertCircle className="h-3 w-3" />
                {errors.password.message}
              </p>
            )}
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="relative group w-full flex justify-center py-3 px-4 border border-transparent rounded-xl text-sm font-bold text-white bg-blue-600 hover:bg-blue-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-blue-600/20"
        >
          {isLoading ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            'Sign In'
          )}
        </button>

        <div className="text-center text-sm text-gray-500 mt-6">
          Don&apos;t have an account?{' '}
          <Link href={ROUTES.PUBLIC.REGISTER} className="font-bold text-blue-500 hover:text-blue-400 transition-colors">
            Register now
          </Link>
        </div>
      </form>
    </div>
  );
};

export default LoginForm;
