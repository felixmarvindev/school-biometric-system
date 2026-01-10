/**
 * JWT token utilities.
 * 
 * Note: This only decodes the token payload (without verification).
 * Token verification should be done on the backend.
 */

/**
 * Decode JWT token payload without verification.
 * 
 * @param token - JWT token string
 * @returns Decoded payload or null if invalid
 */
export function decodeJwtPayload<T = Record<string, unknown>>(token: string): T | null {
  try {
    // JWT tokens have 3 parts: header.payload.signature
    const parts = token.split('.');
    if (parts.length !== 3) {
      return null;
    }
    
    // Decode the payload (second part)
    const payload = parts[1];
    
    // Base64 URL decode
    const decoded = atob(payload.replace(/-/g, '+').replace(/_/g, '/'));
    
    // Parse JSON
    return JSON.parse(decoded) as T;
  } catch (error) {
    console.error('Failed to decode JWT token:', error);
    return null;
  }
}

/**
 * Get user ID from JWT token.
 */
export function getUserIdFromToken(token: string): number | null {
  const payload = decodeJwtPayload<{ sub?: string }>(token);
  if (!payload || !payload.sub) {
    return null;
  }
  return parseInt(payload.sub, 10) || null;
}

/**
 * Get email from JWT token.
 */
export function getEmailFromToken(token: string): string | null {
  const payload = decodeJwtPayload<{ email?: string }>(token);
  return payload?.email || null;
}

/**
 * Get school ID from JWT token.
 */
export function getSchoolIdFromToken(token: string): number | null {
  const payload = decodeJwtPayload<{ school_id?: number }>(token);
  return payload?.school_id || null;
}

/**
 * Get role from JWT token.
 */
export function getRoleFromToken(token: string): string | null {
  const payload = decodeJwtPayload<{ role?: string }>(token);
  return payload?.role || null;
}

/**
 * Get first name from JWT token.
 */
export function getFirstNameFromToken(token: string): string | null {
  const payload = decodeJwtPayload<{ first_name?: string }>(token);
  return payload?.first_name || null;
}

/**
 * Get last name from JWT token.
 */
export function getLastNameFromToken(token: string): string | null {
  const payload = decodeJwtPayload<{ last_name?: string }>(token);
  return payload?.last_name || null;
}

/**
 * JWT token expiration payload structure.
 */
interface JwtExpirationPayload {
  exp?: number; // Expiration time (Unix timestamp)
  iat?: number; // Issued at (Unix timestamp)
}

/**
 * Check if JWT token is expired.
 * 
 * @param token - JWT token string
 * @param bufferSeconds - Optional buffer time in seconds before expiration (default: 0)
 * @returns true if token is expired or will expire within buffer time, false otherwise
 */
export function isTokenExpired(token: string, bufferSeconds: number = 0): boolean {
  const payload = decodeJwtPayload<JwtExpirationPayload>(token);
  
  if (!payload || !payload.exp) {
    // If no expiration claim, consider token invalid
    return true;
  }
  
  // exp is Unix timestamp (seconds), Date.now() is milliseconds
  const expirationTime = payload.exp * 1000; // Convert to milliseconds
  const currentTime = Date.now();
  const bufferTime = bufferSeconds * 1000; // Convert buffer to milliseconds
  
  // Token is expired if current time >= (expiration time - buffer)
  return currentTime >= (expirationTime - bufferTime);
}

/**
 * Get token expiration time.
 * 
 * @param token - JWT token string
 * @returns Expiration Date object or null if expiration not found
 */
export function getTokenExpiration(token: string): Date | null {
  const payload = decodeJwtPayload<JwtExpirationPayload>(token);
  
  if (!payload || !payload.exp) {
    return null;
  }
  
  // exp is Unix timestamp (seconds), convert to milliseconds
  return new Date(payload.exp * 1000);
}

/**
 * Get time until token expiration in milliseconds.
 * 
 * @param token - JWT token string
 * @returns Milliseconds until expiration, or null if expiration not found or already expired
 */
export function getTimeUntilExpiration(token: string): number | null {
  const expiration = getTokenExpiration(token);
  
  if (!expiration) {
    return null;
  }
  
  const timeUntilExpiration = expiration.getTime() - Date.now();
  
  // Return null if already expired
  return timeUntilExpiration > 0 ? timeUntilExpiration : null;
}