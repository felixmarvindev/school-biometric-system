/**
 * Step Progress Indicator Component
 * 
 * Displays a progress indicator for multi-step forms.
 */

"use client"

interface StepProgressIndicatorProps {
  /** Current step (1-based) */
  currentStep: number
  /** Total number of steps */
  totalSteps: number
  /** Step labels */
  stepLabels: string[]
  /** Custom class name */
  className?: string
}

/**
 * Step Progress Indicator Component
 */
export function StepProgressIndicator({
  currentStep,
  totalSteps,
  stepLabels,
  className = "",
}: StepProgressIndicatorProps) {
  return (
    <div className={`flex items-center justify-center gap-2 ${className}`}>
      {Array.from({ length: totalSteps }, (_, i) => i + 1).map((step) => (
        <div key={step} className="flex items-center">
          <div className="flex items-center gap-2">
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-semibold transition-all duration-300 ${
                currentStep >= step
                  ? "bg-blue-600 text-white shadow-lg shadow-blue-600/30"
                  : "bg-gray-200 text-gray-500"
              }`}
            >
              {step}
            </div>
            <span
              className={`text-sm font-medium transition-colors duration-300 ${
                currentStep >= step ? "text-blue-600" : "text-gray-400"
              }`}
            >
              {stepLabels[step - 1] || `Step ${step}`}
            </span>
          </div>
          {step < totalSteps && (
            <div
              className={`w-16 h-1 mx-3 rounded-full transition-all duration-300 ${
                currentStep > step ? "bg-blue-600" : "bg-gray-200"
              }`}
            />
          )}
        </div>
      ))}
    </div>
  )
}

