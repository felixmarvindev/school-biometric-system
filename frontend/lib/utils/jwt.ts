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

