import { offlineManager } from './offline';

const rawBase = (import.meta.env.VITE_API_URL as string | undefined) ?? '/api';
export const API_BASE = rawBase.endsWith('/') ? rawBase.slice(0, -1) : rawBase;

export const getShopIdFromListId = (listId: string): string => {
  const shopMapping: Record<string, string> = {
    'abc123': 'NO-TR-001',
    'def456': 'NO-TR-001', 
    'ghi789': 'NO-OS-001',
    'jkl012': 'NO-BG-001',
  };
  return shopMapping[listId] || 'NO-TR-001';
};

export const getDefaultShopId = (): string => {
  return 'NO-TR-001';
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
  try {
    const res = await fetch(joinApi(API_BASE, path), { ...init, credentials: 'include' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json() as T;
    
    // Cache lists data for offline use
    if (path.includes('lists_get') && Array.isArray(data)) {
      offlineManager.storeOfflineData(data);
    }
    
    return data;
  } catch (error) {
    // For GET requests, try to return cached data if available
    if (path.includes('lists_get')) {
      const cachedData = offlineManager.getOfflineData();
      if (cachedData.length > 0) {
        console.log('Request failed - using cached data:', path);
        return cachedData as T;
      }
    }
    
    // If no cached data or not a lists request, throw the error
    console.error('Request failed with no cached data:', path, error);
    throw error;
  }
}

export async function apiPost<T = unknown>(path: string, body: unknown): Promise<T> {
  try {
    const res = await fetch(joinApi(API_BASE, path), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
      credentials: 'include',
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json() as Promise<T>;
  } catch (error) {
    // Queue ALL failed POST requests (offline OR backend errors)
    console.log('POST request failed - queuing update:', path);
    offlineManager.storePendingUpdate({
      method: 'POST',
      path,
      body
    });
    
    // Return optimistic success
    return { 
      success: true, 
      queued: true,
      message: 'Update queued - will sync when available'
    } as T;
  }
}