import { offlineManager } from './offline';
import { getShopId } from './auth';

const rawBase = (import.meta.env.VITE_API_URL as string | undefined) ?? '/api';
export const API_BASE = rawBase.endsWith('/') ? rawBase.slice(0, -1) : rawBase;

const getConfiguredShopId = (): string => {
  // Get shop ID from authenticated user (returns 'default-shop' if not logged in)
  return getShopId();
};

export const listsRoute = (shopId = getConfiguredShopId()) => `/lists_get?shopId=${encodeURIComponent(shopId)}`;
export const listRoute = (listId: string) =>
  `/list_get?listId=${encodeURIComponent(listId)}`;
export const itemUpdateRoute = (listId: string, itemId: string) =>
  `/item_update/${encodeURIComponent(listId)}/${encodeURIComponent(itemId)}`;
export const listCompleteRoute = (listId: string) =>
  `/list_complete/${encodeURIComponent(listId)}`;
export const listCreateRoute = (shopId = getConfiguredShopId()) => `/list_create?shopId=${encodeURIComponent(shopId)}`;
export const listDeleteRoute = (listId: string) =>
  `/list_delete/${encodeURIComponent(listId)}`;

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
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
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