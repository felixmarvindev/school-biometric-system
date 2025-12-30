# Task 021: Student Form UI

## Story/Phase
- **Story**: Story 02: Student Management
- **Phase**: Phase 2: CRUD Operations

## Description

Create the student registration form component for creating and editing students.

## Type
- [ ] Backend
- [x] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [ ] Student form page route exists at `/dashboard/students/new` and `/dashboard/students/{id}/edit`
2. [ ] Page is protected (requires authentication via layout)
3. [ ] `StudentForm` component created
4. [ ] Form includes all required fields
5. [ ] Form validation works (client-side)
6. [ ] Form pre-populated when editing
7. [ ] Admission number field (read-only when editing)
8. [ ] Date picker for date of birth
9. [ ] Gender dropdown
10. [ ] Class/stream selectors (dropdowns, optional)
11. [ ] Parent contact fields (phone, email)
12. [ ] Save button creates/updates student
13. [ ] Cancel button navigates back
14. [ ] Success message shown after save
15. [ ] Error messages displayed
16. [ ] Loading states during save
17. [ ] Form is responsive and accessible

## Technical Details

### Files to Create/Modify

```
frontend/app/(dashboard)/dashboard/students/new/page.tsx
frontend/app/(dashboard)/dashboard/students/[id]/edit/page.tsx
frontend/components/features/students/StudentForm.tsx
frontend/lib/api/students.ts (add createStudent, updateStudent functions)
frontend/lib/validations/student.ts (Zod schema)
```

### Key Code Patterns

```typescript
// components/features/students/StudentForm.tsx
"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { useAuthStore } from "@/lib/store/authStore"
import { createStudent, updateStudent, getStudent, type StudentResponse } from "@/lib/api/students"

interface StudentFormProps {
  studentId?: number // If provided, form is in edit mode
  onSuccess?: () => void
}

export function StudentForm({ studentId, onSuccess }: StudentFormProps) {
  const router = useRouter()
  const { token } = useAuthStore()
  const [isLoading, setIsLoading] = useState(false)
  const [isFetching, setIsFetching] = useState(!!studentId)
  const [error, setError] = useState<string | null>(null)
  
  const [formData, setFormData] = useState({
    admission_number: "",
    first_name: "",
    last_name: "",
    date_of_birth: "",
    gender: "",
    class_id: null as number | null,
    stream_id: null as number | null,
    parent_phone: "",
    parent_email: "",
  })

  // Fetch student data if editing
  useEffect(() => {
    if (studentId && token) {
      const fetchStudent = async () => {
        try {
          setIsFetching(true)
          const student = await getStudent(token, studentId)
          setFormData({
            admission_number: student.admission_number,
            first_name: student.first_name,
            last_name: student.last_name,
            date_of_birth: student.date_of_birth || "",
            gender: student.gender || "",
            class_id: student.class_id || null,
            stream_id: student.stream_id || null,
            parent_phone: student.parent_phone || "",
            parent_email: student.parent_email || "",
          })
        } catch (err) {
          setError("Failed to load student data")
        } finally {
          setIsFetching(false)
        }
      }
      fetchStudent()
    }
  }, [studentId, token])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!token) return

    setIsLoading(true)
    setError(null)

    try {
      if (studentId) {
        await updateStudent(token, studentId, formData)
      } else {
        await createStudent(token, formData)
      }
      
      if (onSuccess) {
        onSuccess()
      } else {
        router.push("/dashboard/students")
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save student")
    } finally {
      setIsLoading(false)
    }
  }

  if (isFetching) {
    return <div>Loading...</div>
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{studentId ? "Edit Student" : "Add New Student"}</CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Form fields */}
          <Button type="submit" disabled={isLoading}>
            {isLoading ? "Saving..." : studentId ? "Update Student" : "Create Student"}
          </Button>
        </form>
      </CardContent>
    </Card>
  )
}
```

### Dependencies

- Task 015 (Create student API must exist)
- Task 018 (Update student API must exist)
- Task 020 (Student list page should exist for navigation)

## Visual Testing

### Before State
- No student form exists
- Cannot create/edit students from frontend

### After State
- Can navigate to create/edit form
- Form displays correctly
- Can create/edit students
- Validation works

### Testing Steps

1. Navigate to create form
2. Fill form and submit
3. Verify student created
4. Navigate to edit form
5. Modify and save
6. Verify student updated
7. Test validation errors

## Definition of Done

- [ ] Code written and follows standards
- [ ] Component tests written and passing
- [ ] Form validation works
- [ ] Create functionality works
- [ ] Update functionality works
- [ ] Responsive design verified
- [ ] Accessibility verified
- [ ] Loading states implemented
- [ ] Error handling implemented
- [ ] Code reviewed
- [ ] Tested in browser

## Time Estimate

8-10 hours

## Notes

- Admission number is auto-generated or manually entered (school-specific)
- Date picker should use a proper date input component
- Class/stream dropdowns should be populated from API (Phase 3)
- Phone validation should match backend pattern
- Consider multi-step form for better UX (personal info → academic → parent)

