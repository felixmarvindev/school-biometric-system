/**
 * Validation schemas for Student Wizard steps.
 */

import { z } from "zod"
import { genderEnum } from "./student"

export const step1PersonalSchema = z.object({
  first_name: z.string().min(1, "First name is required").max(100, "First name must be less than 100 characters"),
  last_name: z.string().min(1, "Last name is required").max(100, "Last name must be less than 100 characters"),
  date_of_birth: z
    .string()
    .nullable()
    .optional()
    .refine((val) => {
      if (!val || val === "") return true
      const date = new Date(val)
      return !isNaN(date.getTime()) && date <= new Date()
    }, { message: "Date of birth must be a valid date in the past" }),
  gender: genderEnum.nullable().optional(),
  parent_phone: z
    .string()
    .nullable()
    .optional()
    .refine((val) => {
      if (!val || val === "") return true
      return /^\+?[0-9]{10,15}$/.test(val)
    }, { message: "Phone number must be 10-15 digits" }),
  parent_email: z
    .string()
    .nullable()
    .optional()
    .refine((val) => {
      if (!val || val === "") return true
      return z.string().email().safeParse(val).success
    }, { message: "Please enter a valid email address" }),
})

export const step2ClassSchema = z.object({
  admission_number: z
    .string()
    .min(1, "Admission number is required")
    .max(50, "Admission number must be less than 50 characters"),
  class_id: z.number().int().positive().nullable().optional(),
  stream_id: z.number().int().positive().nullable().optional(),
})

export type Step1PersonalData = z.infer<typeof step1PersonalSchema>
export type Step2ClassData = z.infer<typeof step2ClassSchema>
