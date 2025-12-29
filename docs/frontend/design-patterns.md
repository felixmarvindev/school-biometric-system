# Frontend Design Patterns & Animation Guidelines

This document outlines the design patterns, animation schemes, and component guidelines for the School Biometric System frontend.

## Table of Contents

1. [Animation Patterns](#animation-patterns)
2. [Component Design Patterns](#component-design-patterns)
3. [Color Schemes](#color-schemes)
4. [Typography](#typography)
5. [Spacing & Layout](#spacing--layout)
6. [Accessibility](#accessibility)

---

## Animation Patterns

### Library: Framer Motion

We use **Framer Motion** as our primary animation library. It provides smooth, performant animations that work well with React and Next.js.

### Animation Principles

1. **Subtle & Purposeful**: Animations should enhance UX, not distract
2. **Performance First**: Use `transform` and `opacity` for best performance
3. **Consistent Timing**: Use standardized durations and easings
4. **Respect Preferences**: Consider `prefers-reduced-motion`

### Standard Animation Variants

All animation variants are defined in `frontend/lib/animations/framer-motion.ts`.

#### Page Transitions

```typescript
import { pageTransition } from '@/lib/animations';
import { motion } from 'framer-motion';

<motion.div
  initial="initial"
  animate="animate"
  exit="exit"
  variants={pageTransition}
>
  {/* Page content */}
</motion.div>
```

#### Fade In Animations

```typescript
import { fadeIn, fadeInUp, fadeInDown } from '@/lib/animations';

// Simple fade
<motion.div variants={fadeIn} initial="hidden" animate="visible">
  Content
</motion.div>

// Fade with slide up (most common)
<motion.div variants={fadeInUp} initial="hidden" animate="visible">
  Content
</motion.div>
```

#### Staggered Lists/Grids

```typescript
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

#### Card Hover Effects

```typescript
import { cardHover } from '@/lib/animations';

<motion.div
  variants={cardHover}
  initial="rest"
  whileHover="hover"
>
  Card content
</motion.div>
```

#### Button Press

```typescript
import { buttonPress } from '@/lib/animations';

<motion.button
  variants={buttonPress}
  whileTap="pressed"
>
  Click me
</motion.button>
```

### Animation Timing

- **Fast**: 0.2s - Micro-interactions, hover states
- **Normal**: 0.3s - Page transitions, card entrances (default)
- **Slow**: 0.5s - Complex animations, modal entrances
- **Slower**: 0.8s - Special effects, hero animations

### Animation Delays

Use delays sparingly and consistently:
- **0.1s**: First child in a staggered list
- **0.2s**: Secondary elements
- **0.3s+**: Tertiary elements or special emphasis

---

## Component Design Patterns

### Reusable Animated Components

We provide pre-built animated components in `frontend/components/ui/`:

#### AnimatedSection

Wrapper for page sections with fade-in and slide-up:

```typescript
import { AnimatedSection } from '@/components/ui';

<AnimatedSection delay={0.2}>
  <h1>Section Title</h1>
  <p>Section content</p>
</AnimatedSection>
```

#### AnimatedCard

Card with hover and entrance animations:

```typescript
import { AnimatedCard } from '@/components/ui';

<AnimatedCard hoverable delay={0.1}>
  <CardContent>Card content</CardContent>
</AnimatedCard>
```

#### AnimatedButton

Button with press animation:

```typescript
import { AnimatedButton } from '@/components/ui';

<AnimatedButton onClick={handleClick}>
  Submit
</AnimatedButton>
```

### Form Animations

Forms should use staggered animations for fields:

```typescript
import { staggerContainer, staggerItem } from '@/lib/animations';

<motion.div
  variants={staggerContainer}
  initial="hidden"
  animate="visible"
>
  <motion.div variants={staggerItem}>
    <FormField name="field1" />
  </motion.div>
  <motion.div variants={staggerItem}>
    <FormField name="field2" />
  </motion.div>
</motion.div>
```

---

## Color Schemes

### Primary Colors

- **Blue**: `blue-500` to `blue-700` - Primary actions, links
- **Indigo**: `indigo-500` to `indigo-700` - Secondary actions, accents
- **Purple**: `purple-500` to `purple-700` - Optional fields, special sections

### Semantic Colors

- **Success**: `green-500` - Success messages, completed states
- **Error**: `red-500` - Error messages, destructive actions
- **Warning**: `yellow-500` - Warnings, caution states
- **Info**: `blue-500` - Informational messages

### Background Gradients

Use subtle gradients for backgrounds:

```typescript
// Light mode
className="bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50"

// Dark mode
className="bg-gradient-to-br from-blue-950/20 via-indigo-950/20 to-purple-950/20"
```

### Glassmorphism

For cards and overlays:

```typescript
className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm"
```

---

## Typography

### Font Hierarchy

1. **Hero/Page Titles**: `text-5xl sm:text-6xl font-bold`
2. **Section Titles**: `text-3xl font-bold`
3. **Card Titles**: `text-xl font-semibold`
4. **Body Text**: `text-base` (default)
5. **Small Text**: `text-sm`

### Gradient Text

For emphasis:

```typescript
className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600"
```

---

## Spacing & Layout

### Container Patterns

```typescript
// Page container
<div className="container mx-auto px-4 sm:px-6 lg:px-8">

// Content wrapper
<div className="max-w-4xl mx-auto">

// Full-width section
<section className="w-full">
```

### Spacing Scale

- **xs**: `gap-2` or `space-y-2` - Tight spacing
- **sm**: `gap-4` or `space-y-4` - Default spacing
- **md**: `gap-6` or `space-y-6` - Section spacing
- **lg**: `gap-8` or `space-y-8` - Large sections
- **xl**: `gap-12` or `space-y-12` - Major sections

---

## Accessibility

### Reduced Motion

Always respect `prefers-reduced-motion`:

```typescript
import { useReducedMotion } from 'framer-motion';

const shouldReduceMotion = useReducedMotion();

<motion.div
  animate={shouldReduceMotion ? {} : { opacity: 1, y: 0 }}
>
  Content
</motion.div>
```

### Focus States

Ensure all interactive elements have visible focus states:

```typescript
className="focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:outline-none"
```

### ARIA Labels

Always provide ARIA labels for icon-only buttons and form fields:

```typescript
<Button aria-label="Close dialog">
  <X className="h-4 w-4" />
</Button>
```

---

## Best Practices

### DO ✅

- Use animation variants from `@/lib/animations`
- Keep animations subtle and purposeful
- Test with `prefers-reduced-motion`
- Use `transform` and `opacity` for performance
- Animate page transitions consistently
- Use staggered animations for lists/grids

### DON'T ❌

- Don't animate `width`, `height`, or `top/left` (use `transform`)
- Don't over-animate (less is more)
- Don't ignore reduced motion preferences
- Don't create custom animation variants without documenting them
- Don't use animations for critical information (accessibility)

---

## Examples

### Complete Page Example

```typescript
'use client';

import { motion } from 'framer-motion';
import { fadeInUp, staggerContainer, staggerItem } from '@/lib/animations';

export default function ExamplePage() {
  return (
    <div className="min-h-screen">
      {/* Header */}
      <motion.header
        initial="hidden"
        animate="visible"
        variants={fadeInUp}
      >
        Header content
      </motion.header>

      {/* Main content */}
      <main className="container mx-auto px-4 py-20">
        <motion.div
          initial="hidden"
          animate="visible"
          variants={fadeInUp}
          transition={{ delay: 0.2 }}
        >
          <h1>Page Title</h1>
        </motion.div>

        {/* Staggered grid */}
        <motion.div
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true }}
          variants={staggerContainer}
          className="grid grid-cols-1 md:grid-cols-3 gap-8 mt-12"
        >
          {items.map((item) => (
            <motion.div
              key={item.id}
              variants={staggerItem}
              whileHover={{ scale: 1.02, y: -4 }}
              className="card"
            >
              {item.content}
            </motion.div>
          ))}
        </motion.div>
      </main>
    </div>
  );
}
```

---

## Resources

- [Framer Motion Documentation](https://www.framer.com/motion/)
- [Animation Best Practices](https://web.dev/animations/)
- [Accessibility Guidelines](https://www.w3.org/WAI/WCAG21/Understanding/animation-from-interactions.html)

---

**Last Updated**: 2024-01-XX
**Maintained By**: Frontend Team

