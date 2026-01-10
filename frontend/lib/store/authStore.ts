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
  hasHydrated: boolean;
  login: (token: string, user: UserResponse) => void;
  logout: () => void;
  setUser: (user: UserResponse) => void;
  setHasHydrated: (hasHydrated: boolean) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      isAuthenticated: false,
      hasHydrated: false,
      
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

