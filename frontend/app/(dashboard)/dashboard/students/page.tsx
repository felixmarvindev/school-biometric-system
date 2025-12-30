"use client"

import { useState, useEffect, useCallback } from "react"
import { useRouter } from "next/navigation"
import { motion } from "framer-motion"
import { StudentList } from "@/components/features/students/StudentList"
import { useAuthStore } from "@/lib/store/authStore"
import {
  listStudents,
  type StudentResponse,
  StudentApiError,
} from "@/lib/api/students"
import { listClasses, type ClassResponse } from "@/lib/api/classes"
import { listStreams, type StreamResponse } from "@/lib/api/streams"
import { pageTransition } from "@/lib/animations/framer-motion"
import { useDebounce } from "@/lib/hooks/useDebounce"

export default function StudentsPage() {
  const router = useRouter()
  const { token } = useAuthStore()
  const [students, setStudents] = useState<StudentResponse[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(50)
  const [search, setSearch] = useState("")
  const [classFilter, setClassFilter] = useState<number | null>(null)
  const [streamFilter, setStreamFilter] = useState<number | null>(null)
  const [totalPages, setTotalPages] = useState(0)
  const [total, setTotal] = useState(0)
  const [classes, setClasses] = useState<ClassResponse[]>([])
  const [streams, setStreams] = useState<StreamResponse[]>([])

  // Debounce search input
  const debouncedSearch = useDebounce(search, 300)

  // Fetch students
  const fetchStudents = useCallback(async () => {
    if (!token) return

    try {
      setIsLoading(true)
      setError(null)
      const result = await listStudents(token, {
        page,
        page_size: pageSize,
        search: debouncedSearch || undefined,
        class_id: classFilter || undefined,
        stream_id: streamFilter || undefined,
      })
      setStudents(result.items)
      setTotalPages(result.total_pages)
      setTotal(result.total)
    } catch (err) {
      if (err instanceof StudentApiError) {
        setError(err.message)
      } else {
        setError("Failed to load students. Please try again.")
      }
      setStudents([])
    } finally {
      setIsLoading(false)
    }
  }, [token, page, pageSize, debouncedSearch, classFilter, streamFilter])

  useEffect(() => {
    fetchStudents()
  }, [fetchStudents])

  // Reset to page 1 when filters change
  useEffect(() => {
    setPage(1)
  }, [debouncedSearch, classFilter, streamFilter])

  // Fetch classes and streams
  useEffect(() => {
    if (token) {
      const fetchClassesAndStreams = async () => {
        try {
          const [classesData, streamsData] = await Promise.all([
            listClasses(token),
            listStreams(token),
          ])
          setClasses(classesData)
          setStreams(streamsData)
        } catch (err) {
          console.error("Failed to load classes/streams:", err)
        }
      }
      fetchClassesAndStreams()
    }
  }, [token])

  const handleAddStudent = () => {
    router.push("/dashboard/students/new")
  }

  const handleStudentClick = (id: number) => {
    router.push(`/dashboard/students/${id}`)
  }

  return (
    <motion.main
      variants={pageTransition}
      initial="initial"
      animate="animate"
      className="flex-1 space-y-6 p-4 sm:p-6 lg:p-8"
    >
      <StudentList
        students={students}
        isLoading={isLoading}
        error={error}
        search={search}
        onSearchChange={setSearch}
        classFilter={classFilter}
        onClassFilterChange={setClassFilter}
        streamFilter={streamFilter}
        onStreamFilterChange={setStreamFilter}
        page={page}
        totalPages={totalPages}
        total={total}
        onPageChange={setPage}
        onAddStudent={handleAddStudent}
        onStudentClick={handleStudentClick}
        classes={classes.map((c) => ({ id: c.id, name: c.name }))}
        streams={streams.map((s) => ({ id: s.id, name: s.name, class_id: s.class_id }))}
      />
    </motion.main>
  )
}

