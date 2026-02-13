"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { AnimatePresence, motion } from "framer-motion"
import {
  User,
  GraduationCap,
  Server,
  Fingerprint,
  ChevronRight,
  ChevronLeft,
  Check,
  Loader2,
  AlertCircle,
  Plus,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { cn } from "@/lib/utils"
import { slideIn, pageTransition } from "@/lib/animations/framer-motion"
import { StepIndicator, type StepDef } from "./StepIndicator"
import { useAuthStore } from "@/lib/store/authStore"
import {
  createStudent,
  updateStudent,
  getStudent,
  type StudentResponse,
  StudentApiError,
} from "@/lib/api/students"
import { listClasses, type ClassResponse } from "@/lib/api/classes"
import { listStreams, type StreamResponse } from "@/lib/api/streams"
import { listDevices, type DeviceResponse } from "@/lib/api/devices"
import { syncStudentToDevice, getSyncStatus } from "@/lib/api/sync"
import { startEnrollment, EnrollmentApiError } from "@/lib/api/enrollment"
import { step1PersonalSchema, step2ClassSchema, type Step1PersonalData, type Step2ClassData } from "@/lib/validations/studentWizard"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { toast } from "sonner"
import { EnrollmentCapture } from "@/components/features/enrollment/EnrollmentCapture"
import { FingerSelector } from "@/components/features/enrollment/FingerSelector"
import { DeviceStatusBadge } from "@/components/features/devices/DeviceStatusBadge"

const STEPS: StepDef[] = [
  { id: 1, name: "Personal", icon: User, description: "Student details" },
  { id: 2, name: "Class", icon: GraduationCap, description: "Class assignment" },
  { id: 3, name: "Sync", icon: Server, description: "Device sync", optional: true },
  { id: 4, name: "Fingerprint", icon: Fingerprint, description: "Enrollment", optional: true },
]

interface StudentWizardProps {
  mode: "add" | "edit"
  studentId?: number
}

export function StudentWizard({ mode, studentId }: StudentWizardProps) {
  const router = useRouter()
  const { token } = useAuthStore()
  const [currentStep, setCurrentStep] = useState(1)
  const [student, setStudent] = useState<StudentResponse | null>(null)
  const [isFetching, setIsFetching] = useState(mode === "edit" && !!studentId)
  const [error, setError] = useState<string | null>(null)
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})

  // Step 1 form
  const step1Form = useForm<Step1PersonalData>({
    resolver: zodResolver(step1PersonalSchema),
    defaultValues: {
      first_name: "",
      last_name: "",
      date_of_birth: null,
      gender: null,
      parent_phone: null,
      parent_email: null,
    },
  })

  // Step 2 form
  const step2Form = useForm<Step2ClassData>({
    resolver: zodResolver(step2ClassSchema),
    defaultValues: {
      admission_number: "",
      class_id: null,
      stream_id: null,
    },
  })

  // Step 3: sync
  const [devices, setDevices] = useState<DeviceResponse[]>([])
  const [selectedDeviceIds, setSelectedDeviceIds] = useState<Set<number>>(new Set())
  const [syncedDeviceIds, setSyncedDeviceIds] = useState<Set<number>>(new Set())
  const [isSyncing, setIsSyncing] = useState(false)
  const [syncProgress, setSyncProgress] = useState<Record<number, "idle" | "syncing" | "done" | "error">>({})

  // Step 4: enrollment
  const [enrollmentDevice, setEnrollmentDevice] = useState<DeviceResponse | null>(null)
  const [enrollmentFinger, setEnrollmentFinger] = useState<number | null>(null)
  const [enrollmentSession, setEnrollmentSession] = useState<{ session_id: string } | null>(null)
  const [classes, setClasses] = useState<ClassResponse[]>([])
  const [streams, setStreams] = useState<StreamResponse[]>([])
  const [isLoadingClasses, setIsLoadingClasses] = useState(false)

  const step2Values = step2Form.watch()
  const selectedClassId = step2Values.class_id

  // Fetch student when editing
  useEffect(() => {
    if (mode === "edit" && studentId != null && !isNaN(studentId) && token) {
      setIsFetching(true)
      getStudent(token, studentId)
        .then((s) => {
          setStudent(s)
          step1Form.reset({
            first_name: s.first_name,
            last_name: s.last_name,
            date_of_birth: s.date_of_birth ? s.date_of_birth.split("T")[0] : null,
            gender: s.gender || null,
            parent_phone: s.parent_phone || null,
            parent_email: s.parent_email || null,
          })
          step2Form.reset({
            admission_number: s.admission_number,
            class_id: s.class_id || null,
            stream_id: s.stream_id || null,
          })
        })
        .catch((err) => {
          setError(err instanceof StudentApiError ? err.message : "Failed to load student")
        })
        .finally(() => setIsFetching(false))
    }
  }, [mode, studentId, token])

  // Fetch classes
  useEffect(() => {
    if (token) {
      setIsLoadingClasses(true)
      listClasses(token)
        .then(setClasses)
        .catch(() => setClasses([]))
        .finally(() => setIsLoadingClasses(false))
    }
  }, [token])

  // Fetch streams when class changes
  useEffect(() => {
    if (token && selectedClassId) {
      listStreams(token, selectedClassId)
        .then((data) => {
          setStreams(data)
          const currentStreamId = step2Form.getValues("stream_id")
          if (currentStreamId && !data.some((s) => s.id === currentStreamId)) {
            step2Form.setValue("stream_id", null)
          }
        })
        .catch(() => setStreams([]))
    } else {
      setStreams([])
      step2Form.setValue("stream_id", null)
    }
  }, [token, selectedClassId, step2Form])

  // Fetch devices for step 3
  useEffect(() => {
    if (currentStep >= 3 && token && student) {
      listDevices(token, { page_size: 100, status: "online" })
        .then((r) => setDevices(r.items))
        .catch(() => setDevices([]))
    }
  }, [currentStep, token, student])

  // In edit mode, check which devices student is already synced to when Step 3 loads
  useEffect(() => {
    if (mode !== "edit" || currentStep !== 3 || !student?.id || devices.length === 0) return
    const check = async () => {
      const results = await Promise.allSettled(
        devices.map((d) => getSyncStatus(d.id, student.id))
      )
      const alreadySynced = new Set<number>()
      results.forEach((r, i) => {
        if (r.status === "fulfilled" && r.value.synced) {
          alreadySynced.add(devices[i].id)
        }
      })
      setSyncedDeviceIds((prev) => new Set([...prev, ...alreadySynced]))
    }
    check()
  }, [mode, currentStep, student?.id, devices])

  const handleStep1Next = async () => {
    setError(null)
    setFieldErrors({})
    const valid = await step1Form.trigger()
    if (!valid) return

    if (mode === "edit" && student) {
      try {
        const data = step1Form.getValues()
        const updated = await updateStudent(token!, student.id, {
          first_name: data.first_name,
          last_name: data.last_name,
          date_of_birth: data.date_of_birth || null,
          gender: data.gender || null,
          parent_phone: data.parent_phone || null,
          parent_email: data.parent_email || null,
        })
        setStudent(updated)
        toast.success("Personal info saved")
        setCurrentStep(2)
      } catch (err) {
        if (err instanceof StudentApiError) {
          setError(err.message)
          if (err.fieldErrors) setFieldErrors(err.fieldErrors)
        } else setError("Failed to save")
      }
    } else {
      setCurrentStep(2)
    }
  }

  const handleStep2Next = async () => {
    setError(null)
    setFieldErrors({})
    const valid = await step2Form.trigger()
    if (!valid) return

    try {
      if (mode === "add") {
        const personal = step1Form.getValues()
        const classData = step2Form.getValues()
        const created = await createStudent(token!, {
          admission_number: classData.admission_number,
          first_name: personal.first_name,
          last_name: personal.last_name,
          date_of_birth: personal.date_of_birth || null,
          gender: personal.gender || null,
          class_id: classData.class_id || null,
          stream_id: classData.stream_id || null,
          parent_phone: personal.parent_phone || null,
          parent_email: personal.parent_email || null,
        })
        setStudent(created)
        toast.success("Student created")
      } else if (student) {
        const classData = step2Form.getValues()
        const updated = await updateStudent(token!, student.id, {
          class_id: classData.class_id || null,
          stream_id: classData.stream_id || null,
        })
        setStudent(updated)
        toast.success("Class assignment saved")
      }
      setCurrentStep(3)
    } catch (err) {
      if (err instanceof StudentApiError) {
        setError(err.message)
        if (err.fieldErrors) setFieldErrors(err.fieldErrors)
        if (err.statusCode === 409) {
          setFieldErrors((p) => ({ ...p, admission_number: "Admission number already exists for this school" }))
        }
      } else setError("Failed to save")
    }
  }

  const toggleDevice = (id: number) => {
    setSelectedDeviceIds((prev) => {
      const next = new Set(prev)
      if (next.has(id)) next.delete(id)
      else next.add(id)
      return next
    })
  }

  const handleSyncSelected = async () => {
    if (!student) return
    setIsSyncing(true)
    for (const deviceId of selectedDeviceIds) {
      setSyncProgress((p) => ({ ...p, [deviceId]: "syncing" }))
      try {
        await syncStudentToDevice(student.id, deviceId)
        setSyncedDeviceIds((s) => new Set(s).add(deviceId))
        setSyncProgress((p) => ({ ...p, [deviceId]: "done" }))
        toast.success(`Synced to ${devices.find((d) => d.id === deviceId)?.name}`)
      } catch {
        setSyncProgress((p) => ({ ...p, [deviceId]: "error" }))
        toast.error(`Failed to sync to ${devices.find((d) => d.id === deviceId)?.name}`)
      }
    }
    setIsSyncing(false)
  }

  const handleStep3Next = () => {
    setCurrentStep(4)
  }

  const handleStep3Skip = () => {
    setCurrentStep(4)
  }

  const handleStartEnrollment = async () => {
    if (!student || !enrollmentDevice || enrollmentFinger === null || !token) return
    setError(null)
    try {
      const res = await startEnrollment({
        student_id: student.id,
        device_id: enrollmentDevice.id,
        finger_id: enrollmentFinger,
      })
      setEnrollmentSession(res ? { session_id: res.session_id } : null)
      toast.success("Enrollment started")
    } catch (err) {
      if (err instanceof EnrollmentApiError) {
        setError(err.message)
        if (err.statusCode === 400) {
          toast.error("Student not synced to device. Please sync in the previous step first.")
        }
      } else setError("Failed to start enrollment")
    }
  }

  const handleEnrollmentComplete = () => {
    toast.success("Fingerprint enrolled successfully")
    router.push(`/dashboard/students/${student?.id}`)
  }

  const handleEnrollmentSkip = () => {
    router.push(`/dashboard/students/${student?.id}`)
  }

  if (mode === "edit" && (studentId == null || isNaN(studentId))) {
    return (
      <Alert variant="destructive">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>Invalid student ID</AlertDescription>
      </Alert>
    )
  }

  if (isFetching) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    )
  }

  return (
    <motion.div
      variants={pageTransition}
      initial="initial"
      animate="animate"
      className="w-full max-w-3xl mx-auto space-y-8"
    >
      <Button variant="ghost" onClick={() => router.back()} className="text-muted-foreground hover:text-foreground -ml-1">
        <ChevronLeft className="mr-2 h-4 w-4" />
        Back
      </Button>

      {/* Header */}
      <div className="text-center space-y-1">
        <h1 className="text-2xl font-bold tracking-tight text-foreground">
          {mode === "add" ? "Add New Student" : "Edit Student"}
        </h1>
        <p className="text-muted-foreground text-sm">
          {mode === "add" ? "Complete the steps below to register a student" : "Update student information"}
        </p>
      </div>

      {/* Step Indicator */}
      <StepIndicator steps={STEPS} currentStep={currentStep} />

      {/* Step Content Card */}
      <div className="bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm border border-gray-200 dark:border-gray-700 rounded-2xl p-6 sm:p-8 shadow-lg shadow-blue-500/5">
        {error && (
          <Alert variant="destructive" className="mb-6">
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>{error}</AlertDescription>
          </Alert>
        )}

        <AnimatePresence mode="wait">
          {/* Step 1: Personal Info */}
          {currentStep === 1 && (
            <motion.form
              key="step1"
              variants={slideIn}
              initial="initial"
              animate="animate"
              exit="exit"
              onSubmit={(e) => { e.preventDefault(); handleStep1Next() }}
              className="space-y-6"
            >
              <div>
                <p className="text-sm text-muted-foreground">
                  Enter the student&apos;s personal information to get started.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div className="space-y-1.5">
                  <Label htmlFor="first_name" className="text-sm font-medium">
                    First Name <span className="text-destructive">*</span>
                  </Label>
                  <Input
                    id="first_name"
                    {...step1Form.register("first_name")}
                    placeholder="John"
                    className="h-11 border-blue-300 focus:border-blue-500"
                  />
                  {step1Form.formState.errors.first_name && (
                    <p className="text-xs text-destructive">{step1Form.formState.errors.first_name.message}</p>
                  )}
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="last_name" className="text-sm font-medium">
                    Last Name <span className="text-destructive">*</span>
                  </Label>
                  <Input
                    id="last_name"
                    {...step1Form.register("last_name")}
                    placeholder="Doe"
                    className="h-11 border-blue-300 focus:border-blue-500"
                  />
                  {step1Form.formState.errors.last_name && (
                    <p className="text-xs text-destructive">{step1Form.formState.errors.last_name.message}</p>
                  )}
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="date_of_birth" className="text-sm font-medium">
                    Date of Birth
                  </Label>
                  <Input
                    id="date_of_birth"
                    type="date"
                    value={step1Form.watch("date_of_birth") || ""}
                    onChange={(e) => step1Form.setValue("date_of_birth", e.target.value || null)}
                    max={new Date().toISOString().split("T")[0]}
                    className="h-11"
                  />
                </div>
                <div className="space-y-1.5">
                  <Label className="text-sm font-medium">Gender</Label>
                  <Select
                    value={step1Form.watch("gender") || "none"}
                    onValueChange={(v) => step1Form.setValue("gender", v === "none" ? null : (v as "male" | "female" | "other"))}
                  >
                    <SelectTrigger className="h-11">
                      <SelectValue placeholder="Select gender" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">Not specified</SelectItem>
                      <SelectItem value="male">Male</SelectItem>
                      <SelectItem value="female">Female</SelectItem>
                      <SelectItem value="other">Other</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="parent_phone" className="text-sm font-medium">
                    Parent Phone
                  </Label>
                  <Input
                    id="parent_phone"
                    {...step1Form.register("parent_phone")}
                    type="tel"
                    placeholder="+254 712 345 678"
                    className="h-11"
                  />
                  {step1Form.formState.errors.parent_phone && (
                    <p className="text-xs text-destructive">{step1Form.formState.errors.parent_phone.message}</p>
                  )}
                </div>
                <div className="space-y-1.5">
                  <Label htmlFor="parent_email" className="text-sm font-medium">
                    Parent Email
                  </Label>
                  <Input
                    id="parent_email"
                    {...step1Form.register("parent_email")}
                    type="email"
                    placeholder="parent@example.com"
                    className="h-11"
                  />
                  {step1Form.formState.errors.parent_email && (
                    <p className="text-xs text-destructive">{step1Form.formState.errors.parent_email.message}</p>
                  )}
                </div>
              </div>

              <div className="flex justify-end pt-2">
                <Button type="submit" size="lg" className="gap-2 bg-blue-600 hover:bg-blue-700">
                  Continue <ChevronRight className="size-4" />
                </Button>
              </div>
            </motion.form>
          )}

          {/* Step 2: Class Assignment */}
          {currentStep === 2 && (
            <motion.form
              key="step2"
              variants={slideIn}
              initial="initial"
              animate="animate"
              exit="exit"
              onSubmit={(e) => { e.preventDefault(); handleStep2Next() }}
              className="space-y-6"
            >
              <div>
                <p className="text-sm text-muted-foreground">
                  Assign an admission number and class to the student.
                </p>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                <div className="space-y-1.5 sm:col-span-2">
                  <Label htmlFor="admission_number" className="text-sm font-medium">
                    Admission Number <span className="text-destructive">*</span>
                  </Label>
                  <Input
                    id="admission_number"
                    {...step2Form.register("admission_number")}
                    disabled={mode === "edit"}
                    placeholder="STD-001"
                    className="h-11 font-mono max-w-xs border-blue-300 focus:border-blue-500"
                  />
                  {step2Form.formState.errors.admission_number && (
                    <p className="text-xs text-destructive">{step2Form.formState.errors.admission_number.message}</p>
                  )}
                  {fieldErrors.admission_number && (
                    <p className="text-xs text-destructive">{fieldErrors.admission_number}</p>
                  )}
                </div>
                <div className="space-y-1.5">
                  <Label className="text-sm font-medium">Class</Label>
                  <Select
                    value={step2Form.watch("class_id")?.toString() || "none"}
                    onValueChange={(v) => step2Form.setValue("class_id", v === "none" ? null : parseInt(v))}
                  >
                    <SelectTrigger className="h-11">
                      <SelectValue placeholder="Select class" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">Not assigned</SelectItem>
                      {classes.map((c) => (
                        <SelectItem key={c.id} value={c.id.toString()}>
                          {c.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-1.5">
                  <Label className="text-sm font-medium">Stream</Label>
                  <Select
                    value={step2Form.watch("stream_id")?.toString() || "none"}
                    onValueChange={(v) => step2Form.setValue("stream_id", v === "none" ? null : parseInt(v))}
                    disabled={!selectedClassId}
                  >
                    <SelectTrigger className="h-11">
                      <SelectValue placeholder={selectedClassId ? "Select stream" : "Select a class first"} />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="none">Not assigned</SelectItem>
                      {streams.map((s) => (
                        <SelectItem key={s.id} value={s.id.toString()}>
                          {s.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="flex justify-between pt-2">
                <Button type="button" variant="outline" size="lg" onClick={() => setCurrentStep(1)} className="gap-2">
                  <ChevronLeft className="size-4" /> Back
                </Button>
                <Button type="submit" size="lg" disabled={isLoadingClasses} className="gap-2 bg-blue-600 hover:bg-blue-700">
                  Continue <ChevronRight className="size-4" />
                </Button>
              </div>
            </motion.form>
          )}

          {/* Step 3: Sync to Device */}
          {currentStep === 3 && student && (
            <motion.div
              key="step3"
              variants={slideIn}
              initial="initial"
              animate="animate"
              exit="exit"
              className="space-y-6"
            >
              <div>
                <p className="text-sm text-muted-foreground">
                  Select devices to sync this student to. Devices already synced show a checkmark. You can skip this step.
                </p>
              </div>
              <div className="grid gap-2 max-h-52 overflow-y-auto pr-1">
                {devices.map((d) => {
                  const selected = selectedDeviceIds.has(d.id)
                  const synced = syncedDeviceIds.has(d.id)
                  const status = syncProgress[d.id]
                  return (
                    <button
                      key={d.id}
                      type="button"
                      onClick={() => toggleDevice(d.id)}
                      className={cn(
                        "w-full p-3 rounded-lg border-2 text-left flex items-center justify-between",
                        selected ? "border-blue-600 bg-blue-50 dark:bg-blue-900/20" : "border-gray-200 dark:border-gray-700 hover:border-blue-500/50"
                      )}
                    >
                      <div className="flex items-center gap-3">
                        <div className={cn("size-10 rounded-lg flex items-center justify-center", synced ? "bg-green-600/10 text-green-600" : "bg-gray-100 dark:bg-gray-700")}>
                          <Server className="size-5" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2 flex-wrap">
                            <span className="font-medium">{d.name}</span>
                            <DeviceStatusBadge status={d.status} />
                          </div>
                          {d.location && <p className="text-xs text-muted-foreground">{d.location}</p>}
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {status === "syncing" && <Loader2 className="size-4 animate-spin text-blue-600" />}
                        {synced && (
                          <span className="inline-flex items-center gap-1.5 text-green-600 dark:text-green-500 text-sm font-medium">
                            <Check className="size-4" />
                            Synced
                          </span>
                        )}
                        {selected && !synced && <Plus className="size-4 text-blue-600" />}
                      </div>
                    </button>
                  )
                })}
              </div>
              {devices.length === 0 && <p className="text-sm text-muted-foreground py-4">No online devices available.</p>}

              <div className="flex flex-col-reverse sm:flex-row justify-between gap-3 pt-2">
                <Button type="button" variant="outline" size="lg" onClick={() => setCurrentStep(2)} className="gap-2">
                  <ChevronLeft className="size-4" /> Back
                </Button>
                <div className="flex flex-wrap gap-2 justify-end">
                  <Button type="button" variant="outline" size="lg" onClick={handleStep3Skip}>
                    Skip
                  </Button>
                  <Button
                    type="button"
                    size="lg"
                    onClick={handleSyncSelected}
                    disabled={selectedDeviceIds.size === 0 || isSyncing}
                    className="gap-2 bg-indigo-600 hover:bg-indigo-700"
                  >
                    {isSyncing ? <Loader2 className="size-4 animate-spin" /> : null}
                    Sync ({selectedDeviceIds.size})
                  </Button>
                  <Button type="button" size="lg" onClick={handleStep3Next} className="gap-2 bg-blue-600 hover:bg-blue-700">
                    Continue <ChevronRight className="size-4" />
                  </Button>
                </div>
              </div>
            </motion.div>
          )}

          {/* Step 4: Fingerprint Enrollment */}
          {currentStep === 4 && student && (
            <motion.div
              key="step4"
              variants={slideIn}
              initial="initial"
              animate="animate"
              exit="exit"
              className="space-y-6"
            >
              {!enrollmentSession ? (
                <>
                  <div>
                    <p className="text-sm text-muted-foreground">
                      Select a device and finger to enroll. Already enrolled fingers appear with a checkmark when you select a device. You can skip this step.
                    </p>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <Label className="text-sm">Device</Label>
                      <div className="grid gap-2 mt-1 max-h-36 overflow-y-auto pr-1">
                        {devices.map((d) => (
                          <button
                            key={d.id}
                            type="button"
                            onClick={() => setEnrollmentDevice(d)}
                            className={cn(
                              "w-full p-3 rounded-lg border-2 text-left",
                              enrollmentDevice?.id === d.id ? "border-blue-600 bg-blue-50 dark:bg-blue-900/20" : "border-gray-200 dark:border-gray-700"
                            )}
                          >
                            <div className="flex items-center gap-2 flex-wrap">
                              <span className="font-medium">{d.name}</span>
                              <DeviceStatusBadge status={d.status} />
                            </div>
                            {d.location && <p className="text-xs text-muted-foreground">{d.location}</p>}
                          </button>
                        ))}
                      </div>
                    </div>
                    {enrollmentDevice && (
                      <div>
                        <Label>Finger</Label>
                        <FingerSelector
                          selectedFinger={enrollmentFinger}
                          onSelect={setEnrollmentFinger}
                          student={student}
                          deviceId={enrollmentDevice.id}
                        />
                      </div>
                    )}
                  </div>
                  <div className="flex flex-col-reverse sm:flex-row justify-between gap-3 pt-2">
                    <Button type="button" variant="outline" size="lg" onClick={() => setCurrentStep(3)} className="gap-2">
                      <ChevronLeft className="size-4" /> Back
                    </Button>
                    <div className="flex flex-wrap gap-2 justify-end">
                      <Button type="button" variant="outline" size="lg" onClick={handleEnrollmentSkip}>
                        Skip & Finish
                      </Button>
                      <Button
                        type="button"
                        size="lg"
                        onClick={handleStartEnrollment}
                        disabled={!enrollmentDevice || enrollmentFinger === null}
                        className="gap-2 bg-blue-600 hover:bg-blue-700"
                      >
                        Start Enrollment
                      </Button>
                    </div>
                  </div>
                </>
              ) : (
                <EnrollmentCapture
                  student={student}
                  device={enrollmentDevice!}
                  fingerId={enrollmentFinger!}
                  sessionId={enrollmentSession.session_id}
                  onComplete={handleEnrollmentComplete}
                  onRetry={() => setEnrollmentSession(null)}
                  onCancel={handleEnrollmentSkip}
                />
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  )
}
