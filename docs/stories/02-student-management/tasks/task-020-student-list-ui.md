# Task 020: Student List UI

## Story/Phase
- **Story**: Story 02: Student Management
- **Phase**: Phase 2: CRUD Operations

## Description

Create the student list page component with search, filtering, pagination, and student management actions.

## Type
- [ ] Backend
- [x] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [ ] Student list page route exists at `/dashboard/students`
2. [ ] Page is protected (requires authentication via layout)
3. [ ] `StudentList` component created
4. [ ] Displays list of students in table/card format
5. [ ] Search functionality works (by name or admission number)
6. [ ] Filter by class works (dropdown)
7. [ ] Filter by stream works (dropdown)
8. [ ] Pagination controls work
9. [ ] Loading states shown during data fetch
10. [ ] Error states handled gracefully
11. [ ] "Add Student" button navigates to create form
12. [ ] Click on student navigates to detail page
13. [ ] Responsive design (mobile-friendly)
14. [ ] Empty state shown when no students

## Technical Details

### Files to Create/Modify

```
frontend/app/(dashboard)/dashboard/students/page.tsx
frontend/components/features/students/StudentList.tsx
frontend/components/features/students/StudentCard.tsx (or StudentTableRow.tsx)
frontend/components/features/students/StudentListFilters.tsx
frontend/lib/api/students.ts (add listStudents function)
```

### Key Code Patterns

```typescript
// app/(dashboard)/dashboard/students/page.tsx
"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { StudentList } from "@/components/features/students/StudentList"
import { useAuthStore } from "@/lib/store/authStore"
import { listStudents, type StudentResponse } from "@/lib/api/students"

export default function StudentsPage() {
  const router = useRouter()
  const { token } = useAuthStore()
  const [students, setStudents] = useState<StudentResponse[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(50)
  const [search, setSearch] = useState("")
  const [classFilter, setClassFilter] = useState<number | null>(null)
  const [streamFilter, setStreamFilter] = useState<number | null>(null)

  useEffect(() => {
    if (!token) return

    const fetchStudents = async () => {
      try {
        setIsLoading(true)
        const result = await listStudents(token, {
          page,
          page_size: pageSize,
          search: search || undefined,
          class_id: classFilter || undefined,
          stream_id: streamFilter || undefined,
        })
        setStudents(result.items)
      } catch (err) {
        setError("Failed to load students")
      } finally {
        setIsLoading(false)
      }
    }

    fetchStudents()
  }, [token, page, search, classFilter, streamFilter])

  return (
    <StudentList
      students={students}
      isLoading={isLoading}
      error={error}
      search={search}
      onSearchChange={setSearch}
      classFilter={classFilter}
      onClassFilterChange={setClassFilter}
      streamFilter={streamFilter}
      onStreamFilterChange={setStreamFilter}
      onAddStudent={() => router.push("/dashboard/students/new")}
      onStudentClick={(id) => router.push(`/dashboard/students/${id}`)}
    />
  )
}
```

### Dependencies

- Task 016 (List students API must exist)
- Task 006 (Dashboard layout must exist)

## Visual Testing

### Before State
- No student list page exists
- Cannot view students from frontend

### After State
- Can navigate to `/dashboard/students`
- See list of students
- Can search and filter
- Can navigate to student detail or create form

### Testing Steps

1. Navigate to students page
2. Verify list displays correctly
3. Test search functionality
4. Test filtering by class/stream
5. Test pagination
6. Test navigation to detail/create pages

## Definition of Done

- [ ] Code written and follows standards
- [ ] Component tests written and passing
- [ ] Search functionality works
- [ ] Filtering works
- [ ] Pagination works
- [ ] Responsive design verified
- [ ] Loading states implemented
- [ ] Error states handled
- [ ] Empty state implemented
- [ ] Code reviewed
- [ ] Tested in browser

## Time Estimate

6-8 hours

## Notes

- Use table layout for desktop, card layout for mobile
- Debounce search input (300ms delay)
- Show loading skeleton during fetch
- Consider virtual scrolling for large lists
- Add export functionality (future enhancement)

