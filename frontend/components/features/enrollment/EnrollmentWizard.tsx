'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, Circle, ChevronRight, ChevronLeft, User, Smartphone, Fingerprint, Play } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { StudentSelector } from './StudentSelector';
import { DeviceSelector } from './DeviceSelector';
import { FingerSelector } from './FingerSelector';
import type { StudentResponse } from '@/lib/api/students';
import type { DeviceResponse } from '@/lib/api/devices';

const STEPS = [
  { id: 1, name: 'Select Student', icon: User, description: 'Choose a student to enroll' },
  { id: 2, name: 'Choose Device', icon: Smartphone, description: 'Select a biometric device' },
  { id: 3, name: 'Select Finger', icon: Fingerprint, description: 'Choose which finger to enroll' },
  { id: 4, name: 'Start Enrollment', icon: Play, description: 'Begin the enrollment process' },
];

interface EnrollmentWizardProps {
  onStartEnrollment: (data: {
    studentId: number;
    deviceId: number;
    fingerId: number;
  }) => Promise<void>;
  isSubmitting?: boolean;
}

export function EnrollmentWizard({ onStartEnrollment, isSubmitting = false }: EnrollmentWizardProps) {
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedStudent, setSelectedStudent] = useState<StudentResponse | null>(null);
  const [selectedDevice, setSelectedDevice] = useState<DeviceResponse | null>(null);
  const [selectedFinger, setSelectedFinger] = useState<number | null>(null);
  const [selectedClassId, setSelectedClassId] = useState<number | null>(null);

  const canProceed = () => {
    switch (currentStep) {
      case 1:
        return selectedStudent !== null;
      case 2:
        return selectedDevice !== null && selectedDevice.status === 'online';
      case 3:
        return selectedFinger !== null;
      default:
        return false;
    }
  };

  const handleNext = () => {
    if (canProceed() && currentStep < STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleStartEnrollment = async () => {
    if (!selectedStudent || !selectedDevice || selectedFinger === null) return;
    
    await onStartEnrollment({
      studentId: selectedStudent.id,
      deviceId: selectedDevice.id,
      fingerId: selectedFinger,
    });
  };

  const getStepStatus = (stepId: number) => {
    if (stepId < currentStep) return 'completed';
    if (stepId === currentStep) return 'active';
    return 'pending';
  };

  return (
    <div className="w-full max-w-5xl mx-auto">
      {/* Step Indicator */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          {STEPS.map((step, index) => {
            const status = getStepStatus(step.id);
            const isLast = index === STEPS.length - 1;
            
            return (
              <React.Fragment key={step.id}>
                <div className="flex flex-col items-center flex-1">
                  <div className="flex items-center w-full">
                    {/* Step Circle */}
                    <div className="flex flex-col items-center flex-1">
                      <motion.div
                        initial={false}
                        animate={{
                          scale: status === 'active' ? 1.1 : 1,
                        }}
                        className={`
                          relative flex items-center justify-center w-12 h-12 rounded-full border-2 transition-all
                          ${
                            status === 'completed'
                              ? 'bg-blue-600 border-blue-600 text-white'
                              : status === 'active'
                              ? 'bg-blue-50 border-blue-600 text-blue-600 dark:bg-blue-900/30'
                              : 'bg-white border-gray-300 text-gray-400 dark:bg-gray-800 dark:border-gray-700'
                          }
                        `}
                      >
                        {status === 'completed' ? (
                          <CheckCircle2 className="w-6 h-6" />
                        ) : (
                          <step.icon className="w-6 h-6" />
                        )}
                        {status === 'active' && (
                          <motion.div
                            className="absolute inset-0 rounded-full border-2 border-blue-600"
                            animate={{ scale: [1, 1.2, 1] }}
                            transition={{ duration: 2, repeat: Infinity }}
                          />
                        )}
                      </motion.div>
                      <div className="mt-2 text-center">
                        <div
                          className={`text-xs font-medium ${
                            status === 'active'
                              ? 'text-blue-600 dark:text-blue-400'
                              : status === 'completed'
                              ? 'text-gray-700 dark:text-gray-300'
                              : 'text-gray-400 dark:text-gray-600'
                          }`}
                        >
                          {step.name}
                        </div>
                      </div>
                    </div>
                    {/* Connector Line */}
                    {!isLast && (
                      <div
                        className={`flex-1 h-0.5 mx-2 ${
                          status === 'completed' ? 'bg-blue-600' : 'bg-gray-300 dark:bg-gray-700'
                        }`}
                      />
                    )}
                  </div>
                </div>
              </React.Fragment>
            );
          })}
        </div>
      </div>

      {/* Step Content */}
      <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl shadow-xl p-8 border border-gray-200/50 dark:border-gray-700/50 min-h-[500px]">
        <AnimatePresence mode="wait">
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3 }}
          >
            {/* Step 1: Student Selection */}
            {currentStep === 1 && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                    Select Student
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400">
                    Choose a student from your school to enroll their fingerprint
                  </p>
                </div>
                <StudentSelector
                  onSelect={(student) => {
                    setSelectedStudent(student);
                    if (student.class_id !== selectedClassId) {
                      setSelectedClassId(student.class_id);
                    }
                  }}
                  selectedStudent={selectedStudent}
                  onClassChange={(classId) => {
                    setSelectedClassId(classId);
                    if (selectedStudent && selectedStudent.class_id !== classId) {
                      setSelectedStudent(null);
                    }
                  }}
                />
              </div>
            )}

            {/* Step 2: Device Selection */}
            {currentStep === 2 && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                    Choose Device
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400">
                    Select an available biometric device for enrollment
                  </p>
                </div>
                <DeviceSelector
                  onSelect={setSelectedDevice}
                  selectedDevice={selectedDevice}
                />
                {selectedDevice && selectedDevice.status !== 'online' && (
                  <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                    <div className="text-sm text-red-700 dark:text-red-400">
                      ⚠️ This device is offline. Please select an online device to proceed.
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Step 3: Finger Selection */}
            {currentStep === 3 && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                    Select Finger
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400">
                    Click on a finger in the hand illustrations to select it for enrollment
                  </p>
                </div>
                <FingerSelector
                  onSelect={setSelectedFinger}
                  selectedFinger={selectedFinger}
                />
              </div>
            )}

            {/* Step 4: Review & Start */}
            {currentStep === 4 && (
              <div className="space-y-6">
                <div>
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-gray-100 mb-2">
                    Review & Start Enrollment
                  </h2>
                  <p className="text-gray-600 dark:text-gray-400">
                    Review your selections and start the enrollment process
                  </p>
                </div>

                {/* Review Summary */}
                <div className="space-y-4">
                  <div className="p-4 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-10 h-10 rounded-full bg-blue-600 flex items-center justify-center text-white">
                        <User className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-600 dark:text-gray-400">Student</div>
                        <div className="font-semibold text-gray-900 dark:text-gray-100">
                          {selectedStudent?.first_name} {selectedStudent?.last_name}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                          {selectedStudent?.admission_number}
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="p-4 bg-indigo-50 dark:bg-indigo-900/20 border border-indigo-200 dark:border-indigo-800 rounded-lg">
                    <div className="flex items-center gap-3 mb-3">
                      <div className="w-10 h-10 rounded-full bg-indigo-600 flex items-center justify-center text-white">
                        <Smartphone className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-600 dark:text-gray-400">Device</div>
                        <div className="font-semibold text-gray-900 dark:text-gray-100">
                          {selectedDevice?.name}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                          {selectedDevice?.location || selectedDevice?.ip_address}
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="p-4 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-purple-600 flex items-center justify-center text-white">
                        <Fingerprint className="w-5 h-5" />
                      </div>
                      <div>
                        <div className="text-sm font-medium text-gray-600 dark:text-gray-400">Finger</div>
                        <div className="font-semibold text-gray-900 dark:text-gray-100">
                          Finger ID: {selectedFinger}
                        </div>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Start Button */}
                <div className="pt-4">
                  <Button
                    onClick={handleStartEnrollment}
                    disabled={isSubmitting}
                    className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white shadow-lg hover:shadow-xl transition-all"
                    size="lg"
                  >
                    {isSubmitting ? (
                      <span className="flex items-center justify-center gap-2">
                        <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></span>
                        Starting Enrollment...
                      </span>
                    ) : (
                      <span className="flex items-center justify-center gap-2">
                        <Play className="w-5 h-5" />
                        Start Enrollment
                      </span>
                    )}
                  </Button>
                </div>
              </div>
            )}
          </motion.div>
        </AnimatePresence>

        {/* Navigation Buttons */}
        {currentStep < 4 && (
          <div className="flex justify-between items-center mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
            <Button
              variant="outline"
              onClick={handlePrevious}
              disabled={currentStep === 1}
              className="flex items-center gap-2"
            >
              <ChevronLeft className="w-4 h-4" />
              Previous
            </Button>
            <Button
              onClick={handleNext}
              disabled={!canProceed()}
              className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700 text-white"
            >
              Next
              <ChevronRight className="w-4 h-4" />
            </Button>
          </div>
        )}
      </div>
    </div>
  );
}
