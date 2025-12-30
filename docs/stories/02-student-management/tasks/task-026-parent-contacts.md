# Task 026: Parent Contacts Integration

## Story/Phase
- **Story**: Story 02: Student Management
- **Phase**: Phase 4: Parent Contacts

## Description

Ensure parent contact information is properly integrated into student forms and displays, with validation.

## Type
- [ ] Backend
- [x] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Acceptance Criteria

1. [ ] Parent phone field in student form
2. [ ] Parent email field in student form
3. [ ] Phone format validation (client-side)
4. [ ] Email format validation (client-side)
5. [ ] Parent information displayed in student detail
6. [ ] Parent information displayed in student list (optional)
7. [ ] Clear labels and placeholders
8. [ ] Helpful validation messages

## Technical Details

### Files to Create/Modify

```
frontend/components/features/students/StudentForm.tsx (already includes parent fields)
frontend/components/features/students/StudentDetail.tsx (display parent info)
frontend/lib/validations/student.ts (add phone/email validation)
```

### Key Code Patterns

```typescript
// validations/student.ts
import { z } from "zod"

export const studentSchema = z.object({
  admission_number: z.string().min(1).max(50),
  first_name: z.string().min(1).max(100),
  last_name: z.string().min(1).max(100),
  date_of_birth: z.date().optional(),
  gender: z.enum(["male", "female", "other"]).optional(),
  class_id: z.number().optional().nullable(),
  stream_id: z.number().optional().nullable(),
  parent_phone: z.string()
    .regex(/^\+?[0-9]{10,15}$/, "Phone number must be 10-15 digits")
    .optional()
    .nullable(),
  parent_email: z.string()
    .email("Please enter a valid email address")
    .optional()
    .nullable(),
})
```

### Dependencies

- Task 021 (Student form must exist)
- Task 022 (Student detail must exist)
- Task 012 (Student model includes parent fields)

## Visual Testing

### Before State
- Parent fields may not be properly validated or displayed

### After State
- Parent fields validated correctly
- Parent information displays properly
- Clear validation messages

### Testing Steps

1. Test phone validation - verify format errors
2. Test email validation - verify format errors
3. Test optional fields - verify can be left empty
4. Verify parent info displays in detail page
5. Verify parent info saves correctly

## Definition of Done

- [ ] Code written and follows standards
- [ ] Validation works correctly
- [ ] Parent information displays correctly
- [ ] Form fields properly labeled
- [ ] Responsive design verified
- [ ] Code reviewed
- [ ] Tested in browser

## Time Estimate

2-3 hours

## Notes

- Parent contact info is optional but recommended
- Phone format: +254712345678 or 0712345678
- Email validation uses standard email format
- Consider adding multiple parent contacts (future enhancement)
- Parent info will be used for SMS notifications (Story 06)

