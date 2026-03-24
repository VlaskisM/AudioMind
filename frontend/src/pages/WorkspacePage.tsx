import { useParams } from 'react-router'

export default function WorkspacePage() {
  const { id } = useParams<{ id: string }>()
  return (
    <div className="flex h-screen items-center justify-center flex-col gap-4">
      <h1 className="text-2xl font-bold">Workspace</h1>
      <p className="text-muted-foreground">Recording {id}</p>
    </div>
  )
}
