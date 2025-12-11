interface User {
  id: string;
  username: string;
  shopId: string;
  role: 'employee' | 'manager' | 'admin';
}

const AUTH_KEY = import.meta.env.VITE_AUTH_KEY || 'spar_auth_user';
const API_BASE = ((import.meta.env.VITE_API_URL as string | undefined) ?? '/api').replace(/\/+$/, '');

export async function login(username: string, password: string): Promise<User | null> {
  try {
    const response = await fetch(`${API_BASE}/auth_login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, password }),
    });

    if (!response.ok) {
      const error = await response.json();
      console.error('Login failed:', error.error);
      return null;
    }

    const user: User = await response.json();
    localStorage.setItem(AUTH_KEY, JSON.stringify(user));
    return user;
  } catch (error) {
    console.error('Login error:', error);
    return null;
  }
}

export function logout(): void {
  localStorage.removeItem(AUTH_KEY);
}

export function getCurrentUser(): User | null {
  const stored = localStorage.getItem(AUTH_KEY);
  if (!stored) return null;

  try {
    return JSON.parse(stored) as User;
  } catch {
    return null;
  }
}

export function isAuthenticated(): boolean {
  return getCurrentUser() !== null;
}

export function getShopId(): string {
  const user = getCurrentUser();
  return user?.shopId || 'default-shop';
}
