# Task 061: Student Selector Component

## Story/Phase
- **Story**: Story 04: Automated Enrollment
- **Phase**: Phase 1: Enrollment UI

## Description

Create a student selector component with search functionality that allows administrators to search and select a student for enrollment.

## Type
- [ ] Backend
- [x] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Duration Estimate
1 day

## Prerequisites

- ✅ Task 060 complete (enrollment page exists)
- ✅ Students API endpoint working (`GET /api/v1/students`)
- ✅ Student list can be fetched

## Acceptance Criteria

1. [ ] Student selector component created
2. [ ] Search input field works (filters students by name/admission number)
3. [ ] Student list displays with search results
4. [ ] Can select a student from list
5. [ ] Selected student is highlighted/indicated
6. [ ] Student details shown (name, admission number, class)
7. [ ] Search is debounced (300ms delay)
8. [ ] Loading state shown while fetching
9. [ ] Empty state shown when no results
10. [ ] Component is reusable

## Implementation Details

### Frontend Changes

1. **frontend/components/features/enrollment/StudentSelector.tsx**
   - Create student selector component
   - Add search input with debounce
   - Add student list display
   - Add selection handling
   - Add loading/empty states

2. **frontend/lib/api/students.ts** (if not exists)
   - Add `searchStudents()` function
   - Add `getAllStudents()` function

3. **frontend/app/(dashboard)/dashboard/enrollment/page.tsx**
   - Integrate StudentSelector component
   - Handle selected student state

### Key Code Patterns

```typescript
// frontend/components/features/enrollment/StudentSelector.tsx
'use client';

import { useState, useEffect, useCallback } from 'react';
import { Search, User } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { searchStudents, type Student } from '@/lib/api/students';
import { useDebounce } from '@/lib/hooks/useDebounce';

interface StudentSelectorProps {
  onSelect: (student: Student) => void;
  selectedStudent?: Student | null;
}

export function StudentSelector({ onSelect, selectedStudent }: StudentSelectorProps) {
  const [search, setSearch] = useState('');
  const [students, setStudents] = useState<Student[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const debouncedSearch = useDebounce(search, 300);

  useEffect(() => {
    if (debouncedSearch.length >= 2) {
      setIsLoading(true);
      searchStudents(debouncedSearch)
        .then(setStudents)
        .finally(() => setIsLoading(false));
    } else {
      setStudents([]);
    }
  }, [debouncedSearch]);

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium text-blue-700 dark:text-blue-400">
        Select Student
      </label>
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
        <Input
          type="text"
          placeholder="Search by name or admission number..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="pl-10"
        />
      </div>
      
      {/* Student list */}
      {isLoading && <div>Loading...</div>}
      {!isLoading && students.length === 0 && search.length >= 2 && (
        <div className="text-sm text-gray-500">No students found</div>
      )}
      {students.length > 0 && (
        <div className="border rounded-lg max-h-60 overflow-y-auto">
          {students.map((student) => (
            <div
              key={student.id}
              onClick={() => onSelect(student)}
              className={`p-3 cursor-pointer hover:bg-blue-50 dark:hover:bg-gray-700 ${
                selectedStudent?.id === student.id ? 'bg-blue-100 dark:bg-blue-900' : ''
              }`}
            >
              <div className="font-medium">{student.first_name} {student.last_name}</div>
              <div className="text-sm text-gray-500">
                {student.admission_number} • {student.class?.name}
              </div>
            </div>
          ))}
        </div>
      )}
      
      {selectedStudent && (
        <div className="p-3 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
          <div className="flex items-center gap-2">
            <User className="text-green-600" />
            <div>
              <div className="font-medium">{selectedStudent.first_name} {selectedStudent.last_name}</div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {selectedStudent.admission_number}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
```

## Testing

### Manual Testing

1. **Search Functionality**
   - Type in search field
   - ✅ Verify search filters students
   - ✅ Verify debounce works (no excessive API calls)
   - ✅ Verify loading state appears

2. **Selection**
   - Click a student
   - ✅ Verify student is selected
   - ✅ Verify selected student is highlighted
   - ✅ Verify onSelect callback called

3. **Empty States**
   - Search for non-existent student
   - ✅ Verify "No students found" message

## Definition of Done

- [ ] Student selector component created
- [ ] Search functionality works
- [ ] Selection works correctly
- [ ] Loading/empty states handled
- [ ] Component is reusable
- [ ] No console errors
- [ ] Follows design system

## Next Task

**Task 062: Device Selector Component** - Add device selection with status indicators.
