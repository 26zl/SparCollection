import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiGet, listsRoute } from '../api';
import { offlineManager } from '../offline';
import CreateListForm from '../components/CreateListForm';

interface ShoppingList {
  id: string;
  title: string;
  status: string;
}

export default function HomePage() {
  const [lists, setLists] = useState<ShoppingList[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        // Try online first
        if (offlineManager.isConnected()) {
          const data = await apiGet<ShoppingList[]>(listsRoute());
          setLists(data);
          offlineManager.storeOfflineData(data);
        } else {
          // Use offline data
          const offlineData = offlineManager.getOfflineData();
          setLists(offlineData);
          setError('Offline mode - showing cached data');
        }
      } catch (err) {
        // Fallback to offline data
        const offlineData = offlineManager.getOfflineData();
        if (offlineData.length > 0) {
          setLists(offlineData);
          setError('Offline mode - showing cached data');
        } else {
          setError(err instanceof Error ? err.message : 'Failed to fetch lists');
        }
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, []);

  const handleListCreated = () => {
    setShowCreateForm(false);
    // Reload lists
    const load = async () => {
      setLoading(true);
      setError(null);
      try {
        if (offlineManager.isConnected()) {
          const data = await apiGet<ShoppingList[]>(listsRoute());
          setLists(data);
          offlineManager.storeOfflineData(data);
        } else {
          const offlineData = offlineManager.getOfflineData();
          setLists(offlineData);
          setError('Offline mode - showing cached data');
        }
      } catch (err) {
        const offlineData = offlineManager.getOfflineData();
        if (offlineData.length > 0) {
          setLists(offlineData);
          setError('Offline mode - showing cached data');
        } else {
          setError(err instanceof Error ? err.message : 'Failed to fetch lists');
        }
      } finally {
        setLoading(false);
      }
    };
    void load();
  };

  return (
    <section className="page">
      <div className="page__intro">
        <h1>Spar Collection</h1>
        <p>Select a list to view details and update collection status.</p>
        
        <div className="page__actions">
          <button
            onClick={() => setShowCreateForm(true)}
            className="btn btn--primary"
          >
            + Create new list
          </button>
        </div>
      </div>

      {loading && <p>Loading lists…</p>}
      {error && <p className="text--error">{error}</p>}

      {showCreateForm && (
        <CreateListForm
          onListCreated={handleListCreated}
          onCancel={() => setShowCreateForm(false)}
        />
      )}

      {!loading && !error && !showCreateForm && (
        <ul className="list__items">
          {lists.map((list) => (
            <li key={list.id} className="item-card">
              <div className="item-card__header">
                <div>
                  <h2>{list.title}</h2>
                  <p className="item-card__meta">List ID: {list.id}</p>
                </div>
                <span className="item-card__status">Status: {list.status}</span>
              </div>
              <div className="item-card__actions">
                <Link className="btn btn--primary" to={`/lists/${list.id}`}>
                  Open list
                </Link>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
