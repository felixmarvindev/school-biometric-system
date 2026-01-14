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

  /**
   * Only auto-logout after this period of inactivity (in milliseconds).
   * Default: 300000 (5 minutes)
   */
  idleTimeoutMs?: number;

  /**
   * How often to record activity (in milliseconds). Prevents excessive writes.
   * Default: 1000 (1 second)
   */
  activityThrottleMs?: number;
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
    idleTimeoutMs = 300000, // 5 minutes idle before auto logout
    activityThrottleMs = 1000,
  } = options;

  const warningShownRef = useRef(false);
  const expiredToastShownRef = useRef(false);
  const lastActivityRef = useRef<number>(Date.now());
  const lastActivityWriteRef = useRef<number>(0);
  const { token, isAuthenticated, logout } = useAuthStore();

  useEffect(() => {
    // Only run on client side and if user is authenticated
    if (typeof window === 'undefined' || !isAuthenticated || !token) {
      return;
    }

    const ACTIVITY_KEY = 'last_activity_at';

    const recordActivity = () => {
      const now = Date.now();
      lastActivityRef.current = now;

      // Throttle localStorage writes
      if (now - lastActivityWriteRef.current < activityThrottleMs) {
        return;
      }
      lastActivityWriteRef.current = now;

      try {
        localStorage.setItem(ACTIVITY_KEY, String(now));
      } catch {
        // Ignore storage errors (private mode, quota, etc.)
      }
    };

    const readLastActivity = (): number => {
      try {
        const raw = localStorage.getItem(ACTIVITY_KEY);
        const parsed = raw ? Number(raw) : NaN;
        if (!Number.isFinite(parsed)) {
          return lastActivityRef.current;
        }
        return parsed;
      } catch {
        return lastActivityRef.current;
      }
    };

    // Initialize activity timestamp + attach listeners
    recordActivity();
    const activityEvents: Array<keyof WindowEventMap> = [
      'mousemove',
      'mousedown',
      'keydown',
      'scroll',
      'touchstart',
      'click',
    ];
    activityEvents.forEach((evt) => window.addEventListener(evt, recordActivity, { passive: true }));

    // Check token expiration immediately
    const checkTokenExpiration = () => {
      if (!token) {
        return;
      }

      // Check if token is expired (or will expire within logout buffer)
      if (isTokenExpired(token, logoutBufferSeconds)) {
        const now = Date.now();
        const lastActivity = readLastActivity();
        const idleForMs = Math.max(0, now - lastActivity);

        // Only auto-logout after idle timeout
        if (idleForMs >= idleTimeoutMs) {
          logout();
          toast.error('Your session has expired. Please log in again.', { duration: 5000 });
          router.push('/login');
          return;
        }

        // Token is expired but user is active; warn once and wait for inactivity
        if (!expiredToastShownRef.current) {
          expiredToastShownRef.current = true;
          toast.warning(
            'Your session has expired. You will be logged out after a period of inactivity.',
            { duration: 8000 }
          );
        }
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
      activityEvents.forEach((evt) => window.removeEventListener(evt, recordActivity));
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
    idleTimeoutMs,
    activityThrottleMs,
  ]);

  // Reset warning flag when token changes (new login)
  useEffect(() => {
    if (token) {
      warningShownRef.current = false;
      expiredToastShownRef.current = false;
    }
  }, [token]);
}
