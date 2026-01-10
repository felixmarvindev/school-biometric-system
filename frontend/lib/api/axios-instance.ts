/**
 * Axios configuration with global interceptors for authentication.
 * 
 * Features:
 * - Automatic token injection in requests
 * - Automatic logout on 401 (Unauthorized) responses
 * - Token expiration checking
 * - Centralized error handling
 * 
 * This sets up global axios defaults and interceptors that apply to ALL axios requests,
 * including those made directly with `axios.get()`, `axios.post()`, etc.
 */

import axios, { AxiosError, InternalAxiosRequestConfig } from 'axios';
import { useAuthStore } from '@/lib/store/authStore';
import { isTokenExpired } from '@/lib/utils/jwt';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

// Set axios default base URL (used by all axios requests)
axios.defaults.baseURL = API_BASE_URL;
axios.defaults.timeout = 30000; // 30 seconds
axios.defaults.headers.common['Content-Type'] = 'application/json';

/**
 * Handle automatic logout when session expires.
 * This function is called from interceptors and can be called from anywhere.
 */
function handleSessionExpiration(message: string = 'Your session has expired. Please log in again.'): void {
  // Only run on client side
  if (typeof window === 'undefined') {
    return;
  }

  const authStore = useAuthStore.getState();
  
  // Only logout if user is actually authenticated
  if (authStore.isAuthenticated && authStore.token) {
    // Clear authentication state
    authStore.logout();
    
    // Store message for display after redirect (using sessionStorage which clears on tab close)
    if (message) {
      sessionStorage.setItem('session_expired_message', message);
    }
    
    // Redirect to login page
    window.location.href = '/login';
  }
}

/**
 * Global request interceptor: Add authentication token to ALL requests.
 * This applies to all axios requests made anywhere in the app.
 */
axios.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    // Only run on client side
    if (typeof window === 'undefined') {
      return config;
    }

    const authStore = useAuthStore.getState();
    const token = authStore.token;

    // Check if token exists and is not expired before adding to request
    if (token) {
      // Check token expiration (with 5 second buffer to account for network delay)
      if (isTokenExpired(token, 5)) {
        // Token is expired, trigger logout
        handleSessionExpiration('Your session has expired. Please log in again.');
        // Cancel the request
        return Promise.reject(new Error('Token expired'));
      }

      // Add token to Authorization header (only if not already set)
      if (!config.headers.Authorization) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }

    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

/**
 * Global response interceptor: Handle 401 (Unauthorized) responses and token expiration.
 * This applies to all axios responses from anywhere in the app.
 */
axios.interceptors.response.use(
  (response) => {
    // Successful response, return as-is
    return response;
  },
  (error: AxiosError) => {
    // Only run on client side
    if (typeof window === 'undefined') {
      return Promise.reject(error);
    }

    // Handle 401 Unauthorized (token expired or invalid)
    if (error.response?.status === 401) {
      // Only handle 401 if it's not from the login endpoint (to avoid logout loop)
      const url = error.config?.url || '';
      if (!url.includes('/auth/login')) {
        handleSessionExpiration('Your session has expired. Please log in again.');
      }
      return Promise.reject(error);
    }

    // Handle network errors
    if (!error.response) {
      // Could be network error, timeout, etc.
      // Let the calling code handle it
      return Promise.reject(error);
    }

    // For other errors, reject as-is
    return Promise.reject(error);
  }
);

/**
 * Export axios for use in API modules.
 * All axios requests will automatically include the auth token and handle 401 responses.
 * 
 * Usage:
 * ```typescript
 * import axios from 'axios';
 * 
 * const response = await axios.get('/api/v1/endpoint');
 * // Token is automatically added, 401 automatically handled
 * ```
 */
export default axios;
