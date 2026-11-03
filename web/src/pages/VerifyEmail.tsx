import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import * as authApi from '../api/authApi';
import '../styles/site.css';

function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setError('Токен підтвердження відсутній у посиланні.');
      return;
    }
    authApi
      .verifyEmail(token)
      .then(() => setStatus('success'))
      .catch((err) => {
        setStatus('error');
        setError(err.message);
      });
  }, [token]);

  return (
    <main>
      <section className="section auth-section">
        <div className="auth-card">
          <h1>Підтвердження email</h1>

          {status === 'loading' && <p className="auth-card__subtitle">Перевіряємо токен…</p>}

          {status === 'success' && (
            <>
              <p className="auth-card__subtitle">Email успішно підтверджено.</p>
              <Link className="btn btn--primary" to="/login" style={{ width: '100%', display: 'flex' }}>
                Увійти
              </Link>
            </>
          )}

          {status === 'error' && (
            <>
              <p className="auth-form__error">{error}</p>
              <Link className="btn btn--ghost" to="/login" style={{ width: '100%', display: 'flex' }}>
                До сторінки входу
              </Link>
            </>
          )}
        </div>
      </section>
    </main>
  );
}

export default VerifyEmail;
