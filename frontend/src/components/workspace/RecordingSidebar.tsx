import { useNavigate, useParams } from 'react-router'
import { Plus, LogOut } from 'lucide-react'
import { useRecordings } from '@/hooks/useRecordings'
import { useAuthStore } from '@/stores/authStore'
import { useWorkspaceStore } from '@/stores/workspaceStore'
import { UploadModal } from '@/components/workspace/UploadModal'
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
              recordings.map((rec) => (
                <SidebarMenuItem key={rec.id}>
                  <SidebarMenuButton
                    isActive={String(rec.id) === id}
                    onClick={() => navigate(`/recordings/${rec.id}`)}
                  >
                    <span className="truncate">
                      {rec.original_filename ?? `Recording ${rec.id}`}
                    </span>
                    {rec.status !== 'ready' && (
                      <Badge variant="secondary" className="ml-auto text-xs">
                        {rec.status}
                      </Badge>
                    )}
                  </SidebarMenuButton>
                </SidebarMenuItem>
              ))
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
