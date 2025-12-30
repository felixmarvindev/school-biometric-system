"use client"

import { motion } from "framer-motion"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { ScrollArea } from "@/components/ui/scroll-area"
import { ActivityItem, type ActivityItemProps } from "./ActivityItem"
import { fadeInUp } from "@/lib/animations/framer-motion"

export interface RecentActivityCardProps {
  activities: Omit<ActivityItemProps, "index">[]
}

export function RecentActivityCard({ activities }: RecentActivityCardProps) {
  return (
    <motion.div variants={fadeInUp} initial="hidden" animate="visible">
      <Card className="h-full border-none shadow-sm">
        <CardHeader className="pb-4">
          <CardTitle className="text-lg font-semibold">Recent Activity</CardTitle>
          <CardDescription>Latest updates in your system</CardDescription>
        </CardHeader>
        <CardContent>
          <ScrollArea className="h-[280px] pr-4">
            <div className="space-y-1">
              {activities.map((activity, index) => (
                <ActivityItem key={index} {...activity} index={index} />
              ))}
            </div>
          </ScrollArea>
        </CardContent>
      </Card>
    </motion.div>
  )
}

