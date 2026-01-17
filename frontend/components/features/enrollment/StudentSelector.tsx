'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { GraduationCap, User, Loader2, ChevronRight } from 'lucide-react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { listStudents, type StudentResponse, StudentApiError } from '@/lib/api/students';
import { listClasses, type ClassResponse, ClassApiError } from '@/lib/api/classes';
import { useAuthStore } from '@/lib/store/authStore';

interface StudentSelectorProps {
  onSelect: (student: StudentResponse) => void;
  selectedStudent?: StudentResponse | null;
  onClassChange?: (classId: number) => void;
}

export function StudentSelector({ onSelect, selectedStudent, onClassChange }: StudentSelectorProps) {
  const { token } = useAuthStore();
  const [selectedClass, setSelectedClass] = useState<number | null>(null);
  const [classes, setClasses] = useState<ClassResponse[]>([]);
  const [students, setStudents] = useState<StudentResponse[]>([]);
  const [isLoadingClasses, setIsLoadingClasses] = useState(true);
  const [isLoadingStudents, setIsLoadingStudents] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load classes on mount
  useEffect(() => {
    if (!token) return;

    setIsLoadingClasses(true);
    setError(null);
    listClasses(token)
      .then((data) => {
        setClasses(data);
      })
      .catch((err) => {
        if (err instanceof ClassApiError) {
          setError(err.message);
        } else {
          setError('Failed to load classes');
        }
      })
      .finally(() => {
        setIsLoadingClasses(false);
      });
  }, [token]);

  // Load students when class is selected
  useEffect(() => {
    if (!token || !selectedClass) {
      setStudents([]);
      return;
    }

    setIsLoadingStudents(true);
    setError(null);
    listStudents(token, {
      class_id: selectedClass,
      page_size: 100, // Get all students in the class
    })
      .then((result) => {
        setStudents(result.items);
      })
      .catch((err) => {
        if (err instanceof StudentApiError) {
          setError(err.message);
        } else {
          setError('Failed to load students');
        }
        setStudents([]);
      })
      .finally(() => {
        setIsLoadingStudents(false);
      });
  }, [token, selectedClass]);

  const handleClassChange = (classId: string) => {
    const id = parseInt(classId, 10);
    setSelectedClass(id);
    // Notify parent of class change
    if (onClassChange) {
      onClassChange(id);
    }
  };

  const selectedClassData = classes.find(c => c.id === selectedClass);

  return (
    <div className="space-y-4">
      <div>
        <label className="text-sm font-medium text-blue-700 dark:text-blue-400">
          Select Student <span className="text-red-500">*</span>
        </label>
        <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
          First select a class, then choose a student from that class.
        </p>
      </div>

      {/* Class Selection */}
      <div className="space-y-2">
        <label className="text-xs font-medium text-gray-700 dark:text-gray-300">
          Step 1: Select Class
        </label>
        <Select
          value={selectedClass?.toString() || ''}
          onValueChange={handleClassChange}
          disabled={isLoadingClasses}
        >
          <SelectTrigger className="w-full border-blue-300 focus:border-blue-500 focus:ring-blue-500">
            <div className="flex items-center gap-2">
              <GraduationCap className="w-4 h-4 text-gray-400" />
              <SelectValue placeholder="Select a class...">
                {selectedClassData?.name || 'Select a class...'}
              </SelectValue>
            </div>
          </SelectTrigger>
          <SelectContent>
            {isLoadingClasses ? (
              <div className="flex items-center justify-center py-4">
                <Loader2 className="w-4 h-4 animate-spin text-blue-600" />
              </div>
            ) : classes.length === 0 ? (
              <div className="py-4 text-center text-sm text-gray-500">
                No classes available
              </div>
            ) : (
              classes.map((classItem) => (
                <SelectItem key={classItem.id} value={classItem.id.toString()}>
                  <div className="flex items-center gap-2">
                    <GraduationCap className="w-4 h-4" />
                    <span>{classItem.name}</span>
                  </div>
                </SelectItem>
              ))
            )}
          </SelectContent>
        </Select>
      </div>

      {/* Student Selection */}
      {selectedClass && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-2"
        >
          <label className="text-xs font-medium text-gray-700 dark:text-gray-300">
            Step 2: Select Student
          </label>
          
          {isLoadingStudents ? (
            <div className="flex items-center justify-center py-8 border border-gray-200 dark:border-gray-700 rounded-lg">
              <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
              <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">Loading students...</span>
            </div>
          ) : error ? (
            <div className="p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <div className="text-sm text-red-600 dark:text-red-400">{error}</div>
            </div>
          ) : students.length === 0 ? (
            <div className="p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg text-center">
              <div className="text-sm text-yellow-700 dark:text-yellow-400">
                No students found in {selectedClassData?.name}
              </div>
            </div>
          ) : (
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg max-h-64 overflow-y-auto">
              {students.map((student) => {
                const isSelected = selectedStudent?.id === student.id;
                return (
                  <div
                    key={student.id}
                    onClick={() => onSelect(student)}
                    className={`
                      p-4 cursor-pointer transition-all border-b border-gray-100 dark:border-gray-800 last:border-b-0
                      hover:bg-blue-50 dark:hover:bg-gray-700
                      ${isSelected 
                        ? 'bg-blue-100 dark:bg-blue-900/30 border-l-4 border-blue-600' 
                        : ''
                      }
                    `}
                  >
                    <div className="flex items-center gap-3">
                      <div className={`
                        flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center
                        ${isSelected 
                          ? 'bg-blue-600 text-white' 
                          : 'bg-gray-200 dark:bg-gray-700 text-gray-600 dark:text-gray-400'
                        }
                      `}>
                        <User className="w-5 h-5" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="font-medium text-gray-900 dark:text-gray-100">
                          {student.first_name} {student.last_name}
                        </div>
                        <div className="text-sm text-gray-500 dark:text-gray-400">
                          {student.admission_number}
                        </div>
                      </div>
                      {isSelected && (
                        <ChevronRight className="w-5 h-5 text-blue-600 dark:text-blue-400 flex-shrink-0" />
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </motion.div>
      )}

      {/* Selected Student Display */}
      {selectedStudent && (
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800"
        >
          <div className="flex items-center gap-3">
            <div className="flex-shrink-0 w-12 h-12 rounded-full bg-green-600 flex items-center justify-center text-white">
              <User className="w-6 h-6" />
            </div>
            <div className="flex-1">
              <div className="font-semibold text-gray-900 dark:text-gray-100">
                {selectedStudent.first_name} {selectedStudent.last_name}
              </div>
              <div className="text-sm text-gray-600 dark:text-gray-400">
                {selectedStudent.admission_number}
                {selectedClassData && ` • ${selectedClassData.name}`}
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
