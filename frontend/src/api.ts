const rawBase = (import.meta.env.VITE_API_URL as string | undefined) ?? '/api';
export const API_BASE = rawBase.endsWith('/') ? rawBase.slice(0, -1) : rawBase;

// Determine shop ID based on list ID pattern
export const getShopIdFromListId = (listId: string): string => {
  // Extract shop ID from list ID pattern
  // List IDs follow pattern: {shop_prefix}-{random}
  // Examples: abc123 -> NO-TR-001, def456 -> NO-TR-002, ghi789 -> NO-OS-001
  
  // For demo purposes, map list IDs to shop IDs
  const shopMapping: Record<string, string> = {
    'abc123': 'NO-TR-001',
    'def456': 'NO-TR-001', 
    'ghi789': 'NO-OS-001',
    'jkl012': 'NO-BG-001',
  };
  
  return shopMapping[listId] || 'NO-TR-001'; // Default fallback
};

// Get shop ID for new lists (can be based on user location, etc.)
export const getDefaultShopId = (): string => {
  return 'NO-TR-001'; // Default shop for new lists
};

export const listsRoute = () => `/lists_get?shopId=${getDefaultShopId()}`;
export const listRoute = (listId: string) =>
  `/list_get?listId=${encodeURIComponent(listId)}&shopId=${getShopIdFromListId(listId)}`;
export const itemUpdateRoute = (listId: string, itemId: string) =>
  `/item_update/${encodeURIComponent(listId)}/${encodeURIComponent(itemId)}`;
export const listCompleteRoute = (listId: string) =>
  `/list_complete/${encodeURIComponent(listId)}`;
export const listCreateRoute = () => `/list_create?shopId=${getDefaultShopId()}`;
export const listDeleteRoute = (listId: string) =>
  `/list_delete/${encodeURIComponent(listId)}?shopId=${getShopIdFromListId(listId)}`;

export const joinApi = (base: string, path: string): string =>
  `${base.replace(/\/+$/, '')}/${path.replace(/^\/+/, '')}`;

export async function apiGet<T = unknown>(path: string, init: RequestInit = {}): Promise<T> {
  const res = await fetch(joinApi(API_BASE, path), { ...init, credentials: 'include' });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<T>;
}

export async function apiPost<T = unknown>(path: string, body: unknown): Promise<T> {
  const res = await fetch(joinApi(API_BASE, path), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    credentials: 'include',
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return res.json() as Promise<T>;
}
