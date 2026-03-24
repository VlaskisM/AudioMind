import { useParams } from 'react-router'

export default function ProcessingPage() {
  const { id } = useParams<{ id: string }>()
  return (
    <div className="flex h-screen items-center justify-center flex-col gap-4">
      <h1 className="text-2xl font-bold">Processing</h1>
      <p className="text-muted-foreground">Recording {id} is being processed...</p>
    </div>
  )
}
