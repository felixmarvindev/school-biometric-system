/**
 * Zod validation schemas for Student entities.
 * 
 * Matches the backend Pydantic schemas in shared/schemas/student.py
 */

import { z } from 'zod';

/**
 * Gender enumeration.
 */
export const genderEnum = z.enum(['male', 'female', 'other']);

/**
 * Student form validation schema (for create and update).
 */
export const studentFormSchema = z.object({
  admission_number: z
    .string()
    .min(1, 'Admission number is required')
    .max(50, 'Admission number must be less than 50 characters'),
  
  first_name: z
    .string()
    .min(1, 'First name is required')
    .max(100, 'First name must be less than 100 characters'),
  
  last_name: z
    .string()
    .min(1, 'Last name is required')
    .max(100, 'Last name must be less than 100 characters'),
  
  date_of_birth: z
    .string()
    .nullable()
    .optional()
    .refine(
      (val) => {
        if (!val || val === '') return true;
        const date = new Date(val);
        return !isNaN(date.getTime()) && date <= new Date();
      },
      { message: 'Date of birth must be a valid date in the past' }
    ),
  
  gender: genderEnum.nullable().optional(),
  
  class_id: z
    .number()
    .int()
    .positive()
    .nullable()
    .optional(),
  
  stream_id: z
    .number()
    .int()
    .positive()
    .nullable()
    .optional(),
  
  parent_phone: z
    .string()
    .nullable()
    .optional()
    .refine(
      (val) => {
        if (!val || val === '') return true; // Allow empty
        return /^\+?[0-9]{10,15}$/.test(val);
      },
      { message: 'Phone number must be 10-15 digits (optional + prefix)' }
    ),
  
  parent_email: z
    .string()
    .nullable()
    .optional()
    .refine(
      (val) => {
        if (!val || val === '') return true; // Allow empty
        return z.string().email().safeParse(val).success;
      },
      { message: 'Please enter a valid email address' }
    ),
});

/**
 * Student create form data type.
 */
export type StudentFormData = z.infer<typeof studentFormSchema>;

/**
 * Student update form data (all fields optional except those being updated).
 */
export const studentUpdateSchema = studentFormSchema.partial().extend({
  admission_number: z.string().optional(), // Not included in updates (immutable)
});

/**
 * Student update form data type.
 */
export type StudentUpdateFormData = z.infer<typeof studentUpdateSchema>;

