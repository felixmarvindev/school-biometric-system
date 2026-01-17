"use client"

import { useState, useEffect } from "react"
import { Fingerprint, CheckCircle2, AlertCircle, RefreshCw } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { cn } from "@/lib/utils"
import { type Student, type Device, FINGERS } from "@/lib/demo-data"

interface EnrollmentCaptureProps {
  student: Student
  device: Device
  fingerId: number
  onComplete: () => void
  onRetry: () => void
  onCancel: () => void
}

type CaptureStatus = "waiting" | "scanning" | "processing" | "success" | "error"

const STATUS_MESSAGES: Record<CaptureStatus, string> = {
  waiting: "Place your finger on the scanner",
  scanning: "Scanning fingerprint...",
  processing: "Processing fingerprint data...",
  success: "Fingerprint enrolled successfully!",
  error: "Failed to capture fingerprint",
}

export function EnrollmentCapture({
  student,
  device,
  fingerId,
  onComplete,
  onRetry,
  onCancel,
}: EnrollmentCaptureProps) {
  const [status, setStatus] = useState<CaptureStatus>("waiting")
  const [progress, setProgress] = useState(0)
  const [captureAttempt, setCaptureAttempt] = useState(1)
  const maxAttempts = 3

  const fingerInfo = FINGERS.find((f) => f.id === fingerId)

  // Simulate enrollment process
  useEffect(() => {
    if (status === "waiting") {
      const timer = setTimeout(() => {
        setStatus("scanning")
        setProgress(20)
      }, 2000)
      return () => clearTimeout(timer)
    }

    if (status === "scanning") {
      const timer = setTimeout(() => {
        setStatus("processing")
        setProgress(60)
      }, 2500)
      return () => clearTimeout(timer)
    }

    if (status === "processing") {
      const timer = setTimeout(() => {
        // Simulate 85% success rate
        const isSuccess = Math.random() > 0.15
        if (isSuccess) {
          setStatus("success")
          setProgress(100)
        } else {
          setStatus("error")
          setProgress(0)
        }
      }, 2000)
      return () => clearTimeout(timer)
    }
  }, [status])

  const handleRetry = () => {
    if (captureAttempt < maxAttempts) {
      setCaptureAttempt((prev) => prev + 1)
      setStatus("waiting")
      setProgress(0)
    }
  }

  return (
    <div className="flex flex-col items-center text-center space-y-8">
      {/* Fingerprint Animation */}
      <div className="relative">
        <div
          className={cn(
            "flex items-center justify-center size-40 rounded-full transition-all duration-500",
            status === "waiting" && "bg-muted",
            status === "scanning" && "bg-primary/10 animate-pulse",
            status === "processing" && "bg-primary/20",
            status === "success" && "bg-success/10",
            status === "error" && "bg-destructive/10",
          )}
        >
          {status === "success" ? (
            <CheckCircle2 className="size-20 text-success" />
          ) : status === "error" ? (
            <AlertCircle className="size-20 text-destructive" />
          ) : (
            <Fingerprint
              className={cn(
                "size-20 transition-colors",
                status === "waiting" && "text-muted-foreground",
                (status === "scanning" || status === "processing") && "text-primary animate-pulse",
              )}
            />
          )}
        </div>

        {/* Scanning ring animation */}
        {(status === "scanning" || status === "processing") && (
          <div className="absolute inset-0 rounded-full border-4 border-primary/30 animate-ping" />
        )}
      </div>

      {/* Status Message */}
      <div className="space-y-2">
        <h3
          className={cn(
            "text-xl font-semibold",
            status === "success" && "text-success",
            status === "error" && "text-destructive",
          )}
        >
          {STATUS_MESSAGES[status]}
        </h3>
        <p className="text-muted-foreground">
          {status === "waiting" && `${fingerInfo?.name} on ${device.name}`}
          {status === "scanning" && "Keep your finger steady..."}
          {status === "processing" && "Almost done..."}
          {status === "success" && `${fingerInfo?.name} has been enrolled for ${student.firstName}`}
          {status === "error" && `Attempt ${captureAttempt} of ${maxAttempts} failed`}
        </p>
      </div>

      {/* Progress Bar */}
      {status !== "success" && status !== "error" && (
        <div className="w-full max-w-xs">
          <Progress value={progress} className="h-2" />
          <p className="text-xs text-muted-foreground mt-2">
            {status === "waiting"
              ? "Waiting for fingerprint..."
              : status === "scanning"
                ? "Capturing image..."
                : "Analyzing quality..."}
          </p>
        </div>
      )}

      {/* Action Buttons */}
      <div className="flex items-center gap-3">
        {status === "success" && (
          <>
            <Button variant="outline" onClick={onRetry}>
              Enroll Another Finger
            </Button>
            <Button onClick={onComplete}>Done</Button>
          </>
        )}

        {status === "error" && (
          <>
            {captureAttempt < maxAttempts ? (
              <>
                <Button variant="outline" onClick={onCancel}>
                  Cancel
                </Button>
                <Button onClick={handleRetry}>
                  <RefreshCw className="size-4 mr-2" />
                  Try Again ({maxAttempts - captureAttempt} left)
                </Button>
              </>
            ) : (
              <>
                <Button variant="outline" onClick={onCancel}>
                  Go Back
                </Button>
                <Button variant="destructive" onClick={onRetry}>
                  Select Different Finger
                </Button>
              </>
            )}
          </>
        )}

        {(status === "waiting" || status === "scanning" || status === "processing") && (
          <Button variant="outline" onClick={onCancel}>
            Cancel
          </Button>
        )}
      </div>

      {/* Enrollment Info Card */}
      <div className="w-full max-w-md p-4 rounded-xl bg-muted/30 border border-border">
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div>
            <p className="text-muted-foreground">Student</p>
            <p className="font-medium truncate">
              {student.firstName} {student.lastName}
            </p>
          </div>
          <div>
            <p className="text-muted-foreground">Device</p>
            <p className="font-medium truncate">{device.name}</p>
          </div>
          <div>
            <p className="text-muted-foreground">Finger</p>
            <p className="font-medium">{fingerInfo?.name}</p>
          </div>
        </div>
      </div>
    </div>
  )
}
