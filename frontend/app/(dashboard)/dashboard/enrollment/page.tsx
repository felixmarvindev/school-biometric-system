'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';
import { fadeInUp } from '@/lib/animations/framer-motion';
import { EnrollmentWizard } from '@/components/features/enrollment/EnrollmentWizard';
import { startEnrollment, EnrollmentApiError } from '@/lib/api/enrollment';

export default function EnrollmentPage() {

  const handleStartEnrollment = async (data: {
    studentId: number;
    deviceId: number;
    fingerId: number;
  }) => {
    try {
      // Call enrollment API
      const response = await startEnrollment({
        student_id: data.studentId,
        device_id: data.deviceId,
        finger_id: data.fingerId,
      });
      
      // Show success message
      toast.success('Enrollment Started', {
        description: `Enrollment session started. The device is now waiting for the student to place their finger.`,
        duration: 5000,
      });
      
      // Return session info to wizard component
      return response;
      
    } catch (error) {
      console.error('Enrollment error:', error);
      
      // Handle different error types
      if (error instanceof EnrollmentApiError) {
        // Show specific error message based on status code
        if (error.statusCode === 503) {
          toast.error('Device Offline', {
            description: 'The selected device is currently offline or unreachable. Please try again later or select a different device.',
            duration: 7000,
          });
        } else if (error.statusCode === 404) {
          toast.error('Not Found', {
            description: 'Student or device not found. Please check your selections and try again.',
            duration: 5000,
          });
        } else if (error.code === 'STUDENT_NOT_ON_DEVICE' || error.statusCode === 400) {
          toast.error('Student Not Synced', {
            description: error.message || 'Student is not synced to this device. Please sync the student first in the device selection step.',
            duration: 6000,
          });
        } else if (error.statusCode === 409) {
          toast.error('Enrollment In Progress', {
            description: 'An enrollment session is already in progress. Please wait for it to complete or cancel it first.',
            duration: 5000,
          });
        } else {
          // Generic error message
          toast.error('Enrollment Failed', {
            description: error.message || 'Failed to start enrollment. Please try again.',
            duration: 5000,
          });
        }
      } else {
        // Unexpected error
        toast.error('Enrollment Failed', {
          description: error instanceof Error ? error.message : 'An unexpected error occurred during enrollment',
          duration: 5000,
        });
      }
      
      // Re-throw error so wizard can handle it
      throw error;
    }
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
          
          <EnrollmentWizard onStartEnrollment={handleStartEnrollment} />
        </motion.div>
      </div>
    </div>
  );
}
