// Offline support for tablets - critical requirement for case study
interface OfflineData {
  lists: any[];
  lastSync: number;
  pendingUpdates: any[];
}

const OFFLINE_STORAGE_KEY = 'spar_collection_offline_data';
const SYNC_INTERVAL = 30000; // 30 seconds

class OfflineManager {
  private isOnline: boolean = navigator.onLine;
  private syncInterval: number | null = null;

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
    this.syncInterval = setInterval(() => {
      if (this.isOnline) {
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
  storePendingUpdate(update: any) {
    const pendingUpdates = this.getPendingUpdates();
    pendingUpdates.push({
      ...update,
      timestamp: Date.now()
    });
    localStorage.setItem('spar_pending_updates', JSON.stringify(pendingUpdates));
  }

  private getPendingUpdates(): any[] {
    try {
      const data = localStorage.getItem('spar_pending_updates');
      return data ? JSON.parse(data) : [];
    } catch {
      return [];
    }
  }

  // Sync offline data when connection is restored
  private async syncOfflineData() {
    if (!this.isOnline) return;

    const pendingUpdates = this.getPendingUpdates();
    if (pendingUpdates.length === 0) return;

    console.log('Syncing', pendingUpdates.length, 'pending updates');

    try {
      // Process pending updates
      for (const update of pendingUpdates) {
        await this.processPendingUpdate(update);
      }

      // Clear pending updates after successful sync
      localStorage.removeItem('spar_pending_updates');
      console.log('Offline data synced successfully');
    } catch (error) {
      console.error('Error syncing offline data:', error);
    }
  }

  private async processPendingUpdate(update: any) {
    // This would integrate with your API calls
    // For now, just log the update
    console.log('Processing pending update:', update);
  }

  // Check if we're online
  isConnected(): boolean {
    return this.isOnline;
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
