'use client';

import { motion } from 'framer-motion';
import { toast } from 'sonner';
import { fadeInUp } from '@/lib/animations/framer-motion';
import { EnrollmentWizard } from '@/components/features/enrollment/EnrollmentWizard';

export default function EnrollmentPage() {
  const handleStartEnrollment = async (data: {
    studentId: number;
    deviceId: number;
    fingerId: number;
  }) => {
    try {
      // TODO: Phase 2 - Call enrollment API
      console.log('Enrollment completed:', data);
      
      // Simulate API call delay (in real implementation, this would be the actual API call)
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Show success message
      toast.success('Enrollment Successful', {
        description: `Fingerprint has been successfully enrolled. Student ID: ${data.studentId}, Device ID: ${data.deviceId}, Finger: ${data.fingerId}`,
        duration: 5000,
      });
      
      // In a real implementation, you might want to:
      // - Refresh student data to show updated enrollment status
      // - Navigate to a success page
      // - Show enrollment summary
    } catch (error) {
      console.error('Enrollment error:', error);
      toast.error('Enrollment Failed', {
        description: error instanceof Error ? error.message : 'An error occurred during enrollment',
        duration: 5000,
      });
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
