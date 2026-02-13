"use client"

import { useParams } from "next/navigation"
import { motion } from "framer-motion"
import { StudentWizard } from "@/components/features/students/StudentWizard"
import { pageTransition } from "@/lib/animations/framer-motion"

export default function EditStudentPage() {
  const params = useParams()
  const studentId = params.id ? parseInt(params.id as string) : undefined

  return (
    <motion.main
      variants={pageTransition}
      initial="initial"
      animate="animate"
      className="flex-1 space-y-6 p-4 sm:p-6 lg:p-8"
    >
      <StudentWizard mode="edit" studentId={studentId} />
    </motion.main>
  )
}

