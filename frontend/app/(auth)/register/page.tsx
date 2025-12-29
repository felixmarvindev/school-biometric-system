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
import { ArrowLeft, CheckCircle2 } from 'lucide-react';
import { SchoolRegistrationForm } from '@/components/features/school/SchoolRegistrationForm';
import { registerSchool, SchoolRegistrationError } from '@/lib/api/schools';
import type { SchoolRegistrationFormData } from '@/lib/validations/school';
import { Button } from '@/components/ui/button';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { fadeInUp, slideInLeft, scaleIn } from '@/lib/animations';

export default function RegisterPage() {
  const router = useRouter();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [success, setSuccess] = useState(false);
  const [registeredSchool, setRegisteredSchool] = useState<{ name: string; code: string } | null>(null);

  const handleSubmit = async (data: SchoolRegistrationFormData) => {
    setIsLoading(true);
    setError(null);
    setFieldErrors({});
    setSuccess(false);

    try {
      const response = await registerSchool(data);
      
      // Store registered school info for success message
      setRegisteredSchool({
        name: response.name,
        code: response.code,
      });
      
      setSuccess(true);
      
      // Redirect to login after 3 seconds
      setTimeout(() => {
        router.push('/login');
      }, 3000);
    } catch (err: unknown) {
      // Handle SchoolRegistrationError with comprehensive error handling
      if (err instanceof SchoolRegistrationError) {
        // Set general error message
        setError(err.message);
        
        // Set field-level errors if available (from 422 validation errors)
        if (err.fieldErrors && Object.keys(err.fieldErrors).length > 0) {
          setFieldErrors(err.fieldErrors);
        }
        
        // For 409 (duplicate code), also set field error on code field
        if (err.statusCode === 409) {
          setFieldErrors({ code: err.message });
        }
      } else if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('An error occurred while registering the school. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuccess = () => {
    // This is called by the form component after successful submission
    // The actual success handling is done in handleSubmit above
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
            className="mb-6"
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

          {/* Success Message */}
          {success && registeredSchool && (
            <motion.div
              initial="hidden"
              animate="visible"
              variants={fadeInUp}
              className="mb-6 w-full max-w-2xl"
            >
              <Alert className="border-green-200 dark:border-green-900/50 bg-green-50 dark:bg-green-950/20">
                <CheckCircle2 className="h-4 w-4 text-green-600 dark:text-green-400" />
                <AlertDescription className="text-green-800 dark:text-green-200">
                  <div className="font-semibold mb-1">Registration Successful!</div>
                  <div>
                    School <strong>{registeredSchool.name}</strong> (Code: <strong>{registeredSchool.code}</strong>) has been registered successfully.
                    You will be redirected to the login page in a few seconds...
                  </div>
                </AlertDescription>
              </Alert>
            </motion.div>
          )}

          <SchoolRegistrationForm
            onSubmit={handleSubmit}
            isLoading={isLoading}
            error={error}
            fieldErrors={fieldErrors}
            onSuccess={handleSuccess}
          />
        </motion.div>
      </div>
    </div>
  );
}

