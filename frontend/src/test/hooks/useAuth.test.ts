import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useAuth } from '@/hooks/useAuth';

// Mock the dependencies
vi.mock('@/lib/supabase', () => ({
  supabase: {
    auth: {
      getSession: vi.fn(),
      onAuthStateChange: vi.fn(() => ({
        data: { subscription: { unsubscribe: vi.fn() } }
      })),
      setSession: vi.fn(),
      signOut: vi.fn(),
    },
  },
}));

vi.mock('@/lib/api', () => ({
  authApi: {
    login: vi.fn(),
    signup: vi.fn(),
    logout: vi.fn(),
  },
}));

describe('useAuth', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('initializes with loading true', async () => {
    const { supabase } = await import('@/lib/supabase');
    (supabase.auth.getSession as any).mockResolvedValue({
      data: { session: null }
    });

    const { result } = renderHook(() => useAuth());

    expect(result.current.loading).toBe(true);
  });

  it('sets user to null when no session', async () => {
    const { supabase } = await import('@/lib/supabase');
    (supabase.auth.getSession as any).mockResolvedValue({
      data: { session: null }
    });

    const { result } = renderHook(() => useAuth());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.user).toBeNull();
  });

  it('login updates user state on success', async () => {
    const { supabase } = await import('@/lib/supabase');
    const { authApi } = await import('@/lib/api');

    (supabase.auth.getSession as any).mockResolvedValue({
      data: { session: null }
    });

    const mockUser = { id: 'user-1', email: 'test@example.com' };
    const mockResponse = {
      access_token: 'token-123',
      refresh_token: 'refresh-123',
      user: mockUser,
    };

    (authApi.login as any).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useAuth());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    await act(async () => {
      await result.current.login('test@example.com', 'password');
    });

    expect(result.current.user).not.toBeNull();
  });

  it('logout clears user state', async () => {
    const { supabase } = await import('@/lib/supabase');
    const { authApi } = await import('@/lib/api');

    // First login
    (supabase.auth.getSession as any).mockResolvedValue({
      data: { session: { user: { id: 'user-1' }, access_token: 'token' } }
    });

    const mockResponse = {
      access_token: 'token-123',
      refresh_token: 'refresh-123',
      user: { id: 'user-1', email: 'test@example.com' },
    };

    (authApi.login as any).mockResolvedValue(mockResponse);
    (authApi.logout as any).mockResolvedValue(undefined);
    (supabase.auth.signOut as any).mockResolvedValue({});

    const { result } = renderHook(() => useAuth());

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    await act(async () => {
      await result.current.logout();
    });

    expect(result.current.user).toBeNull();
  });
});
