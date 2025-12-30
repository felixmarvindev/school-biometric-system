"use client"

import { motion } from "framer-motion"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { School, MapPin, Phone, Mail, Settings } from "lucide-react"
import { fadeInUp } from "@/lib/animations/framer-motion"

export interface SchoolInfoCardProps {
  name: string
  code: string
  address?: string | null
  phone?: string | null
  email?: string | null
  onManageSettings?: () => void
}

export function SchoolInfoCard({
  name,
  code,
  address,
  phone,
  email,
  onManageSettings,
}: SchoolInfoCardProps) {
  return (
    <motion.div variants={fadeInUp} initial="hidden" animate="visible">
      <Card className="h-full border-none shadow-sm">
        <CardHeader className="pb-4">
          <div className="flex items-start justify-between">
            <div>
              <CardTitle className="text-lg font-semibold">School Information</CardTitle>
              <CardDescription>Your registered school details</CardDescription>
            </div>
            <Badge variant="outline" className="font-mono text-xs">
              {code}
            </Badge>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-4">
            <div className="flex items-start gap-3">
              <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                <School className="h-4 w-4 text-primary" />
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                  School Name
                </p>
                <p className="mt-0.5 font-medium text-foreground">{name}</p>
              </div>
            </div>

            {address && (
              <>
                <Separator />
                <div className="flex items-start gap-3">
                  <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                    <MapPin className="h-4 w-4 text-primary" />
                  </div>
                  <div className="min-w-0 flex-1">
                    <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                      Address
                    </p>
                    <p className="mt-0.5 text-sm text-foreground">{address}</p>
                  </div>
                </div>
              </>
            )}

            {(phone || email) && (
              <>
                <Separator />
                <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
                  {phone && (
                    <div className="flex items-start gap-3">
                      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                        <Phone className="h-4 w-4 text-primary" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                          Phone
                        </p>
                        <p className="mt-0.5 text-sm text-foreground">{phone}</p>
                      </div>
                    </div>
                  )}
                  {email && (
                    <div className="flex items-start gap-3">
                      <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary/10">
                        <Mail className="h-4 w-4 text-primary" />
                      </div>
                      <div className="min-w-0 flex-1">
                        <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground">
                          Email
                        </p>
                        <p className="mt-0.5 truncate text-sm text-foreground">{email}</p>
                      </div>
                    </div>
                  )}
                </div>
              </>
            )}
          </div>

          {onManageSettings && (
            <>
              <Separator />
              <Button variant="outline" className="w-full bg-transparent" size="sm" onClick={onManageSettings}>
                <Settings className="mr-2 h-4 w-4" />
                Manage School Settings
              </Button>
            </>
          )}
        </CardContent>
      </Card>
    </motion.div>
  )
}

