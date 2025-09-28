import { useState } from 'react';
import { apiPost, listCreateRoute } from '../api';

interface CreateListFormProps {
  onListCreated: () => void;
  onCancel: () => void;
}

interface ListItem {
  name: string;
  qty: number;
}

export default function CreateListForm({ onListCreated, onCancel }: CreateListFormProps) {
  const [title, setTitle] = useState('');
  const [items, setItems] = useState<ListItem[]>([{ name: '', qty: 1 }]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addItem = () => {
    setItems([...items, { name: '', qty: 1 }]);
  };

  const removeItem = (index: number) => {
    if (items.length > 1) {
      setItems(items.filter((_, i) => i !== index));
    }
  };

  const updateItem = (index: number, field: keyof ListItem, value: string | number) => {
    const newItems = [...items];
    newItems[index] = { ...newItems[index], [field]: value };
    setItems(newItems);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    // Filter out empty items
    const validItems = items
      .filter(item => item.name.trim())
      .map(item => ({
        id: `item-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        name: item.name.trim(),
        qty: item.qty,
        status: 'pending' as const,
        version: 1
      }));

    try {
      await apiPost(listCreateRoute(), {
        title: title.trim(),
        items: validItems
      });
      onListCreated();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Klarte ikke å opprette listen');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="create-list-form">
      <h2>Opprett ny liste</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="title">Liste navn:</label>
          <input
            id="title"
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="F.eks. Dagligvarer"
            required
            disabled={loading}
          />
        </div>

        <div className="form-group">
          <label>Varer:</label>
          {items.map((item, index) => (
            <div key={index} className="item-input">
              <input
                type="text"
                value={item.name}
                onChange={(e) => updateItem(index, 'name', e.target.value)}
                placeholder="Vare navn"
                disabled={loading}
              />
              <input
                type="number"
                value={item.qty}
                onChange={(e) => updateItem(index, 'qty', parseInt(e.target.value) || 1)}
                min="1"
                disabled={loading}
              />
              <button
                type="button"
                onClick={() => removeItem(index)}
                disabled={loading || items.length === 1}
                className="btn btn--danger btn--small"
              >
                Fjern
              </button>
            </div>
          ))}
          <button
            type="button"
            onClick={addItem}
            disabled={loading}
            className="btn btn--secondary btn--small"
          >
            + Legg til vare
          </button>
        </div>

        {error && <p className="text--error">{error}</p>}

        <div className="form-actions">
          <button
            type="button"
            onClick={onCancel}
            disabled={loading}
            className="btn btn--secondary"
          >
            Avbryt
          </button>
          <button
            type="submit"
            disabled={loading || !title.trim()}
            className="btn btn--primary"
          >
            {loading ? 'Oppretter...' : 'Opprett liste'}
          </button>
        </div>
      </form>
    </div>
  );
}
