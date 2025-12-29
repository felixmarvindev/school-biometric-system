/**
 * API client functions for School management.
 * 
 * TODO: Implement API calls to the School Service via API Gateway.
 * 
 * Base URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
 * Endpoint: POST /api/v1/schools/register
 */

import axios from 'axios';
import type { SchoolRegistrationFormData } from '@/lib/validations/school';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Response type from the API after successful registration.
 */
export interface SchoolResponse {
  id: number;
  name: string;
  code: string; // Uppercase
  address: string | null;
  phone: string | null;
  email: string | null;
  is_deleted: boolean;
  created_at: string; // ISO datetime
  updated_at: string | null;
}

/**
 * API error response structure.
 */
export interface ApiError {
  detail: string | Array<{
    loc: (string | number)[];
    msg: string;
    type: string;
  }>;
}

/**
 * Custom error class for API errors with status code and details.
 */
export class SchoolRegistrationError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public fieldErrors?: Record<string, string>
  ) {
    super(message);
    this.name = 'SchoolRegistrationError';
  }
}

/**
 * Register a new school.
 * 
 * @param data - School registration data
 * @returns Promise resolving to the created school
 * @throws SchoolRegistrationError if registration fails
 * 
 * Comprehensive error handling:
 * - 400: Bad request (invalid data format)
 * - 422: Validation errors (returns fieldErrors map)
 * - 409: Duplicate code error
 * - 401/403: Authentication/authorization errors
 * - 500: Server error
 * - 502/503/504: Gateway/service unavailable errors
 * - Network errors: Connection/timeout/CORS errors
 */
export async function registerSchool(
  data: SchoolRegistrationFormData
): Promise<SchoolResponse> {
  try {
    const response = await axios.post<SchoolResponse>(
      `${API_BASE_URL}/api/v1/schools/register`,
      data,
      {
        headers: {
          'Content-Type': 'application/json',
        },
        timeout: 10000, // 10 second timeout
        validateStatus: (status) => status < 500, // Don't throw on 4xx errors
      }
    );
    
    // Check for error responses (4xx status codes)
    if (response.status >= 400) {
      const errorData = response.data as unknown as ApiError | undefined;
      const statusCode = response.status;
      
      // Handle 422 - Validation errors (most common)
      if (statusCode === 422 && errorData?.detail) {
        const fieldErrors: Record<string, string> = {};
        
        if (Array.isArray(errorData.detail)) {
          // FastAPI validation errors format: [{loc: ['body', 'field'], msg: 'error', type: 'type'}]
          errorData.detail.forEach((err) => {
            // Get the last element of loc array (field name)
            // Skip 'body' prefix if present
            const locArray = err.loc || [];
            const fieldIndex = locArray.findIndex((item, idx) => 
              idx > 0 && (typeof item === 'string' && item !== 'body')
            );
            const field = fieldIndex >= 0 
              ? String(locArray[fieldIndex])
              : String(locArray[locArray.length - 1]);
            
            if (field && field !== 'body') {
              // Map backend field names to frontend field names if needed
              const mappedField = mapBackendFieldToFrontend(field);
              fieldErrors[mappedField] = err.msg || 'Invalid value';
            }
          });
        } else if (typeof errorData.detail === 'string') {
          // Single string error message
          throw new SchoolRegistrationError(errorData.detail, statusCode);
        }
        
        const message = Object.keys(fieldErrors).length > 0
          ? 'Please correct the validation errors below'
          : 'Validation failed. Please check your input.';
        
        throw new SchoolRegistrationError(message, statusCode, fieldErrors);
      }
      
      // Handle 400 - Bad request
      if (statusCode === 400) {
        const message = typeof errorData?.detail === 'string'
          ? errorData.detail
          : 'Invalid request. Please check your input and try again.';
        throw new SchoolRegistrationError(message, statusCode);
      }
      
      // Handle 409 - Duplicate code (conflict)
      if (statusCode === 409) {
        const message = typeof errorData?.detail === 'string'
          ? errorData.detail
          : 'School code already exists. Please use a different code.';
        throw new SchoolRegistrationError(message, statusCode, { code: message });
      }
      
      // Handle 401/403 - Authentication/Authorization
      if (statusCode === 401 || statusCode === 403) {
        const message = statusCode === 401
          ? 'Authentication required. Please log in and try again.'
          : 'You do not have permission to perform this action.';
        throw new SchoolRegistrationError(message, statusCode);
      }
      
      // Handle other 4xx errors
      const message = typeof errorData?.detail === 'string'
        ? errorData.detail
        : `Request failed with status ${statusCode}. Please try again.`;
      throw new SchoolRegistrationError(message, statusCode);
    }
    
    return response.data;
  } catch (error) {
    // Handle axios errors
    if (axios.isAxiosError(error)) {
      const statusCode = error.response?.status || 500;
      const errorData = error.response?.data as ApiError | undefined;
      
      // Handle 500 - Internal server error
      if (statusCode === 500) {
        const message = typeof errorData?.detail === 'string'
          ? errorData.detail
          : 'Server error. Our team has been notified. Please try again later.';
        throw new SchoolRegistrationError(message, statusCode);
      }
      
      // Handle 502 - Bad Gateway
      if (statusCode === 502) {
        throw new SchoolRegistrationError(
          'Service temporarily unavailable. Please try again in a few moments.',
          statusCode
        );
      }
      
      // Handle 503 - Service Unavailable
      if (statusCode === 503) {
        throw new SchoolRegistrationError(
          'Service is currently unavailable. Please try again later.',
          statusCode
        );
      }
      
      // Handle 504 - Gateway Timeout
      if (statusCode === 504) {
        throw new SchoolRegistrationError(
          'Request timed out. Please check your connection and try again.',
          statusCode
        );
      }
      
      // Handle network errors (no response received)
      if (!error.response) {
        // Connection timeout
        if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT') {
          throw new SchoolRegistrationError(
            'Request timed out. Please check your internet connection and try again.',
            0
          );
        }
        
        // Network error (server unreachable, CORS, etc.)
        if (error.code === 'ERR_NETWORK') {
          throw new SchoolRegistrationError(
            'Unable to connect to the server. Please ensure:\n' +
            '• The backend services are running\n' +
            '• Your internet connection is stable\n' +
            '• There are no firewall restrictions',
            0
          );
        }
        
        // CORS error
        if (error.code === 'ERR_CORS') {
          throw new SchoolRegistrationError(
            'Cross-origin request blocked. Please contact support if this issue persists.',
            0
          );
        }
        
        // Generic network error
        throw new SchoolRegistrationError(
          'Network error. Please check your connection and try again.',
          0
        );
      }
      
      // Generic axios error with response
      const message = error.response?.data?.detail 
        ? String(error.response.data.detail)
        : error.message || 'An unexpected error occurred';
      throw new SchoolRegistrationError(message, statusCode);
    }
    
    // Handle SchoolRegistrationError (re-throw as-is)
    if (error instanceof SchoolRegistrationError) {
      throw error;
    }
    
    // Handle unknown errors
    const errorMessage = error instanceof Error 
      ? error.message 
      : 'An unexpected error occurred. Please try again.';
    
    // Log unexpected errors for debugging
    console.error('Unexpected error during school registration:', error);
    
    throw new SchoolRegistrationError(errorMessage, 500);
  }
}

/**
 * Map backend field names to frontend field names.
 * Handles any differences in naming conventions.
 */
function mapBackendFieldToFrontend(backendField: string): string {
  const fieldMap: Record<string, string> = {
    // Add mappings if backend uses different field names
    // Example: 'school_name' -> 'name'
  };
  
  return fieldMap[backendField] || backendField;
}

