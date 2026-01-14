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
  refreshToken: string | null;
  user: UserResponse | null;
  isAuthenticated: boolean;
  hasHydrated: boolean;
  login: (token: string, user: UserResponse, refreshToken?: string | null) => void;
  setTokens: (tokens: { accessToken: string; refreshToken?: string | null }) => void;
  logout: () => void;
  setUser: (user: UserResponse) => void;
  setHasHydrated: (hasHydrated: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      refreshToken: null,
      user: null,
      isAuthenticated: false,
      hasHydrated: false,
      
      login: (token: string, user: UserResponse, refreshToken?: string | null) => {
        set({
          token,
          refreshToken: refreshToken ?? null,
          user,
          isAuthenticated: true,
        });
      },

      setTokens: (tokens: { accessToken: string; refreshToken?: string | null }) => {
        set((state) => ({
          token: tokens.accessToken,
          refreshToken: tokens.refreshToken ?? state.refreshToken,
          isAuthenticated: true,
        }));
      },
      
      logout: () => {
        set({
          token: null,
          refreshToken: null,
          user: null,
          isAuthenticated: false,
        });
        // Clear localStorage (persist middleware handles this, but ensure it's cleared)
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth-storage');
        }
      },
      
      setUser: (user: UserResponse) => {
        set({ user });
      },
      
      setHasHydrated: (hasHydrated: boolean) => {
        set({ hasHydrated });
      },
    }),
    {
      name: 'auth-storage', // localStorage key
      partialize: (state) => ({
        token: state.token,
        refreshToken: state.refreshToken,
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
      onRehydrateStorage: () => (state, error) => {
        // This callback runs after rehydration is complete
        if (error) {
          console.error('Error rehydrating auth store:', error);
        }
        // Set hasHydrated to true after rehydration completes (whether successful or not)
        if (state) {
          state.setHasHydrated(true);
        } else {
          // If state is null, still mark as hydrated (no persisted data)
          // We need to access the store to set this
          setTimeout(() => {
            useAuthStore.getState().setHasHydrated(true);
          }, 0);
        }
      },
    }
  )
);

