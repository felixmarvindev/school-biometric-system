"use client"

import { Wifi, WifiOff, CheckCircle2, MapPin, Server } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { cn } from "@/lib/utils"
import { DEMO_DEVICES, type Device } from "@/lib/demo-data"

interface DeviceSelectorProps {
  selectedDevice: Device | null
  onSelect: (device: Device) => void
}

export function DeviceSelector({ selectedDevice, onSelect }: DeviceSelectorProps) {
  const onlineDevices = DEMO_DEVICES.filter((d) => d.status === "online")
  const offlineDevices = DEMO_DEVICES.filter((d) => d.status === "offline")

  return (
    <div className="space-y-6">
      {/* Online Devices */}
      <div>
        <div className="flex items-center gap-2 mb-3">
          <div className="size-2 rounded-full bg-success animate-pulse" />
          <span className="text-sm font-medium text-foreground">Available Devices ({onlineDevices.length})</span>
        </div>

        <div className="grid gap-3">
          {onlineDevices.map((device) => {
            const isSelected = selectedDevice?.id === device.id

            return (
              <button
                key={device.id}
                onClick={() => onSelect(device)}
                className={cn(
                  "w-full p-4 rounded-xl border-2 text-left transition-all",
                  "hover:border-primary/50 hover:bg-muted/30",
                  isSelected ? "border-primary bg-primary/5 ring-2 ring-primary/20" : "border-border bg-card",
                )}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex items-start gap-3">
                    <div
                      className={cn(
                        "relative flex items-center justify-center size-12 rounded-xl shrink-0 transition-all",
                        isSelected ? "bg-primary text-primary-foreground scale-105" : "bg-muted text-muted-foreground",
                      )}
                    >
                      <Server className="size-5" />
                      {isSelected && (
                        <div className="absolute -bottom-1 -right-1 size-5 rounded-full bg-background flex items-center justify-center">
                          <CheckCircle2 className="size-4 text-primary" />
                        </div>
                      )}
                    </div>

                    <div>
                      <div className="flex items-center gap-2 flex-wrap">
                        <span
                          className={cn(
                            "font-medium transition-colors",
                            isSelected ? "text-primary" : "text-foreground",
                          )}
                        >
                          {device.name}
                        </span>
                        <Badge className="bg-success/10 text-success border-0 text-xs">
                          <Wifi className="size-3 mr-1" />
                          Online
                        </Badge>
                      </div>
                      <div className="flex items-center gap-1 text-sm text-muted-foreground mt-1">
                        <MapPin className="size-3" />
                        {device.location}
                      </div>
                      <div className="text-xs text-muted-foreground mt-1">
                        {device.ipAddress}:{device.port} • {device.model}
                      </div>
                    </div>
                  </div>

                  <div
                    className={cn(
                      "flex items-center justify-center size-6 rounded-full border-2 transition-all shrink-0 mt-1",
                      isSelected ? "border-primary bg-primary" : "border-muted-foreground/30",
                    )}
                  >
                    {isSelected && <div className="size-2.5 rounded-full bg-primary-foreground" />}
                  </div>
                </div>
              </button>
            )
          })}
        </div>
      </div>

      {/* Offline Devices */}
      {offlineDevices.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <div className="size-2 rounded-full bg-muted-foreground" />
            <span className="text-sm font-medium text-muted-foreground">Unavailable ({offlineDevices.length})</span>
          </div>

          <div className="grid gap-3 opacity-60">
            {offlineDevices.map((device) => (
              <div key={device.id} className="p-4 rounded-xl border border-border bg-muted/30 cursor-not-allowed">
                <div className="flex items-start gap-3">
                  <div className="flex items-center justify-center size-12 rounded-xl bg-muted text-muted-foreground shrink-0">
                    <Server className="size-5" />
                  </div>

                  <div>
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-muted-foreground">{device.name}</span>
                      <Badge variant="secondary" className="text-xs">
                        <WifiOff className="size-3 mr-1" />
                        Offline
                      </Badge>
                    </div>
                    <div className="flex items-center gap-1 text-sm text-muted-foreground mt-1">
                      <MapPin className="size-3" />
                      {device.location}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
