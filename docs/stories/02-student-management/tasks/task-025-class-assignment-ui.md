# Task 025: Class Assignment UI

## Story/Phase
- **Story**: Story 02: Student Management
- **Phase**: Phase 3: Class Assignment

## Description

Create UI components for managing classes and streams, and integrating class/stream selection into the student form.

## Type
- [ ] Backend
- [x] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [x] Class management page exists at `/dashboard/classes`
2. [x] Stream management integrated with class management
3. [x] Can create new classes
4. [x] Can create new streams within classes
5. [x] Can edit class/stream names
6. [x] Can delete classes/streams (with confirmation)
7. [x] Class/stream dropdowns in student form
8. [x] Class/stream displayed in student list
9. [x] Class/stream displayed in student detail
10. [x] Filtering by class/stream works in student list
11. [x] Loading states implemented
12. [x] Error handling implemented

## Technical Details

### Files to Create/Modify

```
frontend/app/(dashboard)/dashboard/classes/page.tsx
frontend/components/features/classes/ClassManagement.tsx
frontend/components/features/classes/ClassForm.tsx
frontend/components/features/classes/StreamForm.tsx
frontend/components/features/students/StudentForm.tsx (add class/stream selectors)
frontend/lib/api/classes.ts (add class management functions)
frontend/lib/api/streams.ts (add stream management functions)
```

### Key Code Patterns

```typescript
// components/features/classes/ClassManagement.tsx
"use client"

import { useState, useEffect } from "react"
import { useAuthStore } from "@/lib/store/authStore"
import { listClasses, createClass, updateClass, deleteClass } from "@/lib/api/classes"
import { listStreams, createStream } from "@/lib/api/streams"

export function ClassManagement() {
  const { token } = useAuthStore()
  const [classes, setClasses] = useState<ClassResponse[]>([])
  const [selectedClass, setSelectedClass] = useState<number | null>(null)
  const [streams, setStreams] = useState<StreamResponse[]>([])

  useEffect(() => {
    if (!token) return
    loadClasses()
  }, [token])

  const loadClasses = async () => {
    const data = await listClasses(token!)
    setClasses(data)
  }

  const handleCreateClass = async (name: string) => {
    await createClass(token!, { name })
    await loadClasses()
  }

  const handleCreateStream = async (classId: number, name: string) => {
    await createStream(token!, { class_id: classId, name })
    await loadStreams(classId)
  }

  return (
    <div>
      {/* Class list and creation */}
      {/* Stream list and creation for selected class */}
    </div>
  )
}
```

### Dependencies

- Task 023 (Class management API must exist)
- Task 024 (Stream management API must exist)
- Task 021 (Student form should exist for integration)

## Visual Testing

### Before State
- No UI for managing classes/streams
- Cannot assign students to classes/streams

### After State
- Can create and manage classes
- Can create and manage streams
- Can assign students to classes/streams
- Filtering by class/stream works

### Testing Steps

1. Navigate to classes page
2. Create a new class
3. Create streams within the class
4. Assign student to class/stream
5. Filter students by class/stream
6. Verify class/stream displayed in student list

## Definition of Done

- [x] Code written and follows standards
- [x] Component tests written and passing
- [x] Class management works
- [x] Stream management works
- [x] Student assignment works
- [x] Filtering works
- [x] Responsive design verified
- [x] Code reviewed
- [x] Tested in browser

## Time Estimate

6-8 hours

## Notes

- Class management can be a separate page or modal
- Stream management should be contextual to selected class
- Consider drag-and-drop for class assignment (future enhancement)
- Show student count per class/stream

