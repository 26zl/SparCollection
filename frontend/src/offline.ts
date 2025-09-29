// Offline support for tablets - critical requirement for case study
interface OfflineData {
  lists: any[];
  lastSync: number;
  pendingUpdates: PendingUpdate[];
}

interface PendingUpdate {
  method: 'POST';
  path: string;
  body: any;
  timestamp: number;
  retries: number;
}

const OFFLINE_STORAGE_KEY = 'spar_collection_offline_data';
const PENDING_UPDATES_KEY = 'spar_pending_updates';
const SYNC_INTERVAL = 30000; // 30 seconds
const MAX_RETRIES = 3;

class OfflineManager {
  private isOnline: boolean = navigator.onLine;
  private syncInterval: number | null = null;
  private isSyncing: boolean = false;

  constructor() {
    this.setupEventListeners();
    this.startSyncInterval();
  }

  private setupEventListeners() {
    window.addEventListener('online', () => {
      this.isOnline = true;
      console.log('Connection restored - syncing offline data');
      this.syncOfflineData();
    });

    window.addEventListener('offline', () => {
      this.isOnline = false;
      console.log('Connection lost - working offline');
    });
  }

  private startSyncInterval() {
    this.syncInterval = window.setInterval(() => {
      if (this.isOnline && !this.isSyncing) {
        this.syncOfflineData();
      }
    }, SYNC_INTERVAL);
  }

  // Store data locally for offline access
  storeOfflineData(lists: any[]) {
    const offlineData: OfflineData = {
      lists,
      lastSync: Date.now(),
      pendingUpdates: this.getPendingUpdates()
    };
    
    localStorage.setItem(OFFLINE_STORAGE_KEY, JSON.stringify(offlineData));
    console.log('Data stored offline:', lists.length, 'lists');
  }

  // Get offline data
  getOfflineData(): any[] {
    try {
      const data = localStorage.getItem(OFFLINE_STORAGE_KEY);
      if (data) {
        const offlineData: OfflineData = JSON.parse(data);
        return offlineData.lists || [];
      }
    } catch (error) {
      console.error('Error reading offline data:', error);
    }
    return [];
  }

  // Store pending updates for when connection is restored
  storePendingUpdate(update: Omit<PendingUpdate, 'timestamp' | 'retries'>) {
    const pendingUpdates = this.getPendingUpdates();
    const newUpdate: PendingUpdate = {
      ...update,
      timestamp: Date.now(),
      retries: 0
    };
    pendingUpdates.push(newUpdate);
    localStorage.setItem(PENDING_UPDATES_KEY, JSON.stringify(pendingUpdates));
    console.log('Update queued for sync:', update.path);
  }

  private getPendingUpdates(): PendingUpdate[] {
    try {
      const data = localStorage.getItem(PENDING_UPDATES_KEY);
      return data ? JSON.parse(data) : [];
    } catch {
      return [];
    }
  }

  // Sync offline data when connection is restored
  private async syncOfflineData() {
    if (!this.isOnline || this.isSyncing) return;

    const pendingUpdates = this.getPendingUpdates();
    if (pendingUpdates.length === 0) return;

    this.isSyncing = true;
    console.log('Syncing', pendingUpdates.length, 'pending updates');

    const failedUpdates: PendingUpdate[] = [];

    try {
      // Process each pending update
      for (const update of pendingUpdates) {
        try {
          await this.processPendingUpdate(update);
          console.log('Successfully synced update:', update.path);
        } catch (error) {
          console.error('Failed to sync update:', update.path, error);
          
          // Increment retry count
          update.retries++;
          
          if (update.retries < MAX_RETRIES) {
            // Keep for retry
            failedUpdates.push(update);
            console.log(`Will retry (${update.retries}/${MAX_RETRIES})`, update.path);
          } else {
            // Max retries reached, discard
            console.error('Max retries exceeded, discarding update:', update.path);
          }
        }
      }

      // Save only failed updates that haven't exceeded max retries
      localStorage.setItem(PENDING_UPDATES_KEY, JSON.stringify(failedUpdates));
      
      if (failedUpdates.length === 0) {
        console.log('All offline data synced successfully!');
      } else {
        console.log(`${failedUpdates.length} update(s) failed, will retry later`);
      }
    } catch (error) {
      console.error('Error during sync process:', error);
    } finally {
      this.isSyncing = false;
    }
  }

  private async processPendingUpdate(update: PendingUpdate): Promise<void> {
    // Get API base URL
    const API_BASE = ((import.meta.env.VITE_API_URL as string | undefined) ?? '/api')
      .replace(/\/+$/, '');
    
    // Construct full URL
    const url = `${API_BASE}/${update.path.replace(/^\/+/, '')}`;
    
    // Make the actual HTTP request
    const response = await fetch(url, {
      method: update.method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(update.body),
      credentials: 'include',
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }

    // Return the response data
    return response.json();
  }

  // Check if we're online
  isConnected(): boolean {
    return this.isOnline;
  }

  // Get count of pending updates
  getPendingCount(): number {
    return this.getPendingUpdates().length;
  }

  // Get last sync time
  getLastSyncTime(): number {
    try {
      const data = localStorage.getItem(OFFLINE_STORAGE_KEY);
      if (data) {
        const offlineData: OfflineData = JSON.parse(data);
        return offlineData.lastSync;
      }
    } catch {
      // Ignore errors
    }
    return 0;
  }

  // Manually trigger sync (useful for testing or user-initiated sync)
  async triggerSync(): Promise<void> {
    if (this.isOnline) {
      await this.syncOfflineData();
    } else {
      console.warn('Cannot sync while offline');
    }
  }

  // Cleanup
  destroy() {
    if (this.syncInterval) {
      clearInterval(this.syncInterval);
    }
  }
}

// Export singleton instance
export const offlineManager = new OfflineManager();
export default OfflineManager;