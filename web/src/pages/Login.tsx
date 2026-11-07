import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context';
import { useLanguage } from '../context/languageContext';
import '../styles/site.css';

function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const { signIn } = useAuth();
  const { t } = useLanguage();
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    const { error } = await signIn(email, password);
    setSubmitting(false);
    if (error) {
      setError(error);
      return;
    }
    navigate('/account');
  }

  return (
    <main>
      <section className="section auth-section">
        <div className="auth-card">
          <h1>{t('auth.login.title')}</h1>
          <p className="auth-card__subtitle">{t('auth.login.subtitle')}</p>

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="field">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="field">
              <label htmlFor="password">{t('auth.login.password')}</label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="current-password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
            </div>

            {error && <p className="auth-form__error">{error}</p>}

            <button className="btn btn--primary" type="submit" disabled={submitting}>
              {submitting ? t('auth.login.submitting') : t('auth.login.submit')}
            </button>
          </form>

          <p className="auth-card__footer">
            {t('auth.login.noAccount')} <Link to="/register">{t('auth.login.signUp')}</Link>
            <br />
            <Link to="/forgot-password">{t('auth.login.forgotPassword')}</Link>
          </p>
        </div>
      </section>
    </main>
  );
}

export default Login;
