# Task 063: Finger Selector Component

## Story/Phase
- **Story**: Story 04: Automated Enrollment
- **Phase**: Phase 1: Enrollment UI

## Description

Create a finger selector component that allows administrators to select which finger (0-9) to enroll for the student.

## Type
- [ ] Backend
- [x] Frontend
- [ ] Database
- [ ] DevOps
- [ ] Documentation

## Duration Estimate
0.5 day

## Prerequisites

- ✅ Task 060 complete (enrollment page exists)

## Acceptance Criteria

1. [ ] Finger selector component created
2. [ ] Dropdown/select shows finger options (0-9)
3. [ ] Finger names are human-readable (Thumb, Index, Middle, etc.)
4. [ ] Default selection is Index Finger (1) or Right Thumb (0)
5. [ ] Can change finger selection
6. [ ] Selected finger is displayed clearly
7. [ ] Component is reusable

## Implementation Details

### Frontend Changes

1. **frontend/components/features/enrollment/FingerSelector.tsx**
   - Create finger selector component
   - Add dropdown/select with finger options
   - Map finger IDs to human-readable names
   - Add default selection

2. **frontend/app/(dashboard)/dashboard/enrollment/page.tsx**
   - Integrate FingerSelector component
   - Handle selected finger state

### Key Code Patterns

```typescript
// frontend/components/features/enrollment/FingerSelector.tsx
'use client';

import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

interface FingerSelectorProps {
  onSelect: (fingerId: number) => void;
  selectedFinger?: number;
}

const FINGER_OPTIONS = [
  { id: 0, name: 'Right Thumb', description: 'Most common' },
  { id: 1, name: 'Right Index', description: 'Recommended' },
  { id: 2, name: 'Right Middle', description: '' },
  { id: 3, name: 'Right Ring', description: '' },
  { id: 4, name: 'Right Pinky', description: '' },
  { id: 5, name: 'Left Thumb', description: '' },
  { id: 6, name: 'Left Index', description: '' },
  { id: 7, name: 'Left Middle', description: '' },
  { id: 8, name: 'Left Ring', description: '' },
  { id: 9, name: 'Left Pinky', description: '' },
];

export function FingerSelector({ onSelect, selectedFinger = 1 }: FingerSelectorProps) {
  const selectedOption = FINGER_OPTIONS.find(f => f.id === selectedFinger) || FINGER_OPTIONS[1];

  return (
    <div className="space-y-2">
      <label className="text-sm font-medium text-blue-700 dark:text-blue-400">
        Select Finger
      </label>
      <Select
        value={selectedFinger.toString()}
        onValueChange={(value) => onSelect(parseInt(value, 10))}
      >
        <SelectTrigger className="w-full">
          <SelectValue>
            {selectedOption.name} {selectedOption.description && `(${selectedOption.description})`}
          </SelectValue>
        </SelectTrigger>
        <SelectContent>
          {FINGER_OPTIONS.map((finger) => (
            <SelectItem key={finger.id} value={finger.id.toString()}>
              <div>
                <div className="font-medium">{finger.name}</div>
                {finger.description && (
                  <div className="text-xs text-gray-500">{finger.description}</div>
                )}
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      
      {selectedOption && (
        <div className="text-sm text-gray-600 dark:text-gray-400">
          Finger ID: {selectedFinger}
        </div>
      )}
    </div>
  );
}
```

## Testing

### Manual Testing

1. **Finger Selection**
   - Open enrollment page
   - ✅ Verify finger selector shows default (Index Finger)
   - ✅ Verify can change selection
   - ✅ Verify all 10 fingers available (0-9)
   - ✅ Verify finger names are readable

2. **Default Selection**
   - Load page
   - ✅ Verify default is Index Finger (1) or Right Thumb (0)

## Definition of Done

- [ ] Finger selector component created
- [ ] All 10 finger options available
- [ ] Default selection works
- [ ] Selection change works
- [ ] Component is reusable
- [ ] No console errors
- [ ] Follows design system

## Next Task

**Task 064: Enrollment Form Integration & Validation** - Integrate all selectors and add form validation.
