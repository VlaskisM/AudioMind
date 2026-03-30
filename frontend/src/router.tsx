import { createBrowserRouter, Navigate, useParams } from 'react-router'
import WorkspacePage from './pages/WorkspacePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import { ProtectedRoute } from './components/ProtectedRoute'

function ProcessingRedirect() {
  const { id } = useParams<{ id: string }>()
  return <Navigate to={`/recordings/${id}`} replace />
}

export const router = createBrowserRouter([
  { path: '/login', Component: LoginPage },
  { path: '/register', Component: RegisterPage },
  {
    path: '/',
    element: <ProtectedRoute><WorkspacePage /></ProtectedRoute>,
  },
  {
    path: '/recordings/:id/processing',
    element: <ProtectedRoute><ProcessingRedirect /></ProtectedRoute>,
  },
  {
    path: '/recordings/:id',
    element: <ProtectedRoute><WorkspacePage /></ProtectedRoute>,
  },
])
