import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import * as authApi from '../api/authApi';
import '../styles/site.css';

function ResetPassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!token) {
      setError('Токен відсутній у посиланні.');
      return;
    }
    setSubmitting(true);
    setError(null);
    try {
      await authApi.resetPassword(token, password);
      navigate('/login');
    } catch (err: any) {
      setError(err.message);
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <main>
      <section className="section auth-section">
        <div className="auth-card">
          <h1>Новий пароль</h1>
          <p className="auth-card__subtitle">Введіть новий пароль для свого акаунта</p>

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="field">
              <label htmlFor="password">Новий пароль</label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                placeholder="Мінімум 8 символів"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={8}
              />
            </div>

            {error && <p className="auth-form__error">{error}</p>}

            <button className="btn btn--primary" type="submit" disabled={submitting}>
              {submitting ? 'Зберігаємо…' : 'Зберегти пароль'}
            </button>
          </form>

          <p className="auth-card__footer">
            <Link to="/login">До сторінки входу</Link>
          </p>
        </div>
      </section>
    </main>
  );
}

export default ResetPassword;
