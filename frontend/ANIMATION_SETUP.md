# Animation Setup Guide

This guide explains how to set up and use animations in the School Biometric System frontend.

## Installation

Install Framer Motion:

```bash
cd frontend
npm install framer-motion
```

## What's Been Added

### 1. Animation Library

**Location**: `frontend/lib/animations/framer-motion.ts`

Contains all reusable animation variants:
- `fadeIn`, `fadeInUp`, `fadeInDown`
- `scaleIn`, `slideInLeft`, `slideInRight`
- `staggerContainer`, `staggerItem`
- `pageTransition`, `cardHover`, `buttonPress`
- And more...

### 2. Reusable Animated Components

**Location**: `frontend/components/ui/`

- `AnimatedSection` - Wrapper for animated sections
- `AnimatedCard` - Card with hover animations
- `AnimatedButton` - Button with press animation

### 3. Updated Pages

The following pages have been enhanced with animations:

- **Home Page** (`app/page.tsx`):
  - Animated header (slide in from left/right)
  - Staggered hero section
  - Staggered feature cards with hover effects
  - Animated footer

- **Register Page** (`app/(auth)/register/page.tsx`):
  - Animated back button (slide in from left)
  - Animated form (scale in)

- **School Registration Form** (`components/features/school/SchoolRegistrationForm.tsx`):
  - Staggered form fields
  - Smooth section transitions

## Usage Examples

### Basic Fade In

```typescript
import { motion } from 'framer-motion';
import { fadeInUp } from '@/lib/animations';

<motion.div
  initial="hidden"
  animate="visible"
  variants={fadeInUp}
>
  Content
</motion.div>
```

### Staggered List

```typescript
import { motion } from 'framer-motion';
import { staggerContainer, staggerItem } from '@/lib/animations';

<motion.div
  variants={staggerContainer}
  initial="hidden"
  animate="visible"
>
  {items.map((item) => (
    <motion.div key={item.id} variants={staggerItem}>
      {item.content}
    </motion.div>
  ))}
</motion.div>
```

### Using Reusable Components

```typescript
import { AnimatedSection, AnimatedCard } from '@/components/ui';

<AnimatedSection delay={0.2}>
  <h1>Title</h1>
</AnimatedSection>

<AnimatedCard hoverable delay={0.1}>
  <CardContent>Card content</CardContent>
</AnimatedCard>
```

## Documentation

- **Design Patterns**: `docs/frontend/design-patterns.md`
- **Cursor Rules**: `.cursor/rules/frontend-design-patterns.mdc`

## Next Steps

1. Install framer-motion: `npm install framer-motion`
2. Restart your dev server
3. Test the animations on the home and register pages
4. Follow the patterns in `docs/frontend/design-patterns.md` for new components

## Troubleshooting

### TypeScript Errors

If you see "Cannot find module '@/lib/animations'":
1. Make sure framer-motion is installed
2. Restart your TypeScript server (VS Code: Cmd/Ctrl + Shift + P → "TypeScript: Restart TS Server")
3. Restart your dev server

### Animations Not Working

1. Ensure you're using `'use client'` directive in client components
2. Check that `motion` components are imported from `framer-motion`
3. Verify animation variants are imported correctly

---

**Last Updated**: 2024-01-XX

