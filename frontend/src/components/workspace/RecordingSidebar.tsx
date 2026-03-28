import { useNavigate, useParams } from 'react-router'
import { Plus, LogOut } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useRecordings } from '@/hooks/useRecordings'
import { useAuthStore } from '@/stores/authStore'
import { useWorkspaceStore } from '@/stores/workspaceStore'
import { UploadModal } from '@/components/workspace/UploadModal'
import { ProcessingStatus } from '@/components/ProcessingStatus'
import {
  HoverCard,
  HoverCardTrigger,
  HoverCardContent,
} from '@/components/ui/hover-card'
import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarHeader,
  SidebarGroup,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarMenuSkeleton,
} from '@/components/ui/sidebar'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'

export function RecordingSidebar() {
  const navigate = useNavigate()
  const { id } = useParams<{ id: string }>()
  const { data, isLoading } = useRecordings()
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)
  const setUploadModalOpen = useWorkspaceStore((s) => s.setUploadModalOpen)

  const recordings = data?.data ?? []

  return (
    <Sidebar>
      <SidebarHeader className="flex flex-row items-center justify-between px-4 py-2">
        <span className="text-sm font-semibold">Записи</span>
        <Button variant="ghost" size="icon" className="h-7 w-7" onClick={() => setUploadModalOpen(true)}>
          <Plus className="h-4 w-4" />
        </Button>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarMenu>
            {isLoading ? (
              <>
                <SidebarMenuSkeleton />
                <SidebarMenuSkeleton />
                <SidebarMenuSkeleton />
              </>
            ) : (
              recordings.map((rec) => {
                const isProcessing = rec.status !== 'ready' && rec.status !== 'failed'

                if (isProcessing) {
                  return (
                    <SidebarMenuItem key={rec.id}>
                      <HoverCard openDelay={300}>
                        <HoverCardTrigger asChild>
                          <SidebarMenuButton
                            isActive={String(rec.id) === id}
                            onClick={() => navigate(`/recordings/${rec.id}`)}
                          >
                            <span className={cn(
                              "truncate",
                              "bg-gradient-to-r from-foreground via-foreground/40 to-foreground bg-[length:200%_100%] bg-clip-text text-transparent animate-[shimmer_1.5s_infinite]"
                            )}>
                              {rec.original_filename ?? `Recording ${rec.id}`}
                            </span>
                          </SidebarMenuButton>
                        </HoverCardTrigger>
                        <HoverCardContent side="right" className="w-48 p-3">
                          <ProcessingStatus currentStatus={rec.status} />
                        </HoverCardContent>
                      </HoverCard>
                    </SidebarMenuItem>
                  )
                }

                return (
                  <SidebarMenuItem key={rec.id}>
                    <SidebarMenuButton
                      isActive={String(rec.id) === id}
                      onClick={() => navigate(`/recordings/${rec.id}`)}
                    >
                      <span className="truncate">
                        {rec.original_filename ?? `Recording ${rec.id}`}
                      </span>
                      {rec.status === 'failed' && (
                        <Badge variant="destructive" className="ml-auto text-xs">
                          ошибка
                        </Badge>
                      )}
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                )
              })
            )}
          </SidebarMenu>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter className="px-4 py-2">
        <div className="flex items-center justify-between">
          <span className="truncate text-xs text-muted-foreground">{user?.email}</span>
          <Button
            variant="ghost"
            size="icon"
            className="h-7 w-7"
            onClick={() => {
              logout()
              navigate('/login')
            }}
          >
            <LogOut className="h-4 w-4" />
          </Button>
        </div>
      </SidebarFooter>
      <UploadModal />
    </Sidebar>
  )
}
