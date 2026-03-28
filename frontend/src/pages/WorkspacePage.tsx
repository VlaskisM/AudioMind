import { useParams } from 'react-router'
import { useRecordings } from '@/hooks/useRecordings'
import {
  SidebarProvider,
  SidebarInset,
  SidebarTrigger,
} from '@/components/ui/sidebar'
import {
  ResizablePanelGroup,
  ResizablePanel,
  ResizableHandle,
} from '@/components/ui/resizable'
import { Separator } from '@/components/ui/separator'
import { RecordingSidebar } from '@/components/workspace/RecordingSidebar'
import { ChatPanel } from '@/components/workspace/ChatPanel'
import { AnalysisPanel } from '@/components/workspace/AnalysisPanel'
import { Upload } from 'lucide-react'

export default function WorkspacePage() {
  const { id } = useParams<{ id: string }>()
  const { data } = useRecordings()

  const recordings = data?.data ?? []
  const current = recordings.find((r) => String(r.id) === id)
  const title = id
    ? (current?.original_filename ?? `Recording ${id}`)
    : 'Speechmate'

  return (
    <SidebarProvider>
      <RecordingSidebar />
      <SidebarInset className="flex h-screen flex-col">
        <header className="flex items-center gap-2 border-b p-2">
          <SidebarTrigger />
          <Separator orientation="vertical" className="h-4" />
          <h1 className="text-sm font-medium">{title}</h1>
        </header>
        <div className="flex-1 overflow-hidden">
          {id ? (
            <ResizablePanelGroup orientation="horizontal">
              <ResizablePanel defaultSize={50} minSize={30}>
                <ChatPanel recordingId={id} />
              </ResizablePanel>
              <ResizableHandle withHandle />
              <ResizablePanel
                defaultSize={50}
                minSize={15}
                collapsible
                collapsedSize={0}
              >
                <AnalysisPanel recordingId={id} />
              </ResizablePanel>
            </ResizablePanelGroup>
          ) : recordings.length === 0 ? (
            <div className="flex h-full flex-col items-center justify-center gap-4 text-muted-foreground">
              <Upload className="h-12 w-12" />
              <p className="text-lg font-medium">Добавьте первую запись</p>
              <p className="text-sm">Нажмите &quot;+&quot; в сайдбаре, чтобы загрузить аудиофайл</p>
            </div>
          ) : (
            <div className="flex h-full flex-col items-center justify-center gap-4 text-muted-foreground">
              <p className="text-lg font-medium">Выберите запись из сайдбара</p>
              <p className="text-sm">Или нажмите &quot;+&quot; чтобы загрузить новый файл</p>
            </div>
          )}
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}
