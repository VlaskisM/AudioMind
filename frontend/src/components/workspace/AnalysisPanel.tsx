import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { useWorkspaceStore, type RightPanelTab } from '@/stores/workspaceStore'
import { TranscriptView } from './TranscriptView'
import { AnalysisResult } from './AnalysisResult'

interface AnalysisPanelProps {
  recordingId: string
}

export function AnalysisPanel({ recordingId }: AnalysisPanelProps) {
  const activeTab = useWorkspaceStore((s) => s.activeTab)
  const setActiveTab = useWorkspaceStore((s) => s.setActiveTab)

  return (
    <Tabs
      value={activeTab}
      onValueChange={(v) => setActiveTab(v as RightPanelTab)}
      className="flex h-full flex-col"
    >
      <TabsList className="w-full shrink-0">
        <TabsTrigger value="transcript" className="flex-1">Транскрипция</TabsTrigger>
        <TabsTrigger value="summary" className="flex-1">Краткое</TabsTrigger>
        <TabsTrigger value="key-points" className="flex-1">Тезисы</TabsTrigger>
        <TabsTrigger value="action-items" className="flex-1">Задачи</TabsTrigger>
        <TabsTrigger value="faq" className="flex-1">FAQ</TabsTrigger>
      </TabsList>
      <div className="flex-1 overflow-hidden">
        <TabsContent value="transcript" className="m-0 h-full">
          <TranscriptView recordingId={recordingId} />
        </TabsContent>
        <TabsContent value="summary" className="m-0 h-full">
          <AnalysisResult recordingId={recordingId} type="summary" />
        </TabsContent>
        <TabsContent value="key-points" className="m-0 h-full">
          <AnalysisResult recordingId={recordingId} type="key-points" />
        </TabsContent>
        <TabsContent value="action-items" className="m-0 h-full">
          <AnalysisResult recordingId={recordingId} type="action-items" />
        </TabsContent>
        <TabsContent value="faq" className="m-0 h-full">
          <AnalysisResult recordingId={recordingId} type="faq" />
        </TabsContent>
      </div>
    </Tabs>
  )
}
