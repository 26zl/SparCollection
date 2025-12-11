import { useNavigate } from 'react-router-dom';
import { getCurrentUser, logout } from '../auth';

export default function Header() {
  const navigate = useNavigate();
  const user = getCurrentUser();

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  return (
    <header className="app-header">
      <div className="app-header__content">
        <div>
          <h1>Spar Collection</h1>
          <p>Manage and complete your shopping lists</p>
        </div>
        {user && (
          <div className="app-header__user">
            <span className="user-info">
              {user.username} ({user.shopId})
            </span>
            <button onClick={handleLogout} className="btn btn--small btn--secondary">
              Logout
            </button>
          </div>
        )}
      </div>
    </header>
  );
}
