/**
 * API client functions for Device management.
 * 
 * Base URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'
 * Endpoints:
 * - GET /api/v1/devices - List devices (with pagination, filtering, search)
 * - GET /api/v1/devices/{id} - Get device by ID
 * - POST /api/v1/devices - Create a new device
 * - PATCH /api/v1/devices/{id} - Update device
 * - DELETE /api/v1/devices/{id} - Soft delete device
 * - POST /api/v1/devices/{id}/test - Test device connection
 */

import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8002';

/**
 * Device status enumeration.
 */
export type DeviceStatus = 'online' | 'offline' | 'unknown';

/**
 * Device response type from the API.
 */
export interface DeviceResponse {
  id: number;
  school_id: number;
  name: string;
  ip_address: string;
  port: number;
  com_password: string | null;
  serial_number: string | null;
  location: string | null;
  description: string | null;
  status: DeviceStatus;
  last_seen: string | null; // ISO datetime string
  last_sync: string | null; // ISO datetime string
  max_users: number | null;
  enrolled_users: number;
  device_group_id: number | null;
  created_at: string; // ISO datetime
  updated_at: string | null;
}

/**
 * Paginated device list response.
 */
export interface PaginatedDeviceResponse {
  items: DeviceResponse[];
  total: number;
  page: number;
  page_size: number;
  pages: number;
}

/**
 * Device creation data (school_id is auto-assigned).
 */
export interface DeviceCreateData {
  name: string;
  ip_address: string;
  port?: number;
  com_password?: string | null;
  serial_number?: string | null;
  location?: string | null;
  description?: string | null;
  device_group_id?: number | null;
}

/**
 * Device update data.
 */
export interface DeviceUpdateData {
  name?: string;
  ip_address?: string;
  port?: number;
  com_password?: string | null;
  serial_number?: string | null;
  location?: string | null;
  description?: string | null;
  device_group_id?: number | null;
}

/**
 * List devices query parameters.
 */
export interface ListDevicesParams {
  page?: number;
  page_size?: number;
  search?: string;
  status?: DeviceStatus;
  device_group_id?: number;
}

/**
 * Device connection test request.
 */
export interface DeviceConnectionTestRequest {
  timeout?: number;
}

/**
 * Device connection test by address (before device creation).
 */
export interface DeviceConnectionTestByAddressRequest {
  ip_address: string;
  port: number;
  com_password?: string | null;
  timeout?: number;
}

/**
 * Device connection test response.
 */
export interface DeviceConnectionTestResponse {
  success: boolean;
  message: string;
  device_info?: Record<string, unknown> | null;
  response_time_ms?: number | null;
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
 * Custom error class for device API errors.
 */
export class DeviceApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public fieldErrors?: Record<string, string>
  ) {
    super(message);
    this.name = 'DeviceApiError';
  }
}

/**
 * List devices with pagination, filtering, and search.
 * 
 * @param token - JWT authentication token
 * @param params - Query parameters (page, page_size, filters, search)
 * @returns Promise resolving to paginated device list
 * @throws DeviceApiError if request fails
 */
export async function listDevices(
  token: string,
  params: ListDevicesParams = {}
): Promise<PaginatedDeviceResponse> {
  try {
    const queryParams = new URLSearchParams();
    if (params.page) queryParams.append('page', params.page.toString());
    if (params.page_size) queryParams.append('page_size', params.page_size.toString());
    if (params.search) queryParams.append('search', params.search);
    if (params.status) queryParams.append('status', params.status);
    if (params.device_group_id) queryParams.append('device_group_id', params.device_group_id.toString());

    const response = await axios.get<PaginatedDeviceResponse>(
      `${API_BASE_URL}/api/v1/devices?${queryParams.toString()}`,
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
        throw new DeviceApiError(
          'Authentication required. Please log in and try again.',
          statusCode
        );
      }

      const message = typeof errorData?.detail === 'string'
        ? errorData.detail
        : `Failed to load devices (${statusCode})`;
      throw new DeviceApiError(message, statusCode);
    }

    return response.data;
  } catch (error) {
    if (error instanceof DeviceApiError) {
      throw error;
    }
    if (axios.isAxiosError(error)) {
      throw new DeviceApiError(
        error.message || 'Failed to load devices',
        error.response?.status || 500
      );
    }
    throw new DeviceApiError('An unexpected error occurred', 500);
  }
}

/**
 * Get a device by ID.
 * 
 * @param token - JWT authentication token
 * @param deviceId - Device ID
 * @returns Promise resolving to device data
 * @throws DeviceApiError if request fails
 */
export async function getDevice(
  token: string,
  deviceId: number
): Promise<DeviceResponse> {
  try {
    const response = await axios.get<DeviceResponse>(
      `${API_BASE_URL}/api/v1/devices/${deviceId}`,
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
        throw new DeviceApiError(
          'Authentication required. Please log in and try again.',
          statusCode
        );
      }

      if (statusCode === 404) {
        throw new DeviceApiError('Device not found', statusCode);
      }

      const message = typeof errorData?.detail === 'string'
        ? errorData.detail
        : `Failed to load device (${statusCode})`;
      throw new DeviceApiError(message, statusCode);
    }

    return response.data;
  } catch (error) {
    if (error instanceof DeviceApiError) {
      throw error;
    }
    if (axios.isAxiosError(error)) {
      throw new DeviceApiError(
        error.message || 'Failed to load device',
        error.response?.status || 500
      );
    }
    throw new DeviceApiError('An unexpected error occurred', 500);
  }
}

/**
 * Create a new device.
 * 
 * @param token - JWT authentication token
 * @param data - Device creation data
 * @returns Promise resolving to created device
 * @throws DeviceApiError if request fails
 */
export async function createDevice(
  token: string,
  data: DeviceCreateData
): Promise<DeviceResponse> {
  try {
    const response = await axios.post<DeviceResponse>(
      `${API_BASE_URL}/api/v1/devices`,
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
        throw new DeviceApiError(
          'Authentication required. Please log in and try again.',
          statusCode
        );
      }

      if (statusCode === 409) {
        const message = typeof errorData?.detail === 'string'
          ? errorData.detail
          : 'Device with this IP address, port, or serial number already exists';
        throw new DeviceApiError(message, statusCode);
      }

      // Handle validation errors (422)
      if (statusCode === 422) {
        let message = 'Validation failed. Please check your input.';
        const fieldErrors: Record<string, string> = {};

        if (Array.isArray(errorData?.detail)) {
          errorData.detail.forEach((err) => {
            const field = err.loc[err.loc.length - 1] as string;
            fieldErrors[field] = err.msg;
          });
          message = 'Please correct the errors below.';
        } else if (typeof errorData?.detail === 'string') {
          message = errorData.detail;
        }

        throw new DeviceApiError(message, statusCode, fieldErrors);
      }

      const message = typeof errorData?.detail === 'string'
        ? errorData.detail
        : `Failed to create device (${statusCode})`;
      throw new DeviceApiError(message, statusCode);
    }

    return response.data;
  } catch (error) {
    if (error instanceof DeviceApiError) {
      throw error;
    }
    if (axios.isAxiosError(error)) {
      throw new DeviceApiError(
        error.message || 'Failed to create device',
        error.response?.status || 500
      );
    }
    throw new DeviceApiError('An unexpected error occurred', 500);
  }
}

/**
 * Update a device.
 * 
 * @param token - JWT authentication token
 * @param deviceId - Device ID
 * @param data - Device update data
 * @returns Promise resolving to updated device
 * @throws DeviceApiError if request fails
 */
export async function updateDevice(
  token: string,
  deviceId: number,
  data: DeviceUpdateData
): Promise<DeviceResponse> {
  try {
    const response = await axios.patch<DeviceResponse>(
      `${API_BASE_URL}/api/v1/devices/${deviceId}`,
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
        throw new DeviceApiError(
          'Authentication required. Please log in and try again.',
          statusCode
        );
      }

      if (statusCode === 404) {
        throw new DeviceApiError('Device not found', statusCode);
      }

      if (statusCode === 409) {
        const message = typeof errorData?.detail === 'string'
          ? errorData.detail
          : 'Device with this IP address, port, or serial number already exists';
        throw new DeviceApiError(message, statusCode);
      }

      // Handle validation errors (422)
      if (statusCode === 422) {
        let message = 'Validation failed. Please check your input.';
        const fieldErrors: Record<string, string> = {};

        if (Array.isArray(errorData?.detail)) {
          errorData.detail.forEach((err) => {
            const field = err.loc[err.loc.length - 1] as string;
            fieldErrors[field] = err.msg;
          });
          message = 'Please correct the errors below.';
        } else if (typeof errorData?.detail === 'string') {
          message = errorData.detail;
        }

        throw new DeviceApiError(message, statusCode, fieldErrors);
      }

      const message = typeof errorData?.detail === 'string'
        ? errorData.detail
        : `Failed to update device (${statusCode})`;
      throw new DeviceApiError(message, statusCode);
    }

    return response.data;
  } catch (error) {
    if (error instanceof DeviceApiError) {
      throw error;
    }
    if (axios.isAxiosError(error)) {
      throw new DeviceApiError(
        error.message || 'Failed to update device',
        error.response?.status || 500
      );
    }
    throw new DeviceApiError('An unexpected error occurred', 500);
  }
}

/**
 * Delete a device (soft delete).
 * 
 * @param token - JWT authentication token
 * @param deviceId - Device ID
 * @throws DeviceApiError if request fails
 */
export async function deleteDevice(
  token: string,
  deviceId: number
): Promise<void> {
  try {
    const response = await axios.delete(
      `${API_BASE_URL}/api/v1/devices/${deviceId}`,
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
        throw new DeviceApiError(
          'Authentication required. Please log in and try again.',
          statusCode
        );
      }

      if (statusCode === 404) {
        throw new DeviceApiError('Device not found', statusCode);
      }

      const message = typeof errorData?.detail === 'string'
        ? errorData.detail
        : `Failed to delete device (${statusCode})`;
      throw new DeviceApiError(message, statusCode);
    }
  } catch (error) {
    if (error instanceof DeviceApiError) {
      throw error;
    }
    if (axios.isAxiosError(error)) {
      throw new DeviceApiError(
        error.message || 'Failed to delete device',
        error.response?.status || 500
      );
    }
    throw new DeviceApiError('An unexpected error occurred', 500);
  }
}

/**
 * Test device connection.
 * 
 * @param token - JWT authentication token
 * @param deviceId - Device ID
 * @param config - Connection test configuration (optional timeout)
 * @returns Promise resolving to connection test result
 * @throws DeviceApiError if request fails
 */
export async function testDeviceConnection(
  token: string,
  deviceId: number,
  config?: DeviceConnectionTestRequest
): Promise<DeviceConnectionTestResponse> {
  try {
    const response = await axios.post<DeviceConnectionTestResponse>(
      `${API_BASE_URL}/api/v1/devices/${deviceId}/test`,
      config || {},
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
        throw new DeviceApiError(
          'Authentication required. Please log in and try again.',
          statusCode
        );
      }

      if (statusCode === 404) {
        throw new DeviceApiError('Device not found', statusCode);
      }

      const message = typeof errorData?.detail === 'string'
        ? errorData.detail
        : `Connection test failed (${statusCode})`;
      throw new DeviceApiError(message, statusCode);
    }

    return response.data;
  } catch (error) {
    if (error instanceof DeviceApiError) {
      throw error;
    }
    if (axios.isAxiosError(error)) {
      throw new DeviceApiError(
        error.message || 'Connection test failed',
        error.response?.status || 500
      );
    }
    throw new DeviceApiError('An unexpected error occurred', 500);
  }
}

/**
 * Test device connection by IP address and port (before device creation).
 * 
 * @param token - JWT authentication token
 * @param testData - Connection test data (IP, port, password, timeout)
 * @returns Promise resolving to connection test result
 * @throws DeviceApiError if request fails
 */
export async function testDeviceConnectionByAddress(
  token: string,
  testData: DeviceConnectionTestByAddressRequest
): Promise<DeviceConnectionTestResponse> {
  try {
    const response = await axios.post<DeviceConnectionTestResponse>(
      `${API_BASE_URL}/api/v1/devices/test-connection`,
      testData,
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
        throw new DeviceApiError(
          'Authentication required. Please log in and try again.',
          statusCode
        );
      }

      if (statusCode === 422) {
        const message = typeof errorData?.detail === 'string'
          ? errorData.detail
          : 'Validation failed. Please check your input.';
        throw new DeviceApiError(message, statusCode);
      }

      const message = typeof errorData?.detail === 'string'
        ? errorData.detail
        : `Connection test failed (${statusCode})`;
      throw new DeviceApiError(message, statusCode);
    }

    return response.data;
  } catch (error) {
    if (error instanceof DeviceApiError) {
      throw error;
    }
    if (axios.isAxiosError(error)) {
      throw new DeviceApiError(
        error.message || 'Connection test failed',
        error.response?.status || 500
      );
    }
    throw new DeviceApiError('An unexpected error occurred', 500);
  }
}

