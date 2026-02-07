import { Routes, Route, Navigate } from 'react-router-dom'
import { AuthProvider, useAuth } from '@/lib/auth'
import { Layout } from '@/components/layout/Layout'
import { Login } from '@/pages/Login'
import { Dashboard } from '@/pages/Dashboard'
import { Dreams } from '@/pages/Dreams'
import { DreamDetail } from '@/pages/DreamDetail'
import { NewDream } from '@/pages/NewDream'
import { ChatPage } from '@/pages/Chat'
import { Graph } from '@/pages/Graph'
import { Analytics } from '@/pages/Analytics'
import { Symbols } from '@/pages/Symbols'
import { Characters } from '@/pages/Characters'
import { Spinner, ErrorBoundary } from '@/components/ui'


function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Spinner size="lg" />
      </div>
    )
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return <>{children}</>
}

function AppRoutes() {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <Spinner size="lg" />
      </div>
    )
  }

  return (
    <Routes>
      <Route
        path="/login"
        element={isAuthenticated ? <Navigate to="/" replace /> : <Login />}
      />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="dreams" element={<Dreams />} />
        <Route path="dreams/new" element={<NewDream />} />
        <Route path="dreams/:id" element={<DreamDetail />} />
        <Route path="dreams/:id/edit" element={<NewDream />} />
        <Route path="chat" element={<ChatPage />} />
        <Route path="graph" element={<Graph />} />
        <Route path="analytics" element={<Analytics />} />
        <Route path="symbols" element={<Symbols />} />
        <Route path="characters" element={<Characters />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <ErrorBoundary>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </ErrorBoundary>
  )
}