"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Alert, AlertDescription } from "@/components/ui/alert"
import { Loader2, AlertCircle } from "lucide-react"
import { fadeInUp } from "@/lib/animations/framer-motion"
import {
  createStream,
  updateStream,
  type StreamResponse,
  type StreamCreateData,
  type StreamUpdateData,
  StreamApiError,
} from "@/lib/api/streams"

export interface StreamFormProps {
  classId: number
  streamData?: StreamResponse
  onSuccess: () => void
  onCancel: () => void
}

export function StreamForm({
  classId,
  streamData,
  onSuccess,
  onCancel,
}: StreamFormProps) {
  const [name, setName] = useState(streamData?.name || "")
  const [description, setDescription] = useState(streamData?.description || "")
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!name.trim()) {
      setError("Stream name is required")
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const { token } = await import("@/lib/store/authStore").then(
        (m) => m.useAuthStore.getState()
      )

      if (!token) {
        throw new Error("Authentication required")
      }

      const data: StreamCreateData | StreamUpdateData = {
        name: name.trim(),
        description: description.trim() || null,
      }

      if (streamData) {
        await updateStream(token, streamData.id, data)
      } else {
        await createStream(token, { ...data, class_id: classId })
      }

      onSuccess()
    } catch (err) {
      if (err instanceof StreamApiError) {
        setError(err.message)
      } else {
        setError("Failed to save stream. Please try again.")
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <motion.form
      initial="hidden"
      animate="visible"
      variants={fadeInUp}
      onSubmit={handleSubmit}
      className="space-y-4"
    >
      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      <div className="space-y-2">
        <Label htmlFor="name" className="text-blue-700 dark:text-blue-400">
          Stream Name <span className="text-red-500">*</span>
        </Label>
        <Input
          id="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g., A, B, C"
          className="border-blue-300 focus:border-blue-500 focus:ring-blue-500"
          required
          disabled={isLoading}
        />
      </div>

      <div className="space-y-2">
        <Label htmlFor="description" className="text-gray-700 dark:text-gray-300">
          Description (Optional)
        </Label>
        <Textarea
          id="description"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="Optional description for this stream"
          className="border-gray-300 focus:border-purple-500 focus:ring-purple-500"
          rows={3}
          disabled={isLoading}
        />
      </div>

      <div className="flex gap-3 pt-2">
        <Button
          type="submit"
          disabled={isLoading || !name.trim()}
          className="bg-indigo-600 hover:bg-indigo-700"
        >
          {isLoading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
          {streamData ? "Update Stream" : "Create Stream"}
        </Button>
        <Button
          type="button"
          variant="outline"
          onClick={onCancel}
          disabled={isLoading}
        >
          Cancel
        </Button>
      </div>
    </motion.form>
  )
}

