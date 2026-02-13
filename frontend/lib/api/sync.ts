/**
 * Sync API client.
 *
 * Handles student-device sync operations: check sync status, sync student to device.
 */

import axios from "axios";
import { useAuthStore } from "../store/authStore";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";

export interface SyncStatusResponse {
  device_id: number;
  student_id: number;
  synced: boolean;
}

export interface SyncSuccessResponse {
  message: string;
  device_id: number;
  student_id: number;
}

export class SyncApiError extends Error {
  constructor(
    message: string,
    public statusCode: number,
    public code?: string
  ) {
    super(message);
    this.name = "SyncApiError";
  }
}

/**
 * Check if a student is synced to a device.
 */
export async function getSyncStatus(
  deviceId: number,
  studentId: number
): Promise<SyncStatusResponse> {
  const authStore = useAuthStore.getState();
  const token = authStore.token;
  if (!token) throw new Error("Not authenticated");

  const response = await axios.get<SyncStatusResponse>(
    `${API_BASE_URL}/api/v1/sync/devices/${deviceId}/students/${studentId}/status`,
    {
      headers: { Authorization: `Bearer ${token}` },
    }
  );
  return response.data;
}

/**
 * Sync a student to a device.
 */
export async function syncStudentToDevice(
  studentId: number,
  deviceId: number
): Promise<SyncSuccessResponse> {
  const authStore = useAuthStore.getState();
  const token = authStore.token;
  if (!token) throw new Error("Not authenticated");

  try {
    const response = await axios.post<SyncSuccessResponse>(
      `${API_BASE_URL}/api/v1/sync/students/${studentId}/devices/${deviceId}`,
      {},
      {
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      }
    );
    return response.data;
  } catch (err) {
    if (axios.isAxiosError(err) && err.response) {
      const detail = err.response.data?.detail;
      const message =
        typeof detail === "string" ? detail : detail?.message || err.message;
      throw new SyncApiError(
        message,
        err.response.status,
        detail?.code
      );
    }
    throw err;
  }
}
