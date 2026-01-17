"use client"

import { useState } from "react"
import {
  User,
  Server,
  Fingerprint,
  Play,
  ChevronRight,
  ChevronLeft,
  Check,
  X,
  MapPin,
  Wifi,
  GraduationCap,
  Hash,
  Hand,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { cn } from "@/lib/utils"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { StudentSelector } from "./StudentSelector"
import { DeviceSelector } from "./DeviceSelector"
import { FingerSelector } from "./FingerSelector"
import { EnrollmentCapture } from "./EnrollmentCapture"
import type { StudentResponse } from "@/lib/api/students"
import type { DeviceResponse } from "@/lib/api/devices"
import { getFingerInfo, FINGERS } from "@/lib/utils/fingers"

const STEPS = [
  { id: 1, name: "Select Student", icon: User, description: "Choose a student to enroll" },
  { id: 2, name: "Choose Device", icon: Server, description: "Select biometric scanner" },
  { id: 3, name: "Select Finger", icon: Fingerprint, description: "Pick finger to enroll" },
  { id: 4, name: "Capture", icon: Play, description: "Complete enrollment" },
]

interface EnrollmentWizardProps {
  onStartEnrollment?: (data: {
    studentId: number
    deviceId: number
    fingerId: number
  }) => Promise<void>
}

export function EnrollmentWizard({ onStartEnrollment }: EnrollmentWizardProps = {}) {
  const [currentStep, setCurrentStep] = useState(1)
  const [selectedStudent, setSelectedStudent] = useState<StudentResponse | null>(null)
  const [selectedDevice, setSelectedDevice] = useState<DeviceResponse | null>(null)
  const [selectedFinger, setSelectedFinger] = useState<number | null>(null)
  const [isCapturing, setIsCapturing] = useState(false)

  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return selectedStudent !== null
      case 2:
        return selectedDevice !== null && selectedDevice.status === "online"
      case 3:
        return selectedFinger !== null
      default:
        return false
    }
  }

  const handleNext = () => {
    if (canProceed() && currentStep < 4) {
      if (currentStep === 3) {
        setIsCapturing(true)
      }
      setCurrentStep(currentStep + 1)
    }
  }

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1)
      setIsCapturing(false)
    }
  }

  const handleEnrollmentComplete = async () => {
    if (onStartEnrollment && selectedStudent && selectedDevice && selectedFinger !== null) {
      await onStartEnrollment({
        studentId: selectedStudent.id,
        deviceId: selectedDevice.id,
        fingerId: selectedFinger,
      })
    }
    
    setCurrentStep(1)
    setSelectedStudent(null)
    setSelectedDevice(null)
    setSelectedFinger(null)
    setIsCapturing(false)
  }

  const handleEnrollAnother = () => {
    setCurrentStep(3)
    setSelectedFinger(null)
    setIsCapturing(false)
  }

  const getStepStatus = (stepId: number) => {
    if (stepId < currentStep) return "completed"
    if (stepId === currentStep) return "active"
    return "pending"
  }

  const fingerInfo = selectedFinger !== null ? FINGERS.find((f) => f.id === selectedFinger) : null

  const clearStudent = () => {
    setSelectedStudent(null)
    setSelectedDevice(null)
    setSelectedFinger(null)
    setCurrentStep(1)
  }

  const clearDevice = () => {
    setSelectedDevice(null)
    setSelectedFinger(null)
    if (currentStep > 2) setCurrentStep(2)
  }

  const clearFinger = () => {
    setSelectedFinger(null)
    if (currentStep > 3) setCurrentStep(3)
  }

  return (
    <div className="w-full max-w-4xl mx-auto">
      {/* Step Indicator */}
      <nav aria-label="Enrollment progress" className="mb-6">
        <ol className="flex items-center">
          {STEPS.map((step, index) => {
            const status = getStepStatus(step.id);
            const isLast = index === STEPS.length - 1;

            return (
              <li key={step.id} className={cn('flex items-center', !isLast && 'flex-1')}>
                <div className="flex flex-col items-center">
                  <div
                    className={cn(
                      "flex items-center justify-center size-10 sm:size-12 rounded-full border-2 transition-all",
                      status === "completed" && "bg-blue-600 border-blue-600 text-white",
                      status === "active" && "bg-blue-50 border-blue-600 text-blue-600 ring-4 ring-blue-600/20 dark:bg-blue-900/30",
                      status === "pending" && "bg-gray-100 border-gray-300 text-gray-400 dark:bg-gray-800 dark:border-gray-700",
                    )}
                  >
                    {status === "completed" ? <Check className="size-5" /> : <step.icon className="size-5" />}
                  </div>
                  <span
                    className={cn(
                      "mt-2 text-xs sm:text-sm font-medium text-center hidden sm:block",
                      status === "active" && "text-blue-600 dark:text-blue-400",
                      status === "completed" && "text-gray-900 dark:text-gray-100",
                      status === "pending" && "text-gray-500 dark:text-gray-400",
                    )}
                  >
                    {step.name}
                  </span>
                </div>

                {!isLast && (
                  <div
                    className={cn(
                      "flex-1 h-0.5 mx-2 sm:mx-4 transition-colors",
                      status === "completed" ? "bg-blue-600" : "bg-gray-300 dark:bg-gray-700",
                    )}
                  />
                )}
              </li>
            );
          })}
        </ol>
      </nav>

      {/* Selected Items Display */}
      {currentStep > 1 && (
        <div className="mb-4 p-3 bg-gradient-to-r from-blue-50/50 via-indigo-50/50 to-purple-50/50 dark:from-gray-800/50 dark:via-gray-800/50 dark:to-gray-800/50 rounded-xl border border-blue-200/50 dark:border-gray-700">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-medium text-gray-600 dark:text-gray-400 uppercase tracking-wide mr-1">Selected:</span>

            {/* Student chip with popover */}
            {selectedStudent && (
              <Popover>
                <PopoverTrigger asChild>
                  <div
                    className={cn(
                      'inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-all cursor-pointer group',
                      'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100 hover:border-blue-500/50 hover:bg-blue-50 dark:hover:bg-blue-900/20',
                    )}
                  >
                    <div className="flex items-center justify-center size-5 rounded-full bg-blue-600/20 text-blue-600 text-xs font-bold">
                      {selectedStudent.first_name[0]}
                    </div>
                    <span className="max-w-[120px] truncate">
                      {selectedStudent.first_name} {selectedStudent.last_name}
                    </span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        clearStudent()
                      }}
                      className="hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full p-0.5 transition-colors"
                      aria-label="Clear student selection"
                    >
                      <X className="size-3.5 text-gray-500 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-gray-100" />
                    </button>
                  </div>
                </PopoverTrigger>
                <PopoverContent className="w-64 p-0" align="start">
                  <div className="p-4 space-y-3">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center justify-center size-10 rounded-full bg-blue-600/10 text-blue-600 font-bold">
                        {selectedStudent.first_name[0]}
                        {selectedStudent.last_name[0]}
                      </div>
                      <div>
                        <p className="font-semibold text-gray-900 dark:text-gray-100">
                          {selectedStudent.first_name} {selectedStudent.last_name}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Student</p>
                      </div>
                    </div>
                    <div className="space-y-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                      <div className="flex items-center gap-2 text-sm">
                        <Hash className="size-4 text-gray-500 dark:text-gray-400" />
                        <span className="text-gray-500 dark:text-gray-400">ID:</span>
                        <span className="font-medium text-gray-900 dark:text-gray-100">{selectedStudent.admission_number}</span>
                      </div>
                      {selectedStudent.class_id && (
                        <div className="flex items-center gap-2 text-sm">
                          <GraduationCap className="size-4 text-gray-500 dark:text-gray-400" />
                          <span className="text-gray-500 dark:text-gray-400">Class:</span>
                          <span className="font-medium text-gray-900 dark:text-gray-100">Class {selectedStudent.class_id}</span>
                        </div>
                      )}
                      {/* TODO: Add enrolled fingers count when API is ready */}
                    </div>
                  </div>
                  <div className="px-4 py-2 bg-gray-50 dark:bg-gray-800/50 border-t border-gray-200 dark:border-gray-700">
                    <button
                      onClick={clearStudent}
                      className="text-xs text-gray-500 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400 transition-colors"
                    >
                      Change student
                    </button>
                  </div>
                </PopoverContent>
              </Popover>
            )}

            {/* Device chip with popover */}
            {selectedDevice && currentStep > 2 && (
              <Popover>
                <PopoverTrigger asChild>
                  <div
                    className={cn(
                      'inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-all cursor-pointer group',
                      'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100 hover:border-blue-500/50 hover:bg-blue-50 dark:hover:bg-blue-900/20',
                    )}
                  >
                    <Server className="size-4 text-green-600 dark:text-green-400" />
                    <span className="max-w-[100px] truncate">{selectedDevice.name}</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        clearDevice()
                      }}
                      className="hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full p-0.5 transition-colors"
                      aria-label="Clear device selection"
                    >
                      <X className="size-3.5 text-gray-500 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-gray-100" />
                    </button>
                  </div>
                </PopoverTrigger>
                <PopoverContent className="w-64 p-0" align="start">
                  <div className="p-4 space-y-3">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center justify-center size-10 rounded-lg bg-green-600/10 text-green-600">
                        <Server className="size-5" />
                      </div>
                      <div>
                        <p className="font-semibold text-gray-900 dark:text-gray-100">{selectedDevice.name}</p>
                        <div className="flex items-center gap-1">
                          <span className="relative flex size-2">
                            <span className="absolute inline-flex size-full animate-ping rounded-full bg-green-400 opacity-75" />
                            <span className="relative inline-flex size-2 rounded-full bg-green-600" />
                          </span>
                          <span className="text-xs text-green-600 dark:text-green-400">Online</span>
                        </div>
                      </div>
                    </div>
                    <div className="space-y-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                      {selectedDevice.location && (
                        <div className="flex items-center gap-2 text-sm">
                          <MapPin className="size-4 text-gray-500 dark:text-gray-400" />
                          <span className="text-gray-500 dark:text-gray-400">Location:</span>
                          <span className="font-medium text-xs text-gray-900 dark:text-gray-100">{selectedDevice.location}</span>
                        </div>
                      )}
                      <div className="flex items-center gap-2 text-sm">
                        <Wifi className="size-4 text-gray-500 dark:text-gray-400" />
                        <span className="text-gray-500 dark:text-gray-400">IP:</span>
                        <span className="font-medium font-mono text-xs text-gray-900 dark:text-gray-100">
                          {selectedDevice.ip_address}:{selectedDevice.port}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="px-4 py-2 bg-gray-50 dark:bg-gray-800/50 border-t border-gray-200 dark:border-gray-700">
                    <button
                      onClick={clearDevice}
                      className="text-xs text-gray-500 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400 transition-colors"
                    >
                      Change device
                    </button>
                  </div>
                </PopoverContent>
              </Popover>
            )}

            {/* Finger chip with popover */}
            {fingerInfo && currentStep > 3 && (
              <Popover>
                <PopoverTrigger asChild>
                  <div
                    className={cn(
                      'inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-all cursor-pointer group',
                      'bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 text-gray-900 dark:text-gray-100 hover:border-blue-500/50 hover:bg-blue-50 dark:hover:bg-blue-900/20',
                    )}
                  >
                    <Fingerprint className="size-4 text-blue-600 dark:text-blue-400" />
                    <span>{fingerInfo.name}</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        clearFinger()
                      }}
                      className="hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full p-0.5 transition-colors"
                      aria-label="Clear finger selection"
                    >
                      <X className="size-3.5 text-gray-500 dark:text-gray-400 group-hover:text-gray-900 dark:group-hover:text-gray-100" />
                    </button>
                  </div>
                </PopoverTrigger>
                <PopoverContent className="w-56 p-0" align="start">
                  <div className="p-4 space-y-3">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center justify-center size-10 rounded-lg bg-blue-600/10 text-blue-600">
                        <Fingerprint className="size-5" />
                      </div>
                      <div>
                        <p className="font-semibold text-gray-900 dark:text-gray-100">{fingerInfo.name}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Selected for enrollment</p>
                      </div>
                    </div>
                    <div className="space-y-2 pt-2 border-t border-gray-200 dark:border-gray-700">
                      <div className="flex items-center gap-2 text-sm">
                        <Hand className="size-4 text-gray-500 dark:text-gray-400" />
                        <span className="text-gray-500 dark:text-gray-400">Hand:</span>
                        <span className="font-medium capitalize text-gray-900 dark:text-gray-100">{fingerInfo.hand}</span>
                      </div>
                      {fingerInfo.recommended && (
                        <div className="flex items-center gap-2">
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400">
                            Recommended
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="px-4 py-2 bg-gray-50 dark:bg-gray-800/50 border-t border-gray-200 dark:border-gray-700">
                    <button
                      onClick={clearFinger}
                      className="text-xs text-gray-500 dark:text-gray-400 hover:text-red-600 dark:hover:text-red-400 transition-colors"
                    >
                      Change finger
                    </button>
                  </div>
                </PopoverContent>
              </Popover>
            )}
          </div>
        </div>
      )}

      {/* Step Content */}
      <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl border border-gray-200/50 dark:border-gray-700/50 shadow-lg overflow-hidden">
        <div className="p-6 sm:p-8">
          {/* Step Header */}
          {currentStep < 4 && (
            <div className="mb-6">
              <h2 className="text-2xl font-semibold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">{STEPS[currentStep - 1].name}</h2>
              <p className="text-gray-600 dark:text-gray-400 mt-1">{STEPS[currentStep - 1].description}</p>
            </div>
          )}

          {/* Step 1: Student Selection */}
          {currentStep === 1 && <StudentSelector selectedStudent={selectedStudent} onSelect={setSelectedStudent} />}

          {/* Step 2: Device Selection */}
          {currentStep === 2 && <DeviceSelector selectedDevice={selectedDevice} onSelect={setSelectedDevice} />}

          {/* Step 3: Finger Selection */}
          {currentStep === 3 && (
            <FingerSelector selectedFinger={selectedFinger} onSelect={setSelectedFinger} student={selectedStudent} />
          )}

          {/* Step 4: Capture */}
          {currentStep === 4 && selectedStudent && selectedDevice && selectedFinger !== null && (
            <EnrollmentCapture
              student={selectedStudent}
              device={selectedDevice}
              fingerId={selectedFinger}
              onComplete={handleEnrollmentComplete}
              onRetry={handleEnrollAnother}
              onCancel={handlePrevious}
            />
          )}
        </div>

        {/* Navigation Footer */}
        {currentStep < 4 && (
          <div className="flex items-center justify-between px-6 sm:px-8 py-4 bg-gradient-to-r from-blue-50/50 to-purple-50/50 dark:from-gray-800/30 dark:to-gray-800/30 border-t border-gray-200 dark:border-gray-700">
            <Button variant="ghost" onClick={handlePrevious} disabled={currentStep === 1} className="gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100">
              <ChevronLeft className="size-4" />
              Back
            </Button>

            <Button onClick={handleNext} disabled={!canProceed()} className="gap-2 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg hover:shadow-xl transition-all">
              {currentStep === 3 ? (
                <>
                  Start Capture
                  <Play className="size-4" />
                </>
              ) : (
                <>
                  Continue
                  <ChevronRight className="size-4" />
                </>
              )}
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}
