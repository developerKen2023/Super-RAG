import { useState, useEffect, useCallback } from 'react'
import { supabase } from '@/lib/supabase'
import { authApi } from '@/lib/api'
import type { User } from '@supabase/supabase-js'

interface AuthState {
  user: User | null
  loading: boolean
  error: string | null
}

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    user: null,
    loading: true,
    error: null,
  })

  useEffect(() => {
    const checkSession = async () => {
      try {
        const { data: { session } } = await supabase.auth.getSession()
        setState({ user: session?.user ?? null, loading: false, error: null })
      } catch (err) {
        setState({ user: null, loading: false, error: 'Failed to check session' })
      }
    }

    checkSession()

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setState({ user: session?.user ?? null, loading: false, error: null })
    })

    return () => subscription.unsubscribe()
  }, [])

  const login = useCallback(async (email: string, password: string) => {
    setState(s => ({ ...s, loading: true, error: null }))
    try {
      const response = await authApi.login(email, password)
      await supabase.auth.setSession({
        access_token: response.access_token,
        refresh_token: response.refresh_token,
      })
      setState({ user: response.user as unknown as User, loading: false, error: null })
      return response
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Login failed'
      setState(s => ({ ...s, loading: false, error }))
      throw err
    }
  }, [])

  const signup = useCallback(async (email: string, password: string, fullName?: string) => {
    setState(s => ({ ...s, loading: true, error: null }))
    try {
      const response = await authApi.signup(email, password, fullName)
      await supabase.auth.setSession({
        access_token: response.access_token,
        refresh_token: response.refresh_token,
      })
      setState({ user: response.user as unknown as User, loading: false, error: null })
      return response
    } catch (err) {
      const error = err instanceof Error ? err.message : 'Signup failed'
      setState(s => ({ ...s, loading: false, error }))
      throw err
    }
  }, [])

  const logout = useCallback(async () => {
    const { data: { session } } = await supabase.auth.getSession()
    if (session?.access_token) {
      try {
        await authApi.logout(session.access_token)
      } catch {
        // Ignore logout errors
      }
    }
    await supabase.auth.signOut()
    setState({ user: null, loading: false, error: null })
  }, [])

  return {
    ...state,
    login,
    signup,
    logout,
  }
}
