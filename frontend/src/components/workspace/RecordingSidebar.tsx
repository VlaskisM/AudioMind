import { useNavigate, useParams, Link } from 'react-router'
import { Plus } from 'lucide-react'
import { useRecordings } from '@/hooks/useRecordings'
import {
  Sidebar,
  SidebarContent,
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

  const recordings = data?.data ?? []

  return (
    <Sidebar>
      <SidebarHeader className="flex flex-row items-center justify-between px-4 py-2">
        <span className="text-sm font-semibold">Записи</span>
        <Button variant="ghost" size="icon" className="h-7 w-7" asChild>
          <Link to="/">
            <Plus className="h-4 w-4" />
          </Link>
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
    </Sidebar>
  )
}
