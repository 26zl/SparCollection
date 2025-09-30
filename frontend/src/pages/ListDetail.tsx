import { useCallback, useEffect, useMemo, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
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
  const navigate = useNavigate();
  const [list, setList] = useState<ShoppingList | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [completing, setCompleting] = useState(false);
  const [activeItem, setActiveItem] = useState<string | null>(null);
  const [completionInfo, setCompletionInfo] = useState<CompletionInfo | null>(null);

  const loadList = useCallback(async (listId: string) => {
    setLoading(true);
    setError(null);
    setMessage(null);
    try {
      const data = await apiGet<ShoppingList>(listRoute(listId));
      setList(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch list');
      setList(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (id) {
      void loadList(id);
    }
  }, [id, loadList]);

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

  const handleUpdate = useCallback(async (itemId: string, newStatus: Exclude<ShoppingListItem['status'], 'pending'>) => {
    if (!id || !list) {
      return;
    }
    setActiveItem(itemId);
    setMessage(null);
    setError(null);
    
    // Optimistic update - update UI immediately
    setList(prevList => {
      if (!prevList) return prevList;
      return {
        ...prevList,
        items: prevList.items.map(item => 
          item.id === itemId 
            ? { ...item, status: newStatus, version: item.version + 1 }
            : item
        )
      };
    });
    
    try {
      await apiPost(itemUpdateRoute(id, itemId), { status: newStatus });
      setMessage('Item updated.');
    } catch (err) {
      // Revert optimistic update on error
      setList(prevList => {
        if (!prevList) return prevList;
        return {
          ...prevList,
          items: prevList.items.map(item => 
            item.id === itemId 
              ? { ...item, status: 'pending', version: item.version - 1 }
              : item
          )
        };
      });
      setError(err instanceof Error ? err.message : 'Failed to update item');
    } finally {
      setActiveItem(null);
    }
  }, [id, list]);

  const handleComplete = useCallback(async () => {
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
      setMessage('Completion registered.');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to complete list');
      setCompletionInfo(null);
    } finally {
      setCompleting(false);
    }
  }, [id, loadList]);

  return (
    <section className="page">
      <header className="page__intro">
        <div className="page__header">
          <button 
            type="button" 
            onClick={() => navigate('/')} 
            className="btn btn--secondary btn--back"
            title="Back to main page"
          >
            ← Back
          </button>
          <h1>List {id ?? 'unknown'}</h1>
        </div>
        <p>Mark items as collected or unavailable as you go.</p>
        <div className="page__summary">
          <span>Pending: {summary.pending}</span>
          <span>Collected: {summary.collected}</span>
          <span>Unavailable: {summary.unavailable}</span>
        </div>
      </header>

      {loading && <p>Loading list…</p>}
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
              {completing ? 'Completing…' : 'Complete list'}
            </button>
          </div>

          {!!completionInfo && <pre className="code-block">{JSON.stringify(completionInfo, null, 2)}</pre>}
        </div>
      )}
    </section>
  );
}
