import { useEffect, useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import * as authApi from '../api/authApi';
import { useLanguage } from '../context/languageContext';
import '../styles/site.css';

function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token');
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [error, setError] = useState<string | null>(null);
  const { t } = useLanguage();

  useEffect(() => {
    if (!token) {
      setStatus('error');
      setError(t('auth.verifyEmail.missingToken'));
      return;
    }
    authApi
      .verifyEmail(token)
      .then(() => setStatus('success'))
      .catch((err) => {
        setStatus('error');
        setError(err.message);
      });
  }, [token, t]);

  return (
    <main>
      <section className="section auth-section">
        <div className="auth-card">
          <h1>{t('auth.verifyEmail.title')}</h1>

          {status === 'loading' && <p className="auth-card__subtitle">{t('auth.verifyEmail.checking')}</p>}

          {status === 'success' && (
            <>
              <p className="auth-card__subtitle">{t('auth.verifyEmail.success')}</p>
              <Link className="btn btn--primary" to="/login" style={{ width: '100%', display: 'flex' }}>
                {t('auth.verifyEmail.signIn')}
              </Link>
            </>
          )}

          {status === 'error' && (
            <>
              <p className="auth-form__error">{error}</p>
              <Link className="btn btn--ghost" to="/login" style={{ width: '100%', display: 'flex' }}>
                {t('auth.verifyEmail.toLogin')}
              </Link>
            </>
          )}
        </div>
      </section>
    </main>
  );
}

export default VerifyEmail;
