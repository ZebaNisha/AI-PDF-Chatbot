'use client';

import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Mail, Lock, User, Loader2, UserPlus, AlertCircle } from 'lucide-react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';

import { AuthService } from '../services/auth.service';
import { notify } from '@/lib/notifications';
import { ROUTES } from '@/config/constants';

const registerSchema = z.object({
  full_name: z.string().min(2, 'Name is too short'),
  email: z.string().email('Invalid email address'),
  password: z.string().min(8, 'Password must be at least 8 characters'),
  confirm_password: z.string(),
}).refine((data) => data.password === data.confirm_password, {
  message: "Passwords don't match",
  path: ["confirm_password"],
});

type RegisterFormValues = z.infer<typeof registerSchema>;

const RegisterForm: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<RegisterFormValues>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormValues) => {
    setIsLoading(true);
    try {
      await AuthService.register(data);
      notify.success('Account created successfully!');
      router.push(ROUTES.PROTECTED.DASHBOARD);
    } catch (error: any) {
      notify.error(error.message || 'Registration failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-md space-y-8 p-8 bg-gray-900/50 backdrop-blur-xl rounded-3xl border border-gray-800 shadow-2xl animate-in fade-in slide-in-from-bottom-4 duration-700">
      <div className="text-center">
        <div className="inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-purple-600/10 border border-purple-500/20 mb-6">
          <UserPlus className="h-6 w-6 text-purple-500" />
        </div>
        <h2 className="text-3xl font-bold text-white tracking-tight">Create Account</h2>
        <p className="mt-2 text-sm text-gray-400">Join the premium RAG chat experience</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="mt-8 space-y-5">
        <div className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 ml-1">Full Name</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-500">
                <User className="h-4 w-4" />
              </div>
              <input
                {...register('full_name')}
                className="block w-full pl-11 pr-4 py-3 bg-gray-800/50 border border-gray-700 rounded-xl focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500 text-white placeholder-gray-500 transition-all outline-none"
                placeholder="John Doe"
              />
            </div>
            {errors.full_name && (
              <p className="mt-1.5 ml-1 flex items-center gap-1.5 text-xs text-red-500 font-medium animate-in fade-in slide-in-from-left-1">
                <AlertCircle className="h-3 w-3" />
                {errors.full_name.message}
              </p>
            )}
          </div>

          <div>
            <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 ml-1">Email Address</label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-500">
                <Mail className="h-4 w-4" />
              </div>
              <input
                {...register('email')}
                type="email"
                className="block w-full pl-11 pr-4 py-3 bg-gray-800/50 border border-gray-700 rounded-xl focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500 text-white placeholder-gray-500 transition-all outline-none"
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

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 ml-1">Password</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-500">
                  <Lock className="h-4 w-4" />
                </div>
                <input
                  {...register('password')}
                  type="password"
                  className="block w-full pl-11 pr-4 py-3 bg-gray-800/50 border border-gray-700 rounded-xl focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500 text-white placeholder-gray-500 transition-all outline-none"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2 ml-1">Confirm</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-gray-500">
                  <Lock className="h-4 w-4" />
                </div>
                <input
                  {...register('confirm_password')}
                  type="password"
                  className="block w-full pl-11 pr-4 py-3 bg-gray-800/50 border border-gray-700 rounded-xl focus:ring-2 focus:ring-purple-500/20 focus:border-purple-500 text-white placeholder-gray-500 transition-all outline-none"
                  placeholder="••••••••"
                />
              </div>
            </div>
            
            {(errors.password || errors.confirm_password) && (
              <p className="col-span-2 mt-1.5 ml-1 flex items-center gap-1.5 text-xs text-red-500 font-medium animate-in fade-in slide-in-from-left-1">
                <AlertCircle className="h-3 w-3" />
                {errors.password?.message || errors.confirm_password?.message}
              </p>
            )}
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading}
          className="relative group w-full flex justify-center py-3 px-4 border border-transparent rounded-xl text-sm font-bold text-white bg-purple-600 hover:bg-purple-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-purple-500 transition-all active:scale-[0.98] disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-purple-600/20 mt-4"
        >
          {isLoading ? (
            <Loader2 className="h-5 w-5 animate-spin" />
          ) : (
            'Create Account'
          )}
        </button>

        <div className="text-center text-sm text-gray-500 mt-6">
          Already have an account?{' '}
          <Link href={ROUTES.PUBLIC.LOGIN} className="font-bold text-purple-500 hover:text-purple-400 transition-colors">
            Login
          </Link>
        </div>
      </form>
    </div>
  );
};

export default RegisterForm;
