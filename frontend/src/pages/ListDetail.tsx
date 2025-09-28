import { useEffect, useMemo, useState } from 'react';
import { useParams } from 'react-router-dom';
import { apiGet, apiPost, itemUpdateRoute, listCompleteRoute, listRoute } from '../api';
import ItemCard from '../components/ItemCard';

interface ShoppingListItem {
  id: string;
  name: string;
  qty?: number;
  status: 'pending' | 'collected' | 'unavailable';
  version: number;
}

interface ShoppingList {
  id: string;
  title: string;
  status: string;
  items: ShoppingListItem[];
  completed_at?: string;
  completed_by?: string;
}

interface Summary {
  pending: number;
  collected: number;
  unavailable: number;
}

const initialSummary: Summary = { pending: 0, collected: 0, unavailable: 0 };

type CompletionInfo = {
  queued: boolean;
  listId: string;
};

export default function ListDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [list, setList] = useState<ShoppingList | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [completing, setCompleting] = useState(false);
  const [activeItem, setActiveItem] = useState<string | null>(null);
  const [completionInfo, setCompletionInfo] = useState<CompletionInfo | null>(null);

  const loadList = async (listId: string) => {
    setLoading(true);
    setError(null);
    setMessage(null);
    try {
      const data = await apiGet<ShoppingList>(listRoute(listId));
      setList(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Klarte ikke å hente listen');
      setList(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (id) {
      void loadList(id);
    }
  }, [id]);

  const summary = useMemo(() => {
    if (!list) {
      return initialSummary;
    }
    return list.items.reduce(
      (acc, item) => {
        acc[item.status] += 1;
        return acc;
      },
      { ...initialSummary },
    );
  }, [list]);

  const handleUpdate = async (itemId: string, newStatus: Exclude<ShoppingListItem['status'], 'pending'>) => {
    if (!id) {
      return;
    }
    setActiveItem(itemId);
    setMessage(null);
    setError(null);
    try {
      await apiPost(itemUpdateRoute(id, itemId), { status: newStatus });
      await loadList(id);
      setMessage('Vare oppdatert.');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Klarte ikke å oppdatere varen');
    } finally {
      setActiveItem(null);
    }
  };

  const handleComplete = async () => {
    if (!id) {
      return;
    }
    setCompleting(true);
    setMessage(null);
    setError(null);
    try {
      const result = await apiPost<CompletionInfo>(listCompleteRoute(id), {});
      setCompletionInfo(result);
      await loadList(id);
      setMessage('Fullføring registrert.');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Klarte ikke å fullføre listen');
      setCompletionInfo(null);
    } finally {
      setCompleting(false);
    }
  };

  return (
    <section className="page">
      <header className="page__intro">
        <h1>Liste {id ?? 'ukjent'}</h1>
        <p>Marker varer som plukket eller utilgjengelig underveis.</p>
        <div className="page__summary">
          <span>Venter: {summary.pending}</span>
          <span>Plukket: {summary.collected}</span>
          <span>Utilgjengelig: {summary.unavailable}</span>
        </div>
      </header>

      {loading && <p>Laster liste…</p>}
      {error && <p className="text--error">{error}</p>}
      {message && <p className="text--info">{message}</p>}

      {list && (
        <div className="list">
          <ul className="list__items">
            {list.items.map((item) => (
              <ItemCard
                key={item.id}
                name={item.name}
                quantity={item.qty}
                status={item.status}
                itemId={item.id}
                onCollected={() => handleUpdate(item.id, 'collected')}
                onUnavailable={() => handleUpdate(item.id, 'unavailable')}
                disabled={activeItem === item.id}
              />
            ))}
          </ul>

          <div className="list__complete">
            <button type="button" onClick={handleComplete} disabled={completing} className="btn btn--primary">
              {completing ? 'Fullfører…' : 'Fullfør liste'}
            </button>
          </div>

          {!!completionInfo && <pre className="code-block">{JSON.stringify(completionInfo, null, 2)}</pre>}
        </div>
      )}
    </section>
  );
}
