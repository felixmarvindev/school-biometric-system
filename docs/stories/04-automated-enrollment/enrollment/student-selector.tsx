"use client"

import { useState, useMemo } from "react"
import { Search, GraduationCap, User, CheckCircle2 } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import { DEMO_CLASSES, DEMO_STUDENTS, type Student } from "@/lib/demo-data"

interface StudentSelectorProps {
  selectedStudent: Student | null
  onSelect: (student: Student) => void
}

export function StudentSelector({ selectedStudent, onSelect }: StudentSelectorProps) {
  const [selectedClassId, setSelectedClassId] = useState<number | null>(null)
  const [searchQuery, setSearchQuery] = useState("")

  const filteredStudents = useMemo(() => {
    let students = DEMO_STUDENTS
    if (selectedClassId) {
      students = students.filter((s) => s.classId === selectedClassId)
    }
    if (searchQuery) {
      const query = searchQuery.toLowerCase()
      students = students.filter(
        (s) =>
          s.firstName.toLowerCase().includes(query) ||
          s.lastName.toLowerCase().includes(query) ||
          s.admissionNumber.toLowerCase().includes(query),
      )
    }
    return students
  }, [selectedClassId, searchQuery])

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3">
        <Select
          value={selectedClassId?.toString() || ""}
          onValueChange={(v) => setSelectedClassId(v ? Number.parseInt(v) : null)}
        >
          <SelectTrigger className="w-full sm:w-[200px] bg-card">
            <div className="flex items-center gap-2">
              <GraduationCap className="size-4 text-muted-foreground" />
              <SelectValue placeholder="All Classes" />
            </div>
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Classes</SelectItem>
            {DEMO_CLASSES.map((c) => (
              <SelectItem key={c.id} value={c.id.toString()}>
                {c.name} - {c.section}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>

        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 size-4 text-muted-foreground" />
          <Input
            placeholder="Search by name or admission number..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 bg-card"
          />
        </div>
      </div>

      {/* Student List */}
      <div className="border border-border rounded-xl overflow-hidden bg-card">
        <div className="max-h-[400px] overflow-y-auto divide-y divide-border">
          {filteredStudents.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
              <User className="size-10 mb-3 opacity-40" />
              <p className="text-sm">No students found</p>
            </div>
          ) : (
            filteredStudents.map((student) => {
              const isSelected = selectedStudent?.id === student.id
              const hasEnrollments = student.enrolledFingers.length > 0

              return (
                <button
                  key={student.id}
                  onClick={() => onSelect(student)}
                  className={cn(
                    "w-full flex items-center gap-4 p-4 text-left transition-all",
                    isSelected ? "bg-primary/10 ring-2 ring-inset ring-primary" : "hover:bg-muted/50",
                  )}
                >
                  <div
                    className={cn(
                      "relative flex items-center justify-center size-12 rounded-full font-semibold text-sm shrink-0 transition-all",
                      isSelected ? "bg-primary text-primary-foreground scale-105" : "bg-muted text-muted-foreground",
                    )}
                  >
                    {student.firstName[0]}
                    {student.lastName[0]}
                    {isSelected && (
                      <div className="absolute -bottom-0.5 -right-0.5 size-5 rounded-full bg-background flex items-center justify-center">
                        <CheckCircle2 className="size-4 text-primary" />
                      </div>
                    )}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span
                        className={cn(
                          "font-medium truncate transition-colors",
                          isSelected ? "text-primary" : "text-foreground",
                        )}
                      >
                        {student.firstName} {student.lastName}
                      </span>
                      {hasEnrollments && (
                        <Badge variant="secondary" className="text-xs bg-success/10 text-success border-0">
                          {student.enrolledFingers.length} enrolled
                        </Badge>
                      )}
                    </div>
                    <div className="flex items-center gap-2 text-sm text-muted-foreground mt-0.5">
                      <span>{student.admissionNumber}</span>
                      <span className="text-border">•</span>
                      <span>{student.className}</span>
                    </div>
                  </div>

                  <div
                    className={cn(
                      "flex items-center justify-center size-6 rounded-full border-2 transition-all shrink-0",
                      isSelected ? "border-primary bg-primary" : "border-muted-foreground/30",
                    )}
                  >
                    {isSelected && <CheckCircle2 className="size-4 text-primary-foreground" />}
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
