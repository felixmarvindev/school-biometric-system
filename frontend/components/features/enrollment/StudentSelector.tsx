"use client"

import { useState, useMemo, useEffect } from "react"
import { Search, GraduationCap, User, CheckCircle2 } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import { listStudents, type StudentResponse, StudentApiError } from "@/lib/api/students"
import { listClasses, type ClassResponse, ClassApiError } from "@/lib/api/classes"
import { useAuthStore } from "@/lib/store/authStore"

interface StudentSelectorProps {
  selectedStudent: StudentResponse | null
  onSelect: (student: StudentResponse) => void
}

export function StudentSelector({ selectedStudent, onSelect }: StudentSelectorProps) {
  const { token } = useAuthStore()
  const [selectedClassId, setSelectedClassId] = useState<number | null>(null)
  const [searchQuery, setSearchQuery] = useState("")
  const [classes, setClasses] = useState<ClassResponse[]>([])
  const [students, setStudents] = useState<StudentResponse[]>([])
  const [isLoadingClasses, setIsLoadingClasses] = useState(true)
  const [isLoadingStudents, setIsLoadingStudents] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Load classes on mount
  useEffect(() => {
    if (!token) return

    setIsLoadingClasses(true)
    setError(null)
    listClasses(token)
      .then((data) => {
        setClasses(data)
      })
      .catch((err) => {
        if (err instanceof ClassApiError) {
          setError(err.message)
        } else {
          setError("Failed to load classes")
        }
      })
      .finally(() => {
        setIsLoadingClasses(false)
      })
  }, [token])

  // Load students when class is selected (or all if no class selected)
  useEffect(() => {
    if (!token) {
      setStudents([])
      return
    }

    setIsLoadingStudents(true)
    setError(null)
    const params: { page_size: number; class_id?: number } = {
      page_size: 100,
    }
    
    // Only add class_id filter if a specific class is selected
    if (selectedClassId) {
      params.class_id = selectedClassId
    }
    
    listStudents(token, params)
      .then((result) => {
        setStudents(result.items)
      })
      .catch((err) => {
        if (err instanceof StudentApiError) {
          setError(err.message)
        } else {
          setError("Failed to load students")
        }
        setStudents([])
      })
      .finally(() => {
        setIsLoadingStudents(false)
      })
  }, [token, selectedClassId])

  const filteredStudents = useMemo(() => {
    let filtered = students
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      filtered = filtered.filter(
        (s) =>
          s.first_name.toLowerCase().includes(query) ||
          s.last_name.toLowerCase().includes(query) ||
          s.admission_number.toLowerCase().includes(query),
      )
    }
    return filtered
  }, [students, searchQuery])

  const selectedClassData = classes.find((c) => c.id === selectedClassId)

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <Select
          value={selectedClassId?.toString() || "all"}
          onValueChange={(v) => setSelectedClassId(v === "all" ? null : Number.parseInt(v))}
          disabled={isLoadingClasses}
        >
          <SelectTrigger className="w-full sm:w-[200px] bg-white dark:bg-gray-800 border-blue-300 dark:border-gray-600 focus:border-blue-500 focus:ring-blue-500">
            <div className="flex items-center gap-2">
              <GraduationCap className="size-4 text-gray-500 dark:text-gray-400" />
              <SelectValue placeholder="All Classes" />
            </div>
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Classes</SelectItem>
            {classes.map((c) => (
              <SelectItem key={c.id} value={c.id.toString()}>
                {c.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-gray-500 dark:text-gray-400" />
          <Input
            placeholder="Search by name or admission number..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-white dark:bg-gray-800 border-blue-300 dark:border-gray-600 focus:border-blue-500 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Student List */}
      <div className="border border-gray-200 dark:border-gray-700 rounded-xl overflow-hidden bg-white dark:bg-gray-800">
        <div className="max-h-[400px] overflow-y-auto divide-y divide-gray-200 dark:divide-gray-700">
          {isLoadingStudents ? (
            <div className="flex flex-col items-center justify-center py-12 text-gray-600 dark:text-gray-400">
              <User className="size-10 mb-3 opacity-40 animate-pulse" />
              <p className="text-sm">Loading students...</p>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-12 text-red-600 dark:text-red-400">
              <User className="size-10 mb-3 opacity-40" />
              <p className="text-sm">{error}</p>
            </div>
          ) : filteredStudents.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-gray-600 dark:text-gray-400">
              <User className="size-10 mb-3 opacity-40" />
              <p className="text-sm">No students found</p>
            </div>
          ) : (
            filteredStudents.map((student) => {
              const isSelected = selectedStudent?.id === student.id
              // TODO: Get enrolled fingers count when API is ready
              const enrolledFingersCount = 0

              return (
                <button
                  key={student.id}
                  onClick={() => onSelect(student)}
                  className={cn(
                    "w-full flex items-center gap-4 p-4 text-left transition-all",
                    isSelected ? "bg-blue-50 ring-2 ring-inset ring-blue-600 dark:bg-blue-900/30 dark:ring-blue-500" : "hover:bg-blue-50/50 dark:hover:bg-gray-700/50",
                  )}
                >
                  <div
                    className={cn(
                      "relative flex items-center justify-center size-12 rounded-full font-semibold text-sm shrink-0 transition-all",
                      isSelected ? "bg-blue-600 text-white scale-105" : "bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400",
                    )}
                  >
                    {student.first_name[0]}
                    {student.last_name[0]}
                    {isSelected && (
                      <div className="absolute -bottom-0.5 -right-0.5 size-5 rounded-full bg-background flex items-center justify-center">
                        <CheckCircle2 className="size-4 text-blue-600" />
                      </div>
                    )}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span
                        className={cn(
                          "font-medium truncate transition-colors",
                          isSelected ? "text-blue-600 dark:text-blue-400" : "text-gray-900 dark:text-gray-100",
                        )}
                      >
                        {student.first_name} {student.last_name}
                      </span>
                      {enrolledFingersCount > 0 && (
                        <Badge variant="secondary" className="text-xs bg-success/10 text-success border-0">
                          {enrolledFingersCount} enrolled
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground mt-0.5">
                      <span>{student.admission_number}</span>
                      {selectedClassData && (
                        <>
                          <span className="text-border">•</span>
                          <span>{selectedClassData.name}</span>
                        </>
                      )}
                    </div>
                  </div>

                  <div
                    className={cn(
                      "flex items-center justify-center size-6 rounded-full border-2 transition-all shrink-0",
                      isSelected ? "border-blue-600 bg-blue-600" : "border-gray-300 dark:border-gray-600",
                    )}
                  >
                    {isSelected && <CheckCircle2 className="size-4 text-white" />}
                  </div>
                </button>
              )
            })
          )}
        </div>
      </div>
    </div>
  )
}
