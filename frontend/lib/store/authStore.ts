/**
 * Authentication state management using Zustand.
 * 
 * Manages:
 * - JWT token storage (localStorage)
 * - User authentication state
 * - Login/logout functionality
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { UserResponse } from '@/lib/api/auth';

interface AuthState {
  token: string | null;
  user: UserResponse | null;
  isAuthenticated: boolean;
  login: (token: string, user: UserResponse) => void;
  logout: () => void;
  setUser: (user: UserResponse) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      
      login: (token: string, user: UserResponse) => {
        set({
          token,
          user,
          isAuthenticated: true,
        });
      },
      
      logout: () => {
        set({
          token: null,
          user: null,
          isAuthenticated: false,
        });
      },
      
      setUser: (user: UserResponse) => {
        set({ user });
      },
    }),
    {
      name: 'auth-storage', // localStorage key
      partialize: (state) => ({
        token: state.token,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

