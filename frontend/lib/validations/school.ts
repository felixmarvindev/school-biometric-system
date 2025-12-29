/**
 * Zod validation schemas for School entities.
 * 
 * TODO: This file will contain validation schemas for school registration.
 * Matches the backend Pydantic schemas in shared/schemas/school.py
 */

import { z } from 'zod';

/**
 * School registration form validation schema.
 * 
 * Validation rules:
 * - name: Required, 1-200 characters
 * - code: Required, 3-50 characters, pattern: ^[A-Za-z0-9-]+$
 * - address: Optional, max 500 characters
 * - phone: Optional, pattern: ^\+?[0-9]{10,15}$
 * - email: Optional, valid email format
 */
export const schoolRegistrationSchema = z.object({
  name: z
    .string()
    .min(1, 'School name is required')
    .max(200, 'School name must be less than 200 characters'),
  
  code: z
    .string()
    .min(3, 'School code must be at least 3 characters')
    .max(50, 'School code must be less than 50 characters')
    .regex(
      /^[A-Za-z0-9-]+$/,
      'School code can only contain letters, numbers, and hyphens'
    ),
  
  address: z
    .string()
    .max(500, 'Address must be less than 500 characters')
    .optional()
    .or(z.literal('')),
  
  phone: z
    .string()
    .regex(
      /^\+?[0-9]{10,15}$/,
      'Phone number must be 10-15 digits (optional + prefix)'
    )
    .optional()
    .or(z.literal('')),
  
  email: z
    .string()
    .email('Please enter a valid email address')
    .optional()
    .or(z.literal('')),
});

export type SchoolRegistrationFormData = z.infer<typeof schoolRegistrationSchema>;

