"use client"

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarRail,
} from "@/components/ui/sidebar"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { Badge } from "@/components/ui/badge"
import { ScrollArea } from "@/components/ui/scroll-area"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  LayoutDashboard,
  Users,
  Smartphone,
  ClipboardCheck,
  UserPlus,
  Bell,
  Settings,
  School,
  HelpCircle,
  LogOut,
  ChevronUp,
  LucideIcon,
} from "lucide-react"
import Link from "next/link"

export interface NavigationItem {
  name: string
  icon: LucideIcon
  href: string
  current?: boolean
  badge?: number
}

export interface DashboardSidebarProps {
  adminName: string
  adminEmail: string
  adminAvatar?: string | null
  currentPath?: string
  onLogout?: () => void
  onSettings?: () => void
}

const coreNavigation: NavigationItem[] = [
  { name: "Dashboard", icon: LayoutDashboard, href: "/dashboard" },
  { name: "Students", icon: Users, href: "/dashboard/students" },
  { name: "Devices", icon: Smartphone, href: "/dashboard/devices" },
  { name: "Attendance", icon: ClipboardCheck, href: "/dashboard/attendance" },
  { name: "Enrollment", icon: UserPlus, href: "/dashboard/enrollment" },
]

const systemNavigation: NavigationItem[] = [
  { name: "Notifications", icon: Bell, href: "/dashboard/notifications", badge: 3 },
  { name: "Settings", icon: Settings, href: "/dashboard/settings" },
  { name: "Help & Support", icon: HelpCircle, href: "/dashboard/help" },
]

export function DashboardSidebar({ 
  adminName, 
  adminEmail, 
  adminAvatar, 
  currentPath,
  onLogout, 
  onSettings 
}: DashboardSidebarProps) {
  const initials = adminName
    .split(" ")
    .map((n) => n[0])
    .join("")
    .toUpperCase()
    .slice(0, 2)

  return (
    <Sidebar collapsible="icon" className="border-r border-border/50 bg-sidebar">
      <SidebarHeader className="border-b border-border/50 p-4">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground shadow-sm">
            <School className="h-5 w-5" />
          </div>
          <div className="flex flex-col gap-0.5 leading-none group-data-[collapsible=icon]:hidden">
            <span className="font-semibold tracking-tight text-foreground">SchoolAdmin</span>
            <span className="text-xs text-muted-foreground">Management System</span>
          </div>
        </div>
      </SidebarHeader>

      <SidebarContent>
        <ScrollArea className="h-full">
          {/* Core Navigation */}
          <SidebarGroup>
            <SidebarGroupLabel className="text-xs font-medium uppercase tracking-wider text-muted-foreground/70">
              Core
            </SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {coreNavigation.map((item) => {
                  const isActive = currentPath === item.href || (item.href !== "/dashboard" && currentPath?.startsWith(item.href))
                  return (
                    <SidebarMenuItem key={item.name}>
                      <SidebarMenuButton asChild isActive={isActive} tooltip={item.name}>
                        <Link href={item.href} className="transition-colors">
                          <item.icon className="h-4 w-4" />
                          <span>{item.name}</span>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  )
                })}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>

          {/* System Navigation */}
          <SidebarGroup>
            <SidebarGroupLabel className="text-xs font-medium uppercase tracking-wider text-muted-foreground/70">
              System
            </SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                {systemNavigation.map((item) => {
                  const isActive = currentPath === item.href || (item.href !== "/dashboard/settings" && currentPath?.startsWith(item.href))
                  return (
                    <SidebarMenuItem key={item.name}>
                      <SidebarMenuButton asChild isActive={isActive} tooltip={item.name}>
                        <Link href={item.href} className="relative transition-colors">
                          <item.icon className="h-4 w-4" />
                          <span>{item.name}</span>
                          {item.badge && (
                            <Badge
                              variant="destructive"
                              className="ml-auto h-5 min-w-5 rounded-full px-1.5 text-xs font-medium"
                            >
                              {item.badge}
                            </Badge>
                          )}
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  )
                })}
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </ScrollArea>
      </SidebarContent>

      <SidebarFooter className="border-t border-border/50 p-2">
        <SidebarMenu>
          <SidebarMenuItem>
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <SidebarMenuButton
                  size="lg"
                  className="data-[state=open]:bg-sidebar-accent data-[state=open]:text-sidebar-accent-foreground"
                >
                  <Avatar className="h-8 w-8">
                    <AvatarImage src={adminAvatar || undefined} />
                    <AvatarFallback className="bg-primary text-primary-foreground text-sm font-medium">
                      {initials}
                    </AvatarFallback>
                  </Avatar>
                  <div className="grid flex-1 text-left text-sm leading-tight group-data-[collapsible=icon]:hidden">
                    <span className="truncate font-semibold">{adminName}</span>
                    <span className="truncate text-xs text-muted-foreground">{adminEmail}</span>
                  </div>
                  <ChevronUp className="ml-auto h-4 w-4 text-muted-foreground group-data-[collapsible=icon]:hidden" />
                </SidebarMenuButton>
              </DropdownMenuTrigger>
              <DropdownMenuContent
                className="w-[--radix-dropdown-menu-trigger-width] min-w-56 rounded-xl"
                side="top"
                align="end"
                sideOffset={8}
              >
                <div className="flex items-center gap-3 p-3">
                  <Avatar className="h-10 w-10">
                    <AvatarFallback className="bg-primary text-primary-foreground">{initials}</AvatarFallback>
                  </Avatar>
                  <div className="flex flex-col">
                    <span className="text-sm font-medium">{adminName}</span>
                    <span className="text-xs text-muted-foreground">{adminEmail}</span>
                  </div>
                </div>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={onSettings}>
                  <Settings className="mr-2 h-4 w-4" />
                  Account Settings
                </DropdownMenuItem>
                <DropdownMenuItem>
                  <HelpCircle className="mr-2 h-4 w-4" />
                  Help & Support
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem className="text-destructive focus:text-destructive" onClick={onLogout}>
                  <LogOut className="mr-2 h-4 w-4" />
                  Sign Out
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>

      <SidebarRail />
    </Sidebar>
  )
}

