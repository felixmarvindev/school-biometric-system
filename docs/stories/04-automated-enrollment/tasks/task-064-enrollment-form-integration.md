# Task 064: Enrollment Form Integration & Validation

## Story/Phase
- **Story**: Story 04: Automated Enrollment
- **Phase**: Phase 1: Enrollment UI

## Description

Integrate all selector components (student, device, finger) into the enrollment page and add form validation to ensure all required fields are selected before allowing enrollment to start.

## Type
- [ ] Backend
- [x] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Duration Estimate
1 day

## Prerequisites

- ✅ Task 061 complete (student selector)
- ✅ Task 062 complete (device selector)
- ✅ Task 063 complete (finger selector)

## Acceptance Criteria

1. [ ] All selector components integrated into enrollment page
2. [ ] Form state management works (selected student, device, finger)
3. [ ] Form validation prevents submission without all selections
4. [ ] "Start Enrollment" button is disabled until all fields selected
5. [ ] Validation error messages shown (if needed)
6. [ ] Form layout is clean and organized
7. [ ] Responsive design works on all screen sizes
8. [ ] Form follows design system

## Implementation Details

### Frontend Changes

1. **frontend/app/(dashboard)/dashboard/enrollment/page.tsx**
   - Integrate all selector components
   - Add form state management
   - Add form validation logic
   - Add "Start Enrollment" button
   - Handle form submission (placeholder for Phase 2)

2. **frontend/lib/validations/enrollment.ts** (optional)
   - Add enrollment form validation schema (Zod)

### Key Code Patterns

```typescript
// frontend/app/(dashboard)/dashboard/enrollment/page.tsx
'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { fadeInUp, staggerContainer, staggerItem } from '@/lib/animations';
import { StudentSelector } from '@/components/features/enrollment/StudentSelector';
import { DeviceSelector } from '@/components/features/enrollment/DeviceSelector';
import { FingerSelector } from '@/components/features/enrollment/FingerSelector';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { Student } from '@/lib/api/students';
import type { Device } from '@/lib/api/devices';

export default function EnrollmentPage() {
  const [selectedStudent, setSelectedStudent] = useState<Student | null>(null);
  const [selectedDevice, setSelectedDevice] = useState<Device | null>(null);
  const [selectedFinger, setSelectedFinger] = useState<number>(1);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const isFormValid = selectedStudent && selectedDevice && selectedFinger !== null;

  const handleStartEnrollment = async () => {
    if (!isFormValid) return;
    
    setIsSubmitting(true);
    // TODO: Phase 2 - Call enrollment API
    console.log('Starting enrollment:', {
      studentId: selectedStudent.id,
      deviceId: selectedDevice.id,
      fingerId: selectedFinger,
    });
    setIsSubmitting(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="container mx-auto px-4 py-8">
        <motion.div
          initial="hidden"
          animate="visible"
          variants={fadeInUp}
        >
          <h1 className="text-3xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 mb-8">
            Enroll Student
          </h1>
          
          <motion.div
            variants={staggerContainer}
            initial="hidden"
            animate="visible"
            className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-xl shadow-lg p-6 space-y-6"
          >
            <motion.div variants={staggerItem}>
              <StudentSelector
                onSelect={setSelectedStudent}
                selectedStudent={selectedStudent}
              />
            </motion.div>

            <motion.div variants={staggerItem}>
              <DeviceSelector
                onSelect={setSelectedDevice}
                selectedDevice={selectedDevice}
              />
            </motion.div>

            <motion.div variants={staggerItem}>
              <FingerSelector
                onSelect={setSelectedFinger}
                selectedFinger={selectedFinger}
              />
            </motion.div>

            <motion.div variants={staggerItem} className="flex gap-4 pt-4">
              <Button
                variant="outline"
                onClick={() => {
                  setSelectedStudent(null);
                  setSelectedDevice(null);
                  setSelectedFinger(1);
                }}
              >
                Clear
              </Button>
              <Button
                onClick={handleStartEnrollment}
                disabled={!isFormValid || isSubmitting}
                className="flex-1 bg-blue-600 hover:bg-blue-700"
              >
                {isSubmitting ? 'Starting...' : 'Start Enrollment'}
              </Button>
            </motion.div>

            {!isFormValid && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="text-sm text-gray-500"
              >
                Please select a student, device, and finger to start enrollment.
              </motion.div>
            )}
          </motion.div>
        </motion.div>
      </div>
    </div>
  );
}
```

## Testing

### Manual Testing

1. **Form Integration**
   - Load enrollment page
   - ✅ Verify all three selectors are visible
   - ✅ Verify layout is clean and organized

2. **Form Validation**
   - Try to click "Start Enrollment" without selections
   - ✅ Verify button is disabled
   - ✅ Verify validation message shown
   - Select all fields
   - ✅ Verify button becomes enabled

3. **Form State**
   - Select student, device, finger
   - ✅ Verify all selections are maintained
   - Click "Clear"
   - ✅ Verify all selections are cleared

4. **Responsive Design**
   - Test on different screen sizes
   - ✅ Verify layout works on desktop
   - ✅ Verify layout works on tablet/mobile

## Definition of Done

- [ ] All selector components integrated
- [ ] Form state management works
- [ ] Form validation works
- [ ] Button disabled/enabled logic works
- [ ] Layout is clean and responsive
- [ ] No console errors
- [ ] Follows design system

## Next Phase

**Phase 2: Device Control** - Now that the UI is complete, we need to implement backend device communication to actually start enrollment on devices.
