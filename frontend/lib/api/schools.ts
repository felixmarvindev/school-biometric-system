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
 * Register a new school.
 * 
 * @param data - School registration data
 * @returns Promise resolving to the created school
 * @throws Error if registration fails
 * 
 * TODO: Implement this function to call the API endpoint.
 * Handle errors:
 * - 422: Validation errors (map to form fields)
 * - 409: Duplicate code error
 * - 500: Server error
 */
export async function registerSchool(
  data: SchoolRegistrationFormData
): Promise<SchoolResponse> {
  // TODO: Implement API call
  // const response = await axios.post<SchoolResponse>(
  //   `${API_BASE_URL}/api/v1/schools/register`,
  //   data
  // );
  // return response.data;
  
  throw new Error('registerSchool not implemented yet');
}

