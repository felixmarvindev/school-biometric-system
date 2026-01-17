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
import { StudentSelector } from "./student-selector"
import { DeviceSelector } from "./device-selector"
import { FingerSelector } from "./finger-selector"
import { EnrollmentCapture } from "./enrollment-capture"
import { type Student, type Device, FINGERS } from "@/lib/demo-data"

const STEPS = [
  { id: 1, name: "Select Student", icon: User, description: "Choose a student to enroll" },
  { id: 2, name: "Choose Device", icon: Server, description: "Select biometric scanner" },
  { id: 3, name: "Select Finger", icon: Fingerprint, description: "Pick finger to enroll" },
  { id: 4, name: "Capture", icon: Play, description: "Complete enrollment" },
]

export function EnrollmentWizard() {
  const [currentStep, setCurrentStep] = useState(1)
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null)
  const [selectedDevice, setSelectedDevice] = useState<Device | null>(null)
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

  const handleEnrollmentComplete = () => {
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

  const fingerInfo = FINGERS.find((f) => f.id === selectedFinger)

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
            const status = getStepStatus(step.id)
            const isLast = index === STEPS.length - 1

            return (
              <li key={step.id} className={cn("flex items-center", !isLast && "flex-1")}>
                <div className="flex flex-col items-center">
                  <div
                    className={cn(
                      "flex items-center justify-center size-10 sm:size-12 rounded-full border-2 transition-all",
                      status === "completed" && "bg-primary border-primary text-primary-foreground",
                      status === "active" && "bg-primary/10 border-primary text-primary ring-4 ring-primary/20",
                      status === "pending" && "bg-muted border-border text-muted-foreground",
                    )}
                  >
                    {status === "completed" ? <Check className="size-5" /> : <step.icon className="size-5" />}
                  </div>
                  <span
                    className={cn(
                      "mt-2 text-xs sm:text-sm font-medium text-center hidden sm:block",
                      status === "active" && "text-primary",
                      status === "completed" && "text-foreground",
                      status === "pending" && "text-muted-foreground",
                    )}
                  >
                    {step.name}
                  </span>
                </div>

                {!isLast && (
                  <div
                    className={cn(
                      "flex-1 h-0.5 mx-2 sm:mx-4 transition-colors",
                      status === "completed" ? "bg-primary" : "bg-border",
                    )}
                  />
                )}
              </li>
            )
          })}
        </ol>
      </nav>

      {currentStep > 1 && (
        <div className="mb-4 p-3 bg-muted/40 rounded-xl border border-border">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs font-medium text-muted-foreground uppercase tracking-wide mr-1">Selected:</span>

            {/* Student chip with popover */}
            {selectedStudent && (
              <Popover>
                <PopoverTrigger asChild>
                  <div
                    className={cn(
                      "inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-all cursor-pointer group",
                      "bg-background border border-border text-foreground hover:border-primary/50 hover:bg-primary/5",
                    )}
                  >
                    <div className="flex items-center justify-center size-5 rounded-full bg-primary/20 text-primary text-xs font-bold">
                      {selectedStudent.firstName[0]}
                    </div>
                    <span className="max-w-[120px] truncate">
                      {selectedStudent.firstName} {selectedStudent.lastName}
                    </span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        clearStudent()
                      }}
                      className="hover:bg-muted rounded-full p-0.5 transition-colors"
                      aria-label="Clear student selection"
                    >
                      <X className="size-3.5 text-muted-foreground group-hover:text-foreground" />
                    </button>
                  </div>
                </PopoverTrigger>
                <PopoverContent className="w-64 p-0" align="start">
                  <div className="p-4 space-y-3">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center justify-center size-10 rounded-full bg-primary/10 text-primary font-bold">
                        {selectedStudent.firstName[0]}
                        {selectedStudent.lastName[0]}
                      </div>
                      <div>
                        <p className="font-semibold text-foreground">
                          {selectedStudent.firstName} {selectedStudent.lastName}
                        </p>
                        <p className="text-xs text-muted-foreground">Student</p>
                      </div>
                    </div>
                    <div className="space-y-2 pt-2 border-t border-border">
                      <div className="flex items-center gap-2 text-sm">
                        <Hash className="size-4 text-muted-foreground" />
                        <span className="text-muted-foreground">ID:</span>
                        <span className="font-medium">{selectedStudent.admissionNumber}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <GraduationCap className="size-4 text-muted-foreground" />
                        <span className="text-muted-foreground">Class:</span>
                        <span className="font-medium">{selectedStudent.className}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <Fingerprint className="size-4 text-muted-foreground" />
                        <span className="text-muted-foreground">Enrolled:</span>
                        <span className="font-medium">{selectedStudent.enrolledFingers.length} finger(s)</span>
                      </div>
                    </div>
                  </div>
                  <div className="px-4 py-2 bg-muted/50 border-t border-border">
                    <button
                      onClick={clearStudent}
                      className="text-xs text-muted-foreground hover:text-destructive transition-colors"
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
                      "inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-all cursor-pointer group",
                      "bg-background border border-border text-foreground hover:border-primary/50 hover:bg-primary/5",
                    )}
                  >
                    <Server className="size-4 text-emerald-500" />
                    <span className="max-w-[100px] truncate">{selectedDevice.name}</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        clearDevice()
                      }}
                      className="hover:bg-muted rounded-full p-0.5 transition-colors"
                      aria-label="Clear device selection"
                    >
                      <X className="size-3.5 text-muted-foreground group-hover:text-foreground" />
                    </button>
                  </div>
                </PopoverTrigger>
                <PopoverContent className="w-64 p-0" align="start">
                  <div className="p-4 space-y-3">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center justify-center size-10 rounded-lg bg-emerald-500/10 text-emerald-500">
                        <Server className="size-5" />
                      </div>
                      <div>
                        <p className="font-semibold text-foreground">{selectedDevice.name}</p>
                        <div className="flex items-center gap-1">
                          <span className="relative flex size-2">
                            <span className="absolute inline-flex size-full animate-ping rounded-full bg-emerald-400 opacity-75" />
                            <span className="relative inline-flex size-2 rounded-full bg-emerald-500" />
                          </span>
                          <span className="text-xs text-emerald-600">Online</span>
                        </div>
                      </div>
                    </div>
                    <div className="space-y-2 pt-2 border-t border-border">
                      <div className="flex items-center gap-2 text-sm">
                        <MapPin className="size-4 text-muted-foreground" />
                        <span className="text-muted-foreground">Location:</span>
                        <span className="font-medium text-xs">{selectedDevice.location}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <Wifi className="size-4 text-muted-foreground" />
                        <span className="text-muted-foreground">IP:</span>
                        <span className="font-medium font-mono text-xs">
                          {selectedDevice.ipAddress}:{selectedDevice.port}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <Server className="size-4 text-muted-foreground" />
                        <span className="text-muted-foreground">Model:</span>
                        <span className="font-medium">{selectedDevice.model}</span>
                      </div>
                    </div>
                  </div>
                  <div className="px-4 py-2 bg-muted/50 border-t border-border">
                    <button
                      onClick={clearDevice}
                      className="text-xs text-muted-foreground hover:text-destructive transition-colors"
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
                      "inline-flex items-center gap-2 px-3 py-1.5 rounded-full text-sm font-medium transition-all cursor-pointer group",
                      "bg-background border border-border text-foreground hover:border-primary/50 hover:bg-primary/5",
                    )}
                  >
                    <Fingerprint className="size-4 text-primary" />
                    <span>{fingerInfo.name}</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        clearFinger()
                      }}
                      className="hover:bg-muted rounded-full p-0.5 transition-colors"
                      aria-label="Clear finger selection"
                    >
                      <X className="size-3.5 text-muted-foreground group-hover:text-foreground" />
                    </button>
                  </div>
                </PopoverTrigger>
                <PopoverContent className="w-56 p-0" align="start">
                  <div className="p-4 space-y-3">
                    <div className="flex items-center gap-3">
                      <div className="flex items-center justify-center size-10 rounded-lg bg-primary/10 text-primary">
                        <Fingerprint className="size-5" />
                      </div>
                      <div>
                        <p className="font-semibold text-foreground">{fingerInfo.name}</p>
                        <p className="text-xs text-muted-foreground">Selected for enrollment</p>
                      </div>
                    </div>
                    <div className="space-y-2 pt-2 border-t border-border">
                      <div className="flex items-center gap-2 text-sm">
                        <Hand className="size-4 text-muted-foreground" />
                        <span className="text-muted-foreground">Hand:</span>
                        <span className="font-medium capitalize">{fingerInfo.hand}</span>
                      </div>
                      {fingerInfo.recommended && (
                        <div className="flex items-center gap-2">
                          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-700">
                            Recommended
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="px-4 py-2 bg-muted/50 border-t border-border">
                    <button
                      onClick={clearFinger}
                      className="text-xs text-muted-foreground hover:text-destructive transition-colors"
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
      <div className="bg-card rounded-2xl border border-border shadow-sm overflow-hidden">
        <div className="p-6 sm:p-8">
          {/* Step Header */}
          {currentStep < 4 && (
            <div className="mb-6">
              <h2 className="text-2xl font-semibold text-foreground">{STEPS[currentStep - 1].name}</h2>
              <p className="text-muted-foreground mt-1">{STEPS[currentStep - 1].description}</p>
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
          <div className="flex items-center justify-between px-6 sm:px-8 py-4 bg-muted/30 border-t border-border">
            <Button variant="ghost" onClick={handlePrevious} disabled={currentStep === 1} className="gap-2">
              <ChevronLeft className="size-4" />
              Back
            </Button>

            <Button onClick={handleNext} disabled={!canProceed()} className="gap-2">
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
