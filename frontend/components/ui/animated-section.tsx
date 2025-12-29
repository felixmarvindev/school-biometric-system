/**
 * Animated Section Component
 * 
 * A reusable wrapper component for animated sections with fade-in and slide-up effects.
 * Use this for consistent page animations.
 */

'use client';

import { motion, MotionProps } from 'framer-motion';
import { fadeInUp } from '@/lib/animations';
import { ReactNode } from 'react';

interface AnimatedSectionProps extends Omit<MotionProps, 'initial' | 'animate' | 'variants'> {
  children: ReactNode;
  delay?: number;
  className?: string;
}

export function AnimatedSection({
  children,
  delay = 0,
  className,
  ...props
}: AnimatedSectionProps) {
  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      animate="visible"
      transition={{ delay }}
      className={className}
      {...props}
    >
      {children}
    </motion.div>
  );
}

