/**
 * API client functions for Student management.
 * 
 * Base URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
 * Endpoints:
 * - GET /api/v1/students - List students (with pagination, filtering, search)
 * - GET /api/v1/students/{id} - Get student by ID
 * - POST /api/v1/students - Create a new student
 * - PUT /api/v1/students/{id} - Update student
 * - DELETE /api/v1/students/{id} - Soft delete student
 */

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';

/**
 * Gender enumeration.
 */
export type Gender = 'male' | 'female' | 'other';

/**
 * Student response type from the API.
 */
export interface StudentResponse {
  id: number;
  school_id: number;
  admission_number: string;
  first_name: string;
  last_name: string;
  date_of_birth: string | null; // ISO date string
  gender: Gender | null;
  class_id: number | null;
  stream_id: number | null;
  parent_phone: string | null;
  parent_email: string | null;
  is_deleted: boolean;
  created_at: string; // ISO datetime
  updated_at: string | null;
}

/**
 * Paginated student list response.
 */
export interface PaginatedStudentResponse {
  items: StudentResponse[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

/**
 * Student creation data (school_id is auto-assigned).
 */
export interface StudentCreateData {
  admission_number: string;
  first_name: string;
  last_name: string;
  date_of_birth?: string | null;
  gender?: Gender | null;
  class_id?: number | null;
  stream_id?: number | null;
  parent_phone?: string | null;
  parent_email?: string | null;
}

/**
 * Student update data.
 */
export interface StudentUpdateData {
  first_name?: string;
  last_name?: string;
  date_of_birth?: string | null;
  gender?: Gender | null;
  class_id?: number | null;
  stream_id?: number | null;
  parent_phone?: string | null;
  parent_email?: string | null;
}

/**
 * List students query parameters.
 */
export interface ListStudentsParams {
  page?: number;
  page_size?: number;
  class_id?: number;
  stream_id?: number;
  search?: string;
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
 * Custom error class for student API errors.
 */
export class StudentApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public fieldErrors?: Record<string, string>
  ) {
    super(message);
    this.name = 'StudentApiError';
  }
}

/**
 * List students with pagination, filtering, and search.
 * 
 * @param token - JWT authentication token
 * @param params - Query parameters (page, page_size, filters, search)
 * @returns Promise resolving to paginated student list
 * @throws StudentApiError if request fails
 */
export async function listStudents(
  token: string,
  params: ListStudentsParams = {}
): Promise<PaginatedStudentResponse> {
  try {
    const queryParams = new URLSearchParams();
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.page_size) queryParams.append('page_size', params.page_size.toString());
    if (params.class_id) queryParams.append('class_id', params.class_id.toString());
    if (params.stream_id) queryParams.append('stream_id', params.stream_id.toString());
    if (params.search) queryParams.append('search', params.search);

    const response = await axios.get<PaginatedStudentResponse>(
      `${API_BASE_URL}/api/v1/students?${queryParams.toString()}`,
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        validateStatus: (status) => status < 500,
      }
    );

    if (response.status >= 400) {
      const errorData = response.data as unknown as ApiError | undefined;
      const statusCode = response.status;

      if (statusCode === 401) {
        throw new StudentApiError(
          'Authentication required. Please log in and try again.',
          statusCode
        );
      }

      const message = typeof errorData?.detail === 'string'
        ? errorData.detail
        : `Failed to load students (${statusCode})`;
      throw new StudentApiError(message, statusCode);
    }

    return response.data;
  } catch (error) {
    if (error instanceof StudentApiError) {
      throw error;
    }

    if (axios.isAxiosError(error)) {
      const statusCode = error.response?.status || 0;

      if (!error.response) {
        if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT') {
          throw new StudentApiError(
            'Request timed out. Please check your internet connection and try again.',
            0
          );
        }

        if (error.code === 'ERR_NETWORK') {
          throw new StudentApiError(
            'Unable to connect to the server. Please ensure the backend services are running.',
            0
          );
        }

        throw new StudentApiError(
          'Network error. Please check your connection and try again.',
          0
        );
      }

      const errorData = error.response?.data as ApiError | undefined;
      const message = typeof errorData?.detail === 'string'
        ? errorData.detail
        : error.message || 'An unexpected error occurred';
      throw new StudentApiError(message, statusCode);
    }

    const errorMessage = error instanceof Error
      ? error.message
      : 'An unexpected error occurred. Please try again.';
    throw new StudentApiError(errorMessage, 500);
  }
}

/**
 * Get a student by ID.
 * 
 * @param token - JWT authentication token
 * @param studentId - Student ID
 * @returns Promise resolving to student data
 * @throws StudentApiError if request fails
 */
export async function getStudent(
  token: string,
  studentId: number
): Promise<StudentResponse> {
  try {
    const response = await axios.get<StudentResponse>(
      `${API_BASE_URL}/api/v1/students/${studentId}`,
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        validateStatus: (status) => status < 500,
      }
    );

    if (response.status >= 400) {
      const errorData = response.data as unknown as ApiError | undefined;
      const statusCode = response.status;

      if (statusCode === 401) {
        throw new StudentApiError(
          'Authentication required. Please log in and try again.',
          statusCode
        );
      }

      if (statusCode === 404) {
        throw new StudentApiError(
          'Student not found.',
          statusCode
        );
      }

      const message = typeof errorData?.detail === 'string'
        ? errorData.detail
        : `Failed to load student (${statusCode})`;
      throw new StudentApiError(message, statusCode);
    }

    return response.data;
  } catch (error) {
    if (error instanceof StudentApiError) {
      throw error;
    }

    if (axios.isAxiosError(error)) {
      const statusCode = error.response?.status || 0;

      if (!error.response) {
        if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT') {
          throw new StudentApiError(
            'Request timed out. Please check your internet connection and try again.',
            0
          );
        }

        if (error.code === 'ERR_NETWORK') {
          throw new StudentApiError(
            'Unable to connect to the server. Please ensure the backend services are running.',
            0
          );
        }

        throw new StudentApiError(
          'Network error. Please check your connection and try again.',
          0
        );
      }

      const errorData = error.response?.data as ApiError | undefined;
      const message = typeof errorData?.detail === 'string'
        ? errorData.detail
        : error.message || 'An unexpected error occurred';
      throw new StudentApiError(message, statusCode);
    }

    const errorMessage = error instanceof Error
      ? error.message
      : 'An unexpected error occurred. Please try again.';
    throw new StudentApiError(errorMessage, 500);
  }
}

/**
 * Create a new student.
 * 
 * @param token - JWT authentication token
 * @param data - Student creation data
 * @returns Promise resolving to created student
 * @throws StudentApiError if creation fails
 */
export async function createStudent(
  token: string,
  data: StudentCreateData
): Promise<StudentResponse> {
  try {
    const response = await axios.post<StudentResponse>(
      `${API_BASE_URL}/api/v1/students`,
      data,
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        validateStatus: (status) => status < 500,
      }
    );

    if (response.status >= 400) {
      const errorData = response.data as unknown as ApiError | undefined;
      const statusCode = response.status;

      if (statusCode === 401) {
        throw new StudentApiError(
          'Authentication required. Please log in and try again.',
          statusCode
        );
      }

      if (statusCode === 409) {
        const message = typeof errorData?.detail === 'string'
          ? errorData.detail
          : 'Admission number already exists for this school.';
        throw new StudentApiError(message, statusCode, { admission_number: message });
      }

      if (statusCode === 422) {
        const fieldErrors: Record<string, string> = {};
        if (Array.isArray(errorData?.detail)) {
          errorData.detail.forEach((err) => {
            const locArray = err.loc || [];
            const field = String(locArray[locArray.length - 1]);
            if (field && field !== 'body') {
              fieldErrors[field] = err.msg || 'Invalid value';
            }
          });
        }
        const message = Object.keys(fieldErrors).length > 0
          ? 'Please correct the validation errors below'
          : (typeof errorData?.detail === 'string' ? errorData.detail : 'Validation failed. Please check your input.');
        throw new StudentApiError(message, statusCode, fieldErrors);
      }

      const message = typeof errorData?.detail === 'string'
        ? errorData.detail
        : `Failed to create student (${statusCode})`;
      throw new StudentApiError(message, statusCode);
    }

    return response.data;
  } catch (error) {
    if (error instanceof StudentApiError) {
      throw error;
    }

    if (axios.isAxiosError(error)) {
      const statusCode = error.response?.status || 0;

      if (!error.response) {
        if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT') {
          throw new StudentApiError(
            'Request timed out. Please check your internet connection and try again.',
            0
          );
        }

        if (error.code === 'ERR_NETWORK') {
          throw new StudentApiError(
            'Unable to connect to the server. Please ensure the backend services are running.',
            0
          );
        }

        throw new StudentApiError(
          'Network error. Please check your connection and try again.',
          0
        );
      }

      const errorData = error.response?.data as ApiError | undefined;
      const message = typeof errorData?.detail === 'string'
        ? errorData.detail
        : error.message || 'An unexpected error occurred';
      throw new StudentApiError(message, statusCode);
    }

    const errorMessage = error instanceof Error
      ? error.message
      : 'An unexpected error occurred. Please try again.';
    throw new StudentApiError(errorMessage, 500);
  }
}

/**
 * Update a student.
 * 
 * @param token - JWT authentication token
 * @param studentId - Student ID
 * @param data - Student update data
 * @returns Promise resolving to updated student
 * @throws StudentApiError if update fails
 */
export async function updateStudent(
  token: string,
  studentId: number,
  data: StudentUpdateData
): Promise<StudentResponse> {
  try {
    const response = await axios.put<StudentResponse>(
      `${API_BASE_URL}/api/v1/students/${studentId}`,
      data,
      {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        validateStatus: (status) => status < 500,
      }
    );

    if (response.status >= 400) {
      const errorData = response.data as unknown as ApiError | undefined;
      const statusCode = response.status;

      if (statusCode === 401) {
        throw new StudentApiError(
          'Authentication required. Please log in and try again.',
          statusCode
        );
      }

      if (statusCode === 404) {
        throw new StudentApiError(
          'Student not found.',
          statusCode
        );
      }

      if (statusCode === 422) {
        const fieldErrors: Record<string, string> = {};
        if (Array.isArray(errorData?.detail)) {
          errorData.detail.forEach((err) => {
            const locArray = err.loc || [];
            const field = String(locArray[locArray.length - 1]);
            if (field && field !== 'body') {
              fieldErrors[field] = err.msg || 'Invalid value';
            }
          });
        }
        const message = Object.keys(fieldErrors).length > 0
          ? 'Please correct the validation errors below'
          : (typeof errorData?.detail === 'string' ? errorData.detail : 'Validation failed. Please check your input.');
        throw new StudentApiError(message, statusCode, fieldErrors);
      }

      const message = typeof errorData?.detail === 'string'
        ? errorData.detail
        : `Failed to update student (${statusCode})`;
      throw new StudentApiError(message, statusCode);
    }

    return response.data;
  } catch (error) {
    if (error instanceof StudentApiError) {
      throw error;
    }

    if (axios.isAxiosError(error)) {
      const statusCode = error.response?.status || 0;

      if (!error.response) {
        if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT') {
          throw new StudentApiError(
            'Request timed out. Please check your internet connection and try again.',
            0
          );
        }

        if (error.code === 'ERR_NETWORK') {
          throw new StudentApiError(
            'Unable to connect to the server. Please ensure the backend services are running.',
            0
          );
        }

        throw new StudentApiError(
          'Network error. Please check your connection and try again.',
          0
        );
      }

      const errorData = error.response?.data as ApiError | undefined;
      const message = typeof errorData?.detail === 'string'
        ? errorData.detail
        : error.message || 'An unexpected error occurred';
      throw new StudentApiError(message, statusCode);
    }

    const errorMessage = error instanceof Error
      ? error.message
      : 'An unexpected error occurred. Please try again.';
    throw new StudentApiError(errorMessage, 500);
  }
}

/**
 * Delete (soft delete) a student.
 * 
 * @param token - JWT authentication token
 * @param studentId - Student ID
 * @throws StudentApiError if deletion fails
 */
export async function deleteStudent(
  token: string,
  studentId: number
): Promise<void> {
  try {
    const response = await axios.delete(
      `${API_BASE_URL}/api/v1/students/${studentId}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        validateStatus: (status) => status < 500,
      }
    );

    if (response.status >= 400) {
      const errorData = response.data as unknown as ApiError | undefined;
      const statusCode = response.status;

      if (statusCode === 401) {
        throw new StudentApiError(
          'Authentication required. Please log in and try again.',
          statusCode
        );
      }

      if (statusCode === 404) {
        throw new StudentApiError(
          'Student not found.',
          statusCode
        );
      }

      const message = typeof errorData?.detail === 'string'
        ? errorData.detail
        : `Failed to delete student (${statusCode})`;
      throw new StudentApiError(message, statusCode);
    }
  } catch (error) {
    if (error instanceof StudentApiError) {
      throw error;
    }

    if (axios.isAxiosError(error)) {
      const statusCode = error.response?.status || 0;

      if (!error.response) {
        if (error.code === 'ECONNABORTED' || error.code === 'ETIMEDOUT') {
          throw new StudentApiError(
            'Request timed out. Please check your internet connection and try again.',
            0
          );
        }

        if (error.code === 'ERR_NETWORK') {
          throw new StudentApiError(
            'Unable to connect to the server. Please ensure the backend services are running.',
            0
          );
        }

        throw new StudentApiError(
          'Network error. Please check your connection and try again.',
          0
        );
      }

      const errorData = error.response?.data as ApiError | undefined;
      const message = typeof errorData?.detail === 'string'
        ? errorData.detail
        : error.message || 'An unexpected error occurred';
      throw new StudentApiError(message, statusCode);
    }

    const errorMessage = error instanceof Error
      ? error.message
      : 'An unexpected error occurred. Please try again.';
    throw new StudentApiError(errorMessage, 500);
  }
}

