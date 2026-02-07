import React, { createContext, useContext, useState, useEffect, useCallback } from 'react'
import { authApi } from './api'

interface User {
  id: number
  email: string
  name: string
}

interface AuthContextType {
  user: User | null
  token: string | null
  isLoading: boolean
  isAuthenticated: boolean
  isDemoMode: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, name: string) => Promise<void>
  logout: () => void
  switchToDemo: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('token'))
  const [isLoading, setIsLoading] = useState(true)
  const [isDemoMode, setIsDemoMode] = useState(() => localStorage.getItem('demo_mode') === 'true')

  const fetchUser = useCallback(async () => {
    if (!token) {
      setIsLoading(false)
      return
    }

    try {
      const response = await authApi.me()
      setUser(response.data)
    } catch {
      localStorage.removeItem('token')
      localStorage.removeItem('demo_mode')
      setToken(null)
      setUser(null)
      setIsDemoMode(false)
    } finally {
      setIsLoading(false)
    }
  }, [token])

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    const isDemoRequested = params.get('demo') === 'true'

    const initializeAuth = async () => {
      // If demo is requested and no existing token, create demo session
      if (isDemoRequested && !token) {
        try {
          const response = await authApi.demo()
          const { access_token, user: demoUser } = response.data
          localStorage.setItem('token', access_token)
          localStorage.setItem('demo_mode', 'true')
          setToken(access_token)
          setUser(demoUser)
          setIsDemoMode(true)

          // Remove demo parameter from URL
          window.history.replaceState({}, '', window.location.pathname)
        } catch (error) {
          console.error('Failed to create demo session:', error)
        } finally {
          setIsLoading(false)
        }
      } else {
        // Normal auth flow
        await fetchUser()
      }
    }

    initializeAuth()
  }, [token, fetchUser])

  const login = async (email: string, password: string) => {
    // Clear demo mode if switching to real account
    if (isDemoMode) {
      localStorage.removeItem('demo_mode')
      setIsDemoMode(false)
    }

    const response = await authApi.login(email, password)
    const { access_token } = response.data
    localStorage.setItem('token', access_token)
    setToken(access_token)

    // Fetch user data
    const userResponse = await authApi.me()
    setUser(userResponse.data)
  }

  const register = async (email: string, password: string, name: string) => {
    // Clear demo mode if switching to real account
    if (isDemoMode) {
      localStorage.removeItem('demo_mode')
      setIsDemoMode(false)
    }

    await authApi.register(email, password, name)
    // Auto-login after registration
    await login(email, password)
  }

  const logout = () => {
    localStorage.removeItem('token')
    localStorage.removeItem('demo_mode')
    setToken(null)
    setUser(null)
    setIsDemoMode(false)
  }

  const switchToDemo = async () => {
    // Clear any existing auth first
    logout()

    try {
      const response = await authApi.demo()
      const { access_token, user: demoUser } = response.data
      localStorage.setItem('token', access_token)
      localStorage.setItem('demo_mode', 'true')
      setToken(access_token)
      setUser(demoUser)
      setIsDemoMode(true)
    } catch (error) {
      console.error('Failed to switch to demo mode:', error)
      throw error
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        isAuthenticated: !!user,
        isDemoMode,
        login,
        register,
        logout,
        switchToDemo,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
