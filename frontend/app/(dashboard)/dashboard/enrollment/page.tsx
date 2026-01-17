'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { fadeInUp } from '@/lib/animations/framer-motion';
import { EnrollmentWizard } from '@/components/features/enrollment/EnrollmentWizard';

export default function EnrollmentPage() {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleStartEnrollment = async (data: {
    studentId: number;
    deviceId: number;
    fingerId: number;
  }) => {
    setIsSubmitting(true);
    
    // TODO: Phase 2 - Call enrollment API
    console.log('Starting enrollment:', data);
    
    // Simulate API call delay
    await new Promise(resolve => setTimeout(resolve, 2000));
    
    setIsSubmitting(false);
    
    // TODO: Show success message and redirect or reset
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Animated background shapes */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-400/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-400/20 rounded-full blur-3xl animate-pulse delay-1000" />
      </div>

      <div className="relative z-10 container mx-auto px-4 py-8">
        <motion.div
          initial="hidden"
          animate="visible"
          variants={fadeInUp}
        >
          <div className="mb-8 text-center">
            <h1 className="text-4xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600 mb-2">
              Fingerprint Enrollment
            </h1>
            <p className="text-gray-600 dark:text-gray-400 text-lg">
              Follow the steps below to enroll a student's fingerprint for biometric attendance
            </p>
          </div>
          
          <EnrollmentWizard
            onStartEnrollment={handleStartEnrollment}
            isSubmitting={isSubmitting}
          />
        </motion.div>
      </div>
    </div>
  );
}
