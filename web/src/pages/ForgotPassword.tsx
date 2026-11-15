import { useState } from 'react';
import { Link } from 'react-router-dom';
import * as authApi from '../api/authApi';
import { useLanguage } from '../context/languageContext';
import '../styles/site.css';

function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);
  const { t } = useLanguage();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await authApi.forgotPassword(email);
    } finally {
      setSubmitting(false);
      setDone(true);
    }
  }

  if (done) {
    return (
      <main>
        <section className="section auth-section">
          <div className="auth-card">
            <h1>{t('auth.forgotPassword.doneTitle')}</h1>
            <p className="auth-card__subtitle">
              {t('auth.forgotPassword.doneSubtitle')}
            </p>
            <Link className="btn btn--primary" to="/login" style={{ width: '100%', display: 'flex' }}>
              {t('auth.forgotPassword.toLogin')}
            </Link>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main>
      <section className="section auth-section">
        <div className="auth-card">
          <h1>{t('auth.forgotPassword.title')}</h1>
          <p className="auth-card__subtitle">{t('auth.forgotPassword.subtitle')}</p>

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
            <button className="btn btn--primary" type="submit" disabled={submitting}>
              {submitting ? t('auth.forgotPassword.submitting') : t('auth.forgotPassword.submit')}
            </button>
          </form>

          <p className="auth-card__footer">
            {t('auth.forgotPassword.rememberedPassword')} <Link to="/login">{t('auth.forgotPassword.signIn')}</Link>
          </p>
        </div>
      </section>
    </main>
  );
}

export default ForgotPassword;
