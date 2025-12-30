"use client"

import { motion } from "framer-motion"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { Eye } from "lucide-react"
import { staggerItem } from "@/lib/animations/framer-motion"
import type { StudentResponse } from "@/lib/api/students"
import { formatDate } from "@/lib/utils"

export interface StudentTableProps {
  students: StudentResponse[]
  onStudentClick: (id: number) => void
}

export function StudentTable({ students, onStudentClick }: StudentTableProps) {
  return (
    <Card className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 overflow-hidden">
      <div className="overflow-x-auto">
        <Table>
          <TableHeader>
            <TableRow className="border-gray-200/50 dark:border-gray-700/50">
              <TableHead className="font-semibold">Admission Number</TableHead>
              <TableHead className="font-semibold">Name</TableHead>
              <TableHead className="font-semibold">Date of Birth</TableHead>
              <TableHead className="font-semibold">Gender</TableHead>
              <TableHead className="font-semibold">Class/Stream</TableHead>
              <TableHead className="font-semibold">Parent Contact</TableHead>
              <TableHead className="font-semibold text-right">Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {students.map((student, index) => (
              <motion.tr
                key={student.id}
                variants={staggerItem}
                initial="hidden"
                animate="visible"
                className="border-gray-200/50 dark:border-gray-700/50 hover:bg-gray-50/50 dark:hover:bg-gray-800/50 transition-colors cursor-pointer"
                onClick={() => onStudentClick(student.id)}
              >
                <TableCell className="font-medium">
                  <Badge variant="outline" className="font-mono">
                    {student.admission_number}
                  </Badge>
                </TableCell>
                <TableCell>
                  <div className="font-medium">
                    {student.first_name} {student.last_name}
                  </div>
                </TableCell>
                <TableCell className="text-muted-foreground">
                  {student.date_of_birth
                    ? formatDate(student.date_of_birth)
                    : "—"}
                </TableCell>
                <TableCell>
                  {student.gender ? (
                    <Badge variant="secondary" className="capitalize">
                      {student.gender}
                    </Badge>
                  ) : (
                    <span className="text-muted-foreground">—</span>
                  )}
                </TableCell>
                <TableCell className="text-muted-foreground">
                  {student.class_id && student.stream_id
                    ? `Form ${student.class_id}-${student.stream_id}`
                    : student.class_id
                    ? `Form ${student.class_id}`
                    : "—"}
                </TableCell>
                <TableCell className="text-muted-foreground">
                  <div className="space-y-1">
                    {student.parent_phone && (
                      <div className="text-sm">{student.parent_phone}</div>
                    )}
                    {student.parent_email && (
                      <div className="text-sm">{student.parent_email}</div>
                    )}
                    {!student.parent_phone && !student.parent_email && "—"}
                  </div>
                </TableCell>
                <TableCell className="text-right">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={(e) => {
                      e.stopPropagation()
                      onStudentClick(student.id)
                    }}
                    className="hover:bg-blue-50 dark:hover:bg-blue-900/20"
                  >
                    <Eye className="h-4 w-4 mr-2" />
                    View
                  </Button>
                </TableCell>
              </motion.tr>
            ))}
          </TableBody>
        </Table>
      </div>
    </Card>
  )
}

