import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { LoginForm } from '@/components/auth/LoginForm';
import { useAuth } from '@/hooks/useAuth';

// Mock the useAuth hook
vi.mock('@/hooks/useAuth', () => ({
  useAuth: vi.fn(),
}));

// Mock react-router-dom
vi.mock('react-router-dom', () => ({
  useNavigate: vi.fn(),
}));

describe('LoginForm', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders login form with email and password fields', () => {
    (useAuth as any).mockReturnValue({
      login: vi.fn(),
      loading: false,
      error: null,
    });

    render(<LoginForm />);

    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  it('shows error message when error is present', () => {
    (useAuth as any).mockReturnValue({
      login: vi.fn(),
      loading: false,
      error: 'Invalid credentials',
    });

    render(<LoginForm />);

    expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
  });

  it('disables button when loading', () => {
    (useAuth as any).mockReturnValue({
      login: vi.fn(),
      loading: true,
      error: null,
    });

    render(<LoginForm />);

    expect(screen.getByRole('button', { name: /logging in/i })).toBeDisabled();
  });

  it('calls login with form values on submit', async () => {
    const mockLogin = vi.fn().mockResolvedValue({});
    (useAuth as any).mockReturnValue({
      login: mockLogin,
      loading: false,
      error: null,
    });

    render(<LoginForm />);

    const emailInput = screen.getByLabelText(/email/i);
    const passwordInput = screen.getByLabelText(/password/i);

    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });

    fireEvent.click(screen.getByRole('button', { name: /login/i }));

    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('test@example.com', 'password123');
    });
  });
});
