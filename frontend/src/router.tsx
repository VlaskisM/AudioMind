import { createBrowserRouter } from 'react-router'
import UploadPage from './pages/UploadPage'
import ProcessingPage from './pages/ProcessingPage'
import WorkspacePage from './pages/WorkspacePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import { ProtectedRoute } from './components/ProtectedRoute'

export const router = createBrowserRouter([
  { path: '/login', Component: LoginPage },
  { path: '/register', Component: RegisterPage },
  {
    path: '/',
    element: <ProtectedRoute><UploadPage /></ProtectedRoute>,
  },
  {
    path: '/recordings/:id/processing',
    element: <ProtectedRoute><ProcessingPage /></ProtectedRoute>,
  },
  {
    path: '/recordings/:id',
    element: <ProtectedRoute><WorkspacePage /></ProtectedRoute>,
  },
])
