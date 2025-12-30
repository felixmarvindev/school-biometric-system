"use client"

import { Separator } from "@/components/ui/separator"
import { Button } from "@/components/ui/button"
import { Avatar, AvatarFallback } from "@/components/ui/avatar"
import { SidebarTrigger } from "@/components/ui/sidebar"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip"
import { Bell, Calendar, Settings, LogOut } from "lucide-react"

export interface DashboardHeaderProps {
  title?: string
  adminName: string
  notificationCount?: number
  onLogout?: () => void
  onSettings?: () => void
}

export function DashboardHeader({
  title = "Dashboard",
  adminName,
  notificationCount = 0,
  onLogout,
  onSettings,
}: DashboardHeaderProps) {
  const initials = adminName
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2)

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-border/50 bg-background/80 px-4 backdrop-blur-md sm:px-6">
      <SidebarTrigger className="-ml-1" />
      <Separator orientation="vertical" className="h-6" />
      <div className="flex-1">
        <h1 className="text-lg font-semibold tracking-tight text-foreground sm:text-xl">{title}</h1>
      </div>
      <div className="flex items-center gap-2">
        <Tooltip>
          <TooltipTrigger asChild>
            <Button variant="ghost" size="icon" className="relative h-9 w-9">
              <Bell className="h-5 w-5" />
              {notificationCount > 0 && (
                <span className="absolute right-1.5 top-1.5 flex h-2 w-2">
                  <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-destructive opacity-75" />
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-destructive" />
                </span>
              )}
              <span className="sr-only">View notifications</span>
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>{notificationCount} new notifications</p>
          </TooltipContent>
        </Tooltip>
        <Tooltip>
          <TooltipTrigger asChild>
            <Button variant="ghost" size="icon" className="h-9 w-9">
              <Calendar className="h-5 w-5" />
              <span className="sr-only">View calendar</span>
            </Button>
          </TooltipTrigger>
          <TooltipContent>
            <p>Calendar</p>
          </TooltipContent>
        </Tooltip>
        <Separator orientation="vertical" className="mx-1 h-6" />
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-9 gap-2 px-2">
              <Avatar className="h-7 w-7">
                <AvatarFallback className="bg-primary text-xs text-primary-foreground">{initials}</AvatarFallback>
              </Avatar>
              <span className="hidden text-sm font-medium sm:inline-block">{adminName.split(" ")[0]}</span>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56 rounded-xl">
            <DropdownMenuItem onClick={onSettings}>
              <Settings className="mr-2 h-4 w-4" />
              Settings
            </DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-destructive focus:text-destructive" onClick={onLogout}>
              <LogOut className="mr-2 h-4 w-4" />
              Sign Out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  )
}

