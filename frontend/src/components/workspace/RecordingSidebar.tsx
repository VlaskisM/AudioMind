import { useState } from 'react'
import { useNavigate, useParams } from 'react-router'
import { useQueryClient } from '@tanstack/react-query'
import { Plus, LogOut, Trash2 } from 'lucide-react'
import { cn } from '@/lib/utils'
import { useRecordings } from '@/hooks/useRecordings'
import { deleteRecording } from '@/api/ingress'
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
  const queryClient = useQueryClient()
  const [deletingId, setDeletingId] = useState<number | null>(null)

  const recordings = data?.data ?? []

  async function handleDelete(e: React.MouseEvent, recordingId: number) {
    e.stopPropagation()
    if (deletingId) return
    setDeletingId(recordingId)
    try {
      await deleteRecording(recordingId)
      queryClient.invalidateQueries({ queryKey: ['recordings'] })
      if (String(recordingId) === id) {
        navigate('/recordings')
      }
    } finally {
      setDeletingId(null)
    }
  }

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
                    <SidebarMenuItem key={rec.id} className="group/item">
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
                      <Button
                        variant="ghost"
                        size="icon"
                        className="absolute right-1 top-1/2 h-6 w-6 -translate-y-1/2 opacity-0 transition-opacity group-hover/item:opacity-100"
                        disabled={deletingId === rec.id}
                        onClick={(e) => handleDelete(e, rec.id)}
                      >
                        <Trash2 className="h-3.5 w-3.5 text-muted-foreground hover:text-destructive" />
                      </Button>
                    </SidebarMenuItem>
                  )
                }

                return (
                  <SidebarMenuItem key={rec.id} className="group/item">
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
                    <Button
                      variant="ghost"
                      size="icon"
                      className="absolute right-1 top-1/2 h-6 w-6 -translate-y-1/2 opacity-0 transition-opacity group-hover/item:opacity-100"
                      disabled={deletingId === rec.id}
                      onClick={(e) => handleDelete(e, rec.id)}
                    >
                      <Trash2 className="h-3.5 w-3.5 text-muted-foreground hover:text-destructive" />
                    </Button>
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
