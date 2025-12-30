"use client"

import { motion } from "framer-motion"
import { Card, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Eye, Calendar, User, Phone, Mail } from "lucide-react"
import { staggerItem, cardHover } from "@/lib/animations/framer-motion"
import type { StudentResponse } from "@/lib/api/students"
import { formatDate } from "@/lib/utils"

export interface StudentCardGridProps {
  students: StudentResponse[]
  onStudentClick: (id: number) => void
}

export function StudentCardGrid({ students, onStudentClick }: StudentCardGridProps) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
      {students.map((student, index) => (
        <motion.div
          key={student.id}
          variants={staggerItem}
          initial="hidden"
          animate="visible"
        >
          <motion.div
            variants={cardHover}
            initial="rest"
            whileHover="hover"
            animate="rest"
          >
            <Card
              className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 cursor-pointer transition-all hover:shadow-lg"
              onClick={() => onStudentClick(student.id)}
            >
              <CardContent className="p-6">
                {/* Header */}
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Badge variant="outline" className="font-mono">
                        {student.admission_number}
                      </Badge>
                    </div>
                    <h3 className="text-lg font-semibold">
                      {student.first_name} {student.last_name}
                    </h3>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation()
                      onStudentClick(student.id)
                    }}
                    className="hover:bg-blue-50 dark:hover:bg-blue-900/20"
                  >
                    <Eye className="h-4 w-4" />
                  </Button>
                </div>

                {/* Details */}
                <div className="space-y-2 text-sm text-muted-foreground">
                  {student.date_of_birth && (
                    <div className="flex items-center gap-2">
                      <Calendar className="h-4 w-4" />
                      <span>{formatDate(student.date_of_birth)}</span>
                    </div>
                  )}
                  {student.gender && (
                    <div className="flex items-center gap-2">
                      <User className="h-4 w-4" />
                      <Badge variant="secondary" className="capitalize">
                        {student.gender}
                      </Badge>
                    </div>
                  )}
                  {(student.class_id || student.stream_id) && (
                    <div className="text-sm">
                      {student.class_id && student.stream_id
                        ? `Form ${student.class_id}-${student.stream_id}`
                        : student.class_id
                        ? `Form ${student.class_id}`
                        : ""}
                    </div>
                  )}
                </div>

                {/* Parent Contact */}
                {(student.parent_phone || student.parent_email) && (
                  <div className="mt-4 pt-4 border-t border-gray-200/50 dark:border-gray-700/50 space-y-2">
                    {student.parent_phone && (
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Phone className="h-4 w-4" />
                        <span>{student.parent_phone}</span>
                      </div>
                    )}
                    {student.parent_email && (
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Mail className="h-4 w-4" />
                        <span className="truncate">{student.parent_email}</span>
                      </div>
                    )}
                  </div>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>
      ))}
    </div>
  )
}

