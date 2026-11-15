import { useEffect, useState } from 'react';
import { Link, Navigate } from 'react-router-dom';
import { useAuth } from '../context';
import { useLanguage } from '../context/languageContext';
import { useTracking } from '../context/trackingContext';
import { listOrders } from '../api/orderApi';
import type { Order } from '../types';
import '../styles/site.css';

function Account() {
  const { user, loading, signOut, accessToken } = useAuth();
  const { t, language } = useLanguage();
  const { consent, setConsent } = useTracking();
  const [orders, setOrders] = useState<Order[] | null>(null);
  const [consentError, setConsentError] = useState<string | null>(null);

  // Withdrawing must be as easy as granting (RODO art. 7(3)): one checkbox, no confirmation.
  async function toggleConsent(granted: boolean) {
    setConsentError(null);
    try {
      await setConsent(granted ? 'granted' : 'denied');
    } catch {
      setConsentError(t('consent.saveError'));
    }
  }

  useEffect(() => {
    if (!accessToken) return;
    let active = true;
    listOrders(accessToken)
      .then((list) => active && setOrders(list))
      .catch(() => active && setOrders([]));
    return () => { active = false; };
  }, [accessToken]);

  if (loading) {
    return (
      <main>
        <section className="section auth-section">
          <p className="auth-card__subtitle">{t('account.loading')}</p>
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
          <h1>{t('account.title')}</h1>
          <p className="auth-card__subtitle">{user.email}</p>

          <h2>{t('account.orders')}</h2>
          {orders === null ? (
            <p>{t('account.loading')}</p>
          ) : orders.length === 0 ? (
            <p>{t('account.noOrders')}</p>
          ) : (
            <ul className="order-list">
              {orders.map((o) => (
                <li key={o.order_number}>
                  <Link to={`/orders/${o.order_number}`}>{o.order_number}</Link>
                  <span>{new Date(o.created_at).toLocaleDateString(language)}</span>
                  <span className={`order-status order-status--${o.status}`}>{t(`order.status.${o.status}`)}</span>
                  <span>{o.currency} {o.total}</span>
                </li>
              ))}
            </ul>
          )}

          <h2>{t('consent.title')}</h2>
          <label className="catalog-filters__check">
            <input
              type="checkbox"
              checked={consent === 'granted'}
              onChange={(e) => toggleConsent(e.target.checked)}
            />
            {t('consent.accountToggle')}
          </label>
          <p className="auth-card__subtitle">{t('consent.withdrawNote')}</p>
          {consentError && <p role="alert">{consentError}</p>}

          <button className="btn btn--ghost" style={{ width: '100%' }} onClick={signOut}>
            {t('account.signOut')}
          </button>
        </div>
      </section>
    </main>
  );
}

export default Account;
