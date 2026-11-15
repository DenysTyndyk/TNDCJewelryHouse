import { useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import * as authApi from '../api/authApi';
import { useLanguage } from '../context/languageContext';
import '../styles/site.css';

function ResetPassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const navigate = useNavigate();
  const { t } = useLanguage();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!token) {
      setError(t('auth.resetPassword.missingToken'));
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
          <h1>{t('auth.resetPassword.title')}</h1>
          <p className="auth-card__subtitle">{t('auth.resetPassword.subtitle')}</p>

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="field">
              <label htmlFor="password">{t('auth.resetPassword.newPassword')}</label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                placeholder={t('auth.resetPassword.passwordPlaceholder')}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={8}
              />
            </div>

            {error && <p className="auth-form__error">{error}</p>}

            <button className="btn btn--primary" type="submit" disabled={submitting}>
              {submitting ? t('auth.resetPassword.submitting') : t('auth.resetPassword.submit')}
            </button>
          </form>

          <p className="auth-card__footer">
            <Link to="/login">{t('auth.resetPassword.toLogin')}</Link>
          </p>
        </div>
      </section>
    </main>
  );
}

export default ResetPassword;
