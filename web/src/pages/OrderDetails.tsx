import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import { useAuth } from '../context';
import { useLanguage } from '../context/languageContext';
import { cancelOrder, getOrder } from '../api/orderApi';
import type { Order } from '../types';
import '../styles/site.css';

function OrderDetails() {
  const { number = '' } = useParams();
  const { t, language } = useLanguage();
  const { accessToken, loading: authLoading } = useAuth();
  const [order, setOrder] = useState<Order | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cancelling, setCancelling] = useState(false);

  useEffect(() => {
    if (authLoading) return; // the owner (user or guest) is unknown until auth resolves
    let active = true;
    setError(null);
    getOrder(number, accessToken)
      .then((o) => active && setOrder(o))
      .catch((e: Error) => active && setError(e.message));
    return () => { active = false; };
  }, [number, accessToken, authLoading]);

  async function handleCancel() {
    if (!order || !window.confirm(t('order.cancelConfirm'))) return;
    setCancelling(true);
    try {
      setOrder(await cancelOrder(order.order_number, accessToken));
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setCancelling(false);
    }
  }

  if (error && !order) {
    return (
      <main className="section"><div className="container">
        <p role="alert">{error === 'Order not found' ? t('order.notFound') : error}</p>
        <Link to="/categories">{t('header.categories')}</Link>
      </div></main>
    );
  }
  if (!order) return <main className="section"><div className="container"><p>{t('account.loading')}</p></div></main>;

  const { currency } = order;
  const delivery = [order.shipping_city, order.provider_point_id ? `${t('checkout.point')} ${order.provider_point_id}` : order.shipping_address_line]
    .filter(Boolean)
    .join(', ');

  return (
    <main>
      <section className="page-hero">
        <div className="container">
          <p className="section__eyebrow">{t('order.eyebrow')}</p>
          <h1>{order.order_number}</h1>
          <p>
            <span className={`order-status order-status--${order.status}`}>{t(`order.status.${order.status}`)}</span>
            {' · '}{new Date(order.created_at).toLocaleString(language)}
          </p>
        </div>
      </section>

      <section className="section">
        <div className="container cart-layout">
          <div>
            <h2>{t('order.items')}</h2>
            {order.items.map((item) => (
              <div className="cart-row" key={item.sku}>
                <span>{item.product_name} ({item.sku}) × {item.quantity}</span>
                <span>{currency} {item.line_total}</span>
              </div>
            ))}

            <h2>{t('checkout.delivery')}</h2>
            <p>{order.recipient_name}, {order.recipient_phone}</p>
            <p>{delivery}</p>
            {order.tracking_number && <p>{t('order.tracking')}: {order.tracking_number}</p>}
            {order.customer_note && <p>{t('checkout.note')}: {order.customer_note}</p>}
          </div>

          <aside className="cart-summary">
            <h2>{t('cart.orderSummary')}</h2>
            <div className="cart-row"><span>{t('cart.subtotal')}</span><span>{currency} {order.subtotal}</span></div>
            <div className="cart-row"><span>{t('checkout.shipping')}</span><span>{currency} {order.shipping_amount}</span></div>
            <div className="cart-row cart-row--total"><span>{t('cart.total')}</span><span>{currency} {order.total}</span></div>
            {error && <p className="auth-form__error" role="alert">{error}</p>}
            {order.status === 'Pending' && (
              <button className="btn btn--ghost" type="button" onClick={handleCancel} disabled={cancelling}>
                {t('order.cancel')}
              </button>
            )}
            <Link className="btn btn--ghost" to="/categories">{t('cart.continueShopping')}</Link>
          </aside>
        </div>
      </section>
    </main>
  );
}

export default OrderDetails;
