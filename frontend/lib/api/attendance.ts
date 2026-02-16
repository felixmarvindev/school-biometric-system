/**
 * API client functions for Attendance records.
 *
 * Base URL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003'
 * Endpoints:
 * - GET /api/v1/attendance          — List records (paginated, filtered)
 * - GET /api/v1/attendance/stats    — Summary stats for a date
 * - GET /api/v1/attendance/students/{id} — Student detail records
 */

import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8003";

// -------------------------------------------------------------------
// Types
// -------------------------------------------------------------------

export type EventType = "IN" | "OUT" | "UNKNOWN" | "DUPLICATE";

export interface AttendanceEvent {
  /** DB primary key (number) for stored records, UUID string for live-only scans. */
  id: string | number;
  student_id: number | null;
  student_name: string | null;
  admission_number: string | null;
  class_name: string | null;
  device_id: number;
  device_name: string;
  event_type: EventType;
  occurred_at: string; // ISO datetime
}

export interface PaginatedAttendanceResponse {
  items: AttendanceEvent[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface AttendanceStats {
  date: string; // YYYY-MM-DD
  total_events: number;
  checked_in: number;
  checked_out: number;
  total_students: number;
  present_rate: number;
}

// -------------------------------------------------------------------
// Filter params
// -------------------------------------------------------------------

export interface AttendanceListParams {
  target_date?: string; // YYYY-MM-DD
  student_id?: number;
  class_id?: number;
  device_id?: number;
  event_type?: EventType;
  page?: number;
  page_size?: number;
}

// -------------------------------------------------------------------
// API functions
// -------------------------------------------------------------------

/**
 * List attendance records with filters and pagination.
 *
 * @param token - JWT authentication token
 * @param params - Query parameters (date, filters, pagination)
 */
export async function listAttendance(
  token: string,
  params: AttendanceListParams = {}
): Promise<PaginatedAttendanceResponse> {
  const queryParams = new URLSearchParams();
  if (params.target_date) queryParams.append("target_date", params.target_date);
  if (params.student_id) queryParams.append("student_id", params.student_id.toString());
  if (params.class_id) queryParams.append("class_id", params.class_id.toString());
  if (params.device_id) queryParams.append("device_id", params.device_id.toString());
  if (params.event_type) queryParams.append("event_type", params.event_type);
  if (params.page) queryParams.append("page", params.page.toString());
  if (params.page_size) queryParams.append("page_size", params.page_size.toString());

  const { data } = await axios.get<PaginatedAttendanceResponse>(
    `${API_BASE_URL}/api/v1/attendance?${queryParams.toString()}`,
    {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    }
  );
  return data;
}

/**
 * Get attendance summary stats for a date.
 *
 * @param token - JWT authentication token
 * @param targetDate - Date string (YYYY-MM-DD), defaults to today on the server
 */
export async function getAttendanceStats(
  token: string,
  targetDate?: string
): Promise<AttendanceStats> {
  const queryParams = new URLSearchParams();
  if (targetDate) queryParams.append("target_date", targetDate);

  const { data } = await axios.get<AttendanceStats>(
    `${API_BASE_URL}/api/v1/attendance/stats?${queryParams.toString()}`,
    {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    }
  );
  return data;
}

/**
 * Get attendance records for a specific student (chronological).
 *
 * @param token - JWT authentication token
 * @param studentId - Student ID
 * @param targetDate - Optional date filter (YYYY-MM-DD)
 */
export async function getStudentAttendance(
  token: string,
  studentId: number,
  targetDate?: string
): Promise<AttendanceEvent[]> {
  const queryParams = new URLSearchParams();
  if (targetDate) queryParams.append("target_date", targetDate);

  const { data } = await axios.get<AttendanceEvent[]>(
    `${API_BASE_URL}/api/v1/attendance/students/${studentId}?${queryParams.toString()}`,
    {
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
    }
  );
  return data;
}
