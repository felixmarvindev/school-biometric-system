/**
 * Hook for periodic session/token expiration checking.
 * 
 * This hook checks token expiration periodically and automatically logs out
 * the user if the token is expired or about to expire.
 */

import { useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/lib/store/authStore';
import { isTokenExpired, getTimeUntilExpiration } from '@/lib/utils/jwt';
import { toast } from 'sonner';

interface UseSessionCheckOptions {
  /**
   * How often to check token expiration (in milliseconds).
   * Default: 60000 (1 minute)
   */
  checkInterval?: number;
  
  /**
   * Buffer time in seconds before expiration to show warning.
   * Default: 300 (5 minutes)
   */
  warningBufferSeconds?: number;
  
  /**
   * Buffer time in seconds before expiration to log out.
   * Default: 0 (log out at expiration)
   */
  logoutBufferSeconds?: number;
  
  /**
   * Whether to show warning toast when token is about to expire.
   * Default: true
   */
  showWarning?: boolean;
}

/**
 * Hook to periodically check token expiration and handle automatic logout.
 * 
 * @param options - Configuration options
 * @returns void
 * 
 * @example
 * ```tsx
 * function DashboardLayout() {
 *   useSessionCheck({
 *     checkInterval: 60000, // Check every minute
 *     warningBufferSeconds: 300, // Show warning 5 minutes before expiration
 *   });
 *   // ...
 * }
 * ```
 */
export function useSessionCheck(options: UseSessionCheckOptions = {}): void {
  const router = useRouter();
  const {
    checkInterval = 60000, // 1 minute default
    warningBufferSeconds = 300, // 5 minutes warning
    logoutBufferSeconds = 0, // No buffer for logout (expire exactly at expiration)
    showWarning = true,
  } = options;

  const warningShownRef = useRef(false);
  const { token, isAuthenticated, logout } = useAuthStore();

  useEffect(() => {
    // Only run on client side and if user is authenticated
    if (typeof window === 'undefined' || !isAuthenticated || !token) {
      return;
    }

    // Check token expiration immediately
    const checkTokenExpiration = () => {
      if (!token) {
        return;
      }

      // Check if token is expired (or will expire within logout buffer)
      if (isTokenExpired(token, logoutBufferSeconds)) {
        // Token expired, logout immediately
        logout();
        
        // Show expiration message
        toast.error('Your session has expired. Please log in again.', {
          duration: 5000,
        });
        
        // Redirect to login
        router.push('/login');
        return;
      }

      // Check if token is about to expire (within warning buffer)
      if (showWarning && !warningShownRef.current) {
        const timeUntilExpiration = getTimeUntilExpiration(token);
        
        if (timeUntilExpiration !== null && timeUntilExpiration <= warningBufferSeconds * 1000) {
          // Show warning (only once)
          warningShownRef.current = true;
          
          const minutesRemaining = Math.ceil(timeUntilExpiration / 60000);
          toast.warning(`Your session will expire in ${minutesRemaining} minute${minutesRemaining !== 1 ? 's' : ''}. Please save your work.`, {
            duration: 10000,
          });
        }
      }
    };

    // Check immediately
    checkTokenExpiration();

    // Set up periodic checking
    const intervalId = setInterval(checkTokenExpiration, checkInterval);

    // Cleanup on unmount
    return () => {
      clearInterval(intervalId);
    };
  }, [
    token,
    isAuthenticated,
    logout,
    router,
    checkInterval,
    warningBufferSeconds,
    logoutBufferSeconds,
    showWarning,
  ]);

  // Reset warning flag when token changes (new login)
  useEffect(() => {
    if (token) {
      warningShownRef.current = false;
    }
  }, [token]);
}
