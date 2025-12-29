/**
 * School Registration Page
 * 
 * TODO: This page will handle the school registration form submission.
 * After v0.dev generates the form component, integrate it here with API calls.
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowLeft } from 'lucide-react';
import { SchoolRegistrationForm } from '@/components/features/school/SchoolRegistrationForm';
import { registerSchool } from '@/lib/api/schools';
import type { SchoolRegistrationFormData } from '@/lib/validations/school';
import { Button } from '@/components/ui/button';
import { fadeInUp, slideInLeft, scaleIn } from '@/lib/animations';

export default function RegisterPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (data: SchoolRegistrationFormData) => {
    setIsLoading(true);
    setError(null);

    try {
      // TODO: Uncomment after implementing registerSchool function
      // const response = await registerSchool(data);
      // console.log('School registered:', response);
      
      // TODO: Handle success (show success message, redirect, etc.)
      // router.push('/login');
    } catch (err: unknown) {
      // TODO: Handle different error types (422, 409, 500)
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An error occurred while registering the school');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuccess = () => {
    // TODO: Implement success handling
    // Could show success toast, redirect to login, etc.
    console.log('Registration successful!');
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      {/* Colorful gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-blue-950/20 dark:via-indigo-950/20 dark:to-purple-950/20" />
      
      {/* Animated background shapes */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-400/30 rounded-full blur-3xl animate-pulse" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-400/30 rounded-full blur-3xl animate-pulse delay-1000" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-indigo-400/20 rounded-full blur-3xl" />
      </div>

      {/* Content */}
      <div className="relative z-10 w-full max-w-4xl mx-auto py-6 px-4 sm:px-6 lg:px-8 flex flex-col justify-center items-center">
        {/* Go Back Button */}
        
        
        <motion.div
          initial="hidden"
          animate="visible"
          variants={scaleIn}
          transition={{ delay: 0.2 }}
        >
          <motion.div
          initial="hidden"
          animate="visible"
          variants={slideInLeft}
          className="mb-6 "
        >
          <Link href="/">
            <Button
              variant="ghost"
              className="text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-white/50 dark:hover:bg-gray-800/50"
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Home
            </Button>
          </Link>
        </motion.div>
          <SchoolRegistrationForm
            onSubmit={handleSubmit}
            isLoading={isLoading}
            error={error}
            onSuccess={handleSuccess}
          />
        </motion.div>
      </div>
    </div>
  );
}

