/**
 * Animated Button Component
 * 
 * A button with press animation and smooth transitions.
 * Wraps shadcn/ui Button with animation.
 */

'use client';

import { motion } from 'framer-motion';
import { buttonPress } from '@/lib/animations';
import { Button, } from '@/components/ui/button';
import { ReactNode } from 'react';
type ButtonProps = React.ComponentProps<typeof Button>;

interface AnimatedButtonProps extends ButtonProps {
  children: ReactNode;
}

export function AnimatedButton({ children, ...props }: AnimatedButtonProps) {
  return (
    <motion.div
      variants={buttonPress}
      initial="rest"
      whileHover="rest"
      whileTap="pressed"
    >
      <Button {...props}>{children}</Button>
    </motion.div>
  );
}

