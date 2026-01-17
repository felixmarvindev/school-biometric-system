/**
 * Finger information and utilities for enrollment
 */

export interface FingerInfo {
  id: number
  name: string
  hand: "left" | "right"
  recommended?: boolean
}

export const FINGERS: FingerInfo[] = [
  { id: 0, name: "Right Thumb", hand: "right", recommended: true },
  { id: 1, name: "Right Index", hand: "right", recommended: true },
  { id: 2, name: "Right Middle", hand: "right" },
  { id: 3, name: "Right Ring", hand: "right" },
  { id: 4, name: "Right Pinky", hand: "right" },
  { id: 5, name: "Left Thumb", hand: "left" },
  { id: 6, name: "Left Index", hand: "left" },
  { id: 7, name: "Left Middle", hand: "left" },
  { id: 8, name: "Left Ring", hand: "left" },
  { id: 9, name: "Left Pinky", hand: "left" },
]

/**
 * Get finger information by ID
 */
export function getFingerInfo(fingerId: number): FingerInfo | undefined {
  return FINGERS.find((f) => f.id === fingerId)
}

/**
 * Get finger name by ID
 */
export function getFingerName(fingerId: number): string {
  return getFingerInfo(fingerId)?.name || `Finger ${fingerId}`
}
