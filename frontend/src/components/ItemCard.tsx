type ItemStatus = 'pending' | 'collected' | 'unavailable';

interface ItemCardProps {
  name: string;
  quantity?: number;
  status: ItemStatus;
  itemId: string;
  onCollected(): void;
  onUnavailable(): void;
  disabled?: boolean;
}

const statusLabel: Record<ItemStatus, string> = {
  pending: 'venter',
  collected: 'plukket',
  unavailable: 'utilgjengelig',
};

export default function ItemCard({
  name,
  quantity = 1,
  status,
  itemId,
  onCollected,
  onUnavailable,
  disabled = false,
}: ItemCardProps) {
  return (
    <li className="item-card">
      <div className="item-card__header">
        <div>
          <h2>{name}</h2>
          <p className="item-card__meta">Vare-ID: {itemId}</p>
        </div>
        <span className="item-card__quantity">Antall: {quantity}</span>
        <span className="item-card__status">Status: {statusLabel[status]}</span>
      </div>
      <div className="item-card__actions">
        <button type="button" onClick={onCollected} disabled={disabled} className="btn btn--success">
          Plukket
        </button>
        <button type="button" onClick={onUnavailable} disabled={disabled} className="btn btn--warning">
          Utilgjengelig
        </button>
      </div>
    </li>
  );
}
