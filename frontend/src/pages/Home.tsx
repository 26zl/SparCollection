import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiGet, listsRoute } from '../api';
import { offlineManager } from '../offline';

interface ShoppingList {
  id: string;
  title: string;
  status: string;
}

export default function HomePage() {
  const [lists, setLists] = useState<ShoppingList[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

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
          setError(err instanceof Error ? err.message : 'Klarte ikke å hente lister');
        }
      } finally {
        setLoading(false);
      }
    };
    void load();
  }, []);

  return (
    <section className="page">
      <div className="page__intro">
        <h1>Spar Collection</h1>
        <p>Velg en liste for å se detaljer og oppdatere plukkestatus.</p>
        <div className="page__status">
          <span className="page__api">Klient snakker via /api</span>
          <span className={`status-indicator ${offlineManager.isConnected() ? 'online' : 'offline'}`}>
            {offlineManager.isConnected() ? '🟢 Online' : '🔴 Offline'}
          </span>
        </div>
      </div>

      {loading && <p>Laster lister…</p>}
      {error && <p className="text--error">{error}</p>}

      {!loading && !error && (
        <ul className="list__items">
          {lists.map((list) => (
            <li key={list.id} className="item-card">
              <div className="item-card__header">
                <div>
                  <h2>{list.title}</h2>
                  <p className="item-card__meta">Liste-ID: {list.id}</p>
                </div>
                <span className="item-card__status">Status: {list.status}</span>
              </div>
              <div className="item-card__actions">
                <Link className="btn btn--primary" to={`/lists/${list.id}`}>
                  Åpne liste
                </Link>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
