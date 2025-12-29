/**
 * Animated Card Component
 * 
 * A card component with hover and entrance animations.
 * Use this for feature cards, info cards, etc.
 */

'use client';

import { motion } from 'framer-motion';
import { scaleIn, cardHover } from '@/lib/animations';
import { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface AnimatedCardProps {
  children: ReactNode;
  className?: string;
  delay?: number;
  hoverable?: boolean;
}

export function AnimatedCard({
  children,
  className,
  delay = 0,
  hoverable = true,
}: AnimatedCardProps) {
  return (
    <motion.div
      variants={hoverable ? cardHover : scaleIn}
      initial="hidden"
      animate="visible"
      whileHover={hoverable ? 'hover' : undefined}
      transition={{ delay }}
      className={cn('cursor-pointer', className)}
    >
      {children}
    </motion.div>
  );
}

