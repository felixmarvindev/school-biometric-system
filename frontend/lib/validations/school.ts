/**
 * Zod validation schemas for School entities.
 * 
 * Matches the backend Pydantic schemas in shared/schemas/school.py
 */

import { z } from 'zod';
import {
  adminAccountSchema,
  type AdminAccountFormData,
} from '@/lib/validations/user';

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

/**
 * Combined school registration with admin user schema.
 * This combines school data with admin user data for a single registration flow.
 */
export const schoolRegistrationWithAdminSchema = schoolRegistrationSchema.extend({
  admin: z.object({
    email: z
      .string()
      .min(1, 'Email is required')
      .email('Please enter a valid email address'),
    first_name: z
      .string()
      .min(1, 'First name is required')
      .max(100, 'First name must be less than 100 characters'),
    last_name: z
      .string()
      .min(1, 'Last name is required')
      .max(100, 'Last name must be less than 100 characters'),
    password: z
      .string()
      .min(8, 'Password must be at least 8 characters')
      .max(72, 'Password cannot be longer than 72 bytes')
      .refine(
        (val) => {
          const encoder = new TextEncoder();
          const bytes = encoder.encode(val);
          return bytes.length <= 72;
        },
        {
          message: 'Password cannot be longer than 72 bytes. Please use a shorter password.',
        }
      )
      .regex(/[A-Z]/, 'Password must contain an uppercase letter')
      .regex(/[a-z]/, 'Password must contain a lowercase letter')
      .regex(/[0-9]/, 'Password must contain a number')
      .regex(/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/, 'Password must contain a special character (!@#$%^&*)'),
    confirmPassword: z.string().min(1, 'Please confirm your password'),
  }).refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
  }),
});

export type SchoolRegistrationWithAdminFormData = z.infer<typeof schoolRegistrationWithAdminSchema>;

