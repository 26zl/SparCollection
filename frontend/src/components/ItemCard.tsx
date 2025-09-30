import { memo } from 'react';

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
  pending: 'pending',
  collected: 'collected',
  unavailable: 'unavailable',
};

const ItemCard = memo(function ItemCard({
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
          <p className="item-card__meta">Item ID: {itemId}</p>
        </div>
        <span className="item-card__quantity">Quantity: {quantity}</span>
        <span className="item-card__status">Status: {statusLabel[status]}</span>
      </div>
      <div className="item-card__actions">
        <button 
          type="button" 
          onClick={onCollected} 
          disabled={disabled || status === 'collected'} 
          className={`btn btn--success ${status === 'collected' ? 'btn--disabled' : ''}`}
        >
          {disabled ? 'Updating...' : 'Collected'}
        </button>
        <button 
          type="button" 
          onClick={onUnavailable} 
          disabled={disabled || status === 'unavailable'} 
          className={`btn btn--warning ${status === 'unavailable' ? 'btn--disabled' : ''}`}
        >
          {disabled ? 'Updating...' : 'Unavailable'}
        </button>
      </div>
    </li>
  );
});

export default ItemCard;
