# Task 022: Student Detail UI

## Story/Phase
- **Story**: Story 02: Student Management
- **Phase**: Phase 2: CRUD Operations

## Description

Create the student detail page component for viewing complete student information.

## Type
- [ ] Backend
- [x] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [ ] Student detail page route exists at `/dashboard/students/{id}`
2. [ ] Page is protected (requires authentication via layout)
3. [ ] `StudentDetail` component created
4. [ ] Displays all student information
5. [ ] Shows class and stream information
6. [ ] Shows parent contact information
7. [ ] "Edit" button navigates to edit form
8. [ ] "Delete" button with confirmation
9. [ ] Loading state during data fetch
10. [ ] Error state if student not found
11. [ ] Responsive design
12. [ ] Empty states for optional fields

## Technical Details

### Files to Create/Modify

```
frontend/app/(dashboard)/dashboard/students/[id]/page.tsx
frontend/components/features/students/StudentDetail.tsx
frontend/components/features/students/StudentInfoCard.tsx
frontend/lib/api/students.ts (getStudent function already exists)
```

### Key Code Patterns

```typescript
// app/(dashboard)/dashboard/students/[id]/page.tsx
"use client"

import { useState, useEffect } from "react"
import { useRouter, useParams } from "next/navigation"
import { StudentDetail } from "@/components/features/students/StudentDetail"
import { useAuthStore } from "@/lib/store/authStore"
import { getStudent, deleteStudent, type StudentResponse } from "@/lib/api/students"

export default function StudentDetailPage() {
  const router = useRouter()
  const params = useParams()
  const studentId = parseInt(params.id as string)
  const { token } = useAuthStore()
  const [student, setStudent] = useState<StudentResponse | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!token || !studentId) return

    const fetchStudent = async () => {
      try {
        setIsLoading(true)
        const data = await getStudent(token, studentId)
        setStudent(data)
      } catch (err) {
        setError("Failed to load student")
      } finally {
        setIsLoading(false)
      }
    }

    fetchStudent()
  }, [token, studentId])

  const handleEdit = () => {
    router.push(`/dashboard/students/${studentId}/edit`)
  }

  const handleDelete = async () => {
    if (!confirm("Are you sure you want to delete this student?")) return
    
    try {
      await deleteStudent(token!, studentId)
      router.push("/dashboard/students")
    } catch (err) {
      setError("Failed to delete student")
    }
  }

  if (isLoading) {
    return <div>Loading...</div>
  }

  if (error || !student) {
    return <div>Error: {error || "Student not found"}</div>
  }

  return (
    <StudentDetail
      student={student}
      onEdit={handleEdit}
      onDelete={handleDelete}
    />
  )
}
```

### Dependencies

- Task 017 (Get student API must exist)
- Task 019 (Delete student API must exist)
- Task 020 (Student list page should exist for navigation)

## Visual Testing

### Before State
- No student detail page exists
- Cannot view individual student details

### After State
- Can navigate to student detail page
- See complete student information
- Can edit or delete student

### Testing Steps

1. Navigate to student detail page
2. Verify all information displays
3. Test edit button navigation
4. Test delete with confirmation
5. Test error state for non-existent student

## Definition of Done

- [ ] Code written and follows standards
- [ ] Component tests written and passing
- [ ] All student information displays
- [ ] Edit functionality works
- [ ] Delete functionality works
- [ ] Responsive design verified
- [ ] Loading states implemented
- [ ] Error states handled
- [ ] Code reviewed
- [ ] Tested in browser

## Time Estimate

4-6 hours

## Notes

- Display student information in organized sections
- Show enrollment status (future - which devices enrolled)
- Show attendance summary (future - attendance stats)
- Consider adding photo display (if photo upload added later)
- Delete should show confirmation dialog

