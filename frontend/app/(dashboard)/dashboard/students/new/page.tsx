"use client"

import { motion } from "framer-motion"
import { StudentForm } from "@/components/features/students/StudentForm"
import { pageTransition } from "@/lib/animations/framer-motion"

export default function NewStudentPage() {
  return (
    <motion.main
      variants={pageTransition}
      initial="initial"
      animate="animate"
      className="flex-1 space-y-6 p-4 sm:p-6 lg:p-8"
    >
      <StudentForm />
    </motion.main>
  )
}

