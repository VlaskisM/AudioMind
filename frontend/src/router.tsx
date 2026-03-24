import { createBrowserRouter } from 'react-router'
import UploadPage from './pages/UploadPage'
import ProcessingPage from './pages/ProcessingPage'
import WorkspacePage from './pages/WorkspacePage'

export const router = createBrowserRouter([
  { path: '/', Component: UploadPage },
  { path: '/recordings/:id/processing', Component: ProcessingPage },
  { path: '/recordings/:id', Component: WorkspacePage },
])
