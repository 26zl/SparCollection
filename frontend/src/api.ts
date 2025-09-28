const rawBase = (import.meta.env.VITE_API_URL as string | undefined) ?? '/api';
export const API_BASE = rawBase.endsWith('/') ? rawBase.slice(0, -1) : rawBase;
export const SHOP_ID = 'NO-TR-001';

export const listsRoute = () => `/lists_get?shopId=${SHOP_ID}`;
export const listRoute = (listId: string) =>
  `/list_get?listId=${encodeURIComponent(listId)}&shopId=${SHOP_ID}`;
export const itemUpdateRoute = (listId: string, itemId: string) =>
  `/item_update/${encodeURIComponent(listId)}/${encodeURIComponent(itemId)}`;
export const listCompleteRoute = (listId: string) =>
  `/list_complete/${encodeURIComponent(listId)}`;

export async function apiGet<T = unknown>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { ...init, credentials: 'include' });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<T>;
}

export async function apiPost<T = unknown>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    credentials: 'include',
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<T>;
}
