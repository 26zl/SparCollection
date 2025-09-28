import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { apiGet, listsRoute } from '../api';

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
        const data = await apiGet<ShoppingList[]>(listsRoute());
        setLists(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Klarte ikke å hente lister');
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
        <span className="page__api">Klient snakker via /api</span>
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
