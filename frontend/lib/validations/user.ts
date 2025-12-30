/**
 * Zod validation schemas for User entities.
 * 
 * Matches the backend Pydantic schemas in shared/schemas/user.py
 */

import { z } from 'zod';

/**
 * Password strength requirements:
 * - Minimum 8 characters
 * - Maximum 72 bytes (bcrypt limitation)
 * - At least one uppercase letter
 * - At least one lowercase letter
 * - At least one digit
 * - At least one special character (!@#$%^&*)
 */
const passwordSchema = z
  .string()
  .min(8, 'Password must be at least 8 characters')
  .max(72, 'Password cannot be longer than 72 bytes')
  .refine(
    (val) => {
      // Check byte length (bcrypt has a 72-byte limit)
      // For most ASCII characters, 1 char = 1 byte, but we need to check actual byte length
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
  .regex(/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/, 'Password must contain a special character (!@#$%^&*)');

/**
 * Admin account creation form validation schema.
 * 
 * Validation rules:
 * - first_name: Required, 1-100 characters
 * - last_name: Required, 1-100 characters
 * - email: Required, valid email format
 * - password: Required, must meet strength requirements
 * - confirmPassword: Required, must match password
 */
export const adminAccountSchema = z
  .object({
    first_name: z
      .string()
      .min(1, 'First name is required')
      .max(100, 'First name must be less than 100 characters'),
    
    last_name: z
      .string()
      .min(1, 'Last name is required')
      .max(100, 'Last name must be less than 100 characters'),
    
    email: z
      .string()
      .min(1, 'Email is required')
      .email('Please enter a valid email address'),
    
    password: passwordSchema,
    
    confirmPassword: z.string().min(1, 'Please confirm your password'),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords don't match",
    path: ['confirmPassword'],
  });

export type AdminAccountFormData = z.infer<typeof adminAccountSchema>;

/**
 * Calculate password strength score (0-4).
 * 
 * @param password - Password to evaluate
 * @returns Strength score (0 = very weak, 4 = very strong)
 */
export function calculatePasswordStrength(password: string): number {
  if (!password) return 0;
  
  let strength = 0;
  
  // Length check
  if (password.length >= 8) strength++;
  if (password.length >= 12) strength++;
  
  // Character variety checks
  if (/[a-z]/.test(password)) strength++;
  if (/[A-Z]/.test(password)) strength++;
  if (/[0-9]/.test(password)) strength++;
  if (/[!@#$%^&*()_+\-=\[\]{}|;:,.<>?]/.test(password)) strength++;
  
  // Cap at 4 (very strong)
  return Math.min(strength, 4);
}

/**
 * Get password strength label.
 * 
 * @param strength - Strength score (0-4)
 * @returns Human-readable strength label
 */
export function getPasswordStrengthLabel(strength: number): string {
  if (strength === 0) return 'Very Weak';
  if (strength === 1) return 'Weak';
  if (strength === 2) return 'Fair';
  if (strength === 3) return 'Good';
  return 'Very Strong';
}

/**
 * Get password strength color class.
 * 
 * @param strength - Strength score (0-4)
 * @returns Tailwind color class for the strength indicator
 */
export function getPasswordStrengthColor(strength: number): string {
  if (strength === 0) return 'bg-red-500';
  if (strength === 1) return 'bg-orange-500';
  if (strength === 2) return 'bg-yellow-500';
  if (strength === 3) return 'bg-blue-500';
  return 'bg-green-500';
}

