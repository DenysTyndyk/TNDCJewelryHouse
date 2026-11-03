import { Navigate } from 'react-router-dom';
import { useAuth } from '../context';
import '../styles/site.css';

function Account() {
  const { user, loading, signOut } = useAuth();

  if (loading) {
    return (
      <main>
        <section className="section auth-section">
          <p className="auth-card__subtitle">Завантаження…</p>
        </section>
      </main>
    );
  }
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  return (
    <main>
      <section className="section auth-section">
        <div className="auth-card">
          <h1>Акаунт</h1>
          <p className="auth-card__subtitle">{user.email}</p>
          <button className="btn btn--ghost" style={{ width: '100%' }} onClick={signOut}>
            Вийти
          </button>
        </div>
      </section>
    </main>
  );
}

export default Account;
