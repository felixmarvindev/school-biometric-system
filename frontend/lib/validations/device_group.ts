/**
 * Zod validation schemas for Device Group entities.
 */

import { z } from "zod"

export const deviceGroupFormSchema = z.object({
  name: z
    .string()
    .min(1, "Group name is required")
    .max(200, "Group name must be at most 200 characters"),
  description: z
    .string()
    .max(1000, "Description must be at most 1000 characters")
    .nullable()
    .optional(),
})

export const deviceGroupUpdateSchema = z.object({
  name: z
    .string()
    .min(1, "Group name is required")
    .max(200, "Group name must be at most 200 characters")
    .optional(),
  description: z
    .string()
    .max(1000, "Description must be at most 1000 characters")
    .nullable()
    .optional(),
})

export type DeviceGroupFormData = z.infer<typeof deviceGroupFormSchema>
export type DeviceGroupUpdateFormData = z.infer<typeof deviceGroupUpdateSchema>

