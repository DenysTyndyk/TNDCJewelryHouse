import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth, useCart } from '../context';
import { useLanguage } from '../context/languageContext';
import { createOrder, listShippingMethods } from '../api/orderApi';
import type { ShippingMethod } from '../types';
import '../styles/site.css';

// Same rule as the backend (E.164); the server validates again.
const PHONE_PATTERN = '\\+[1-9]\\d{7,14}';
const POINT_PROVIDERS = ['NovaPoshta', 'UkrPoshta'];

// Preview only: the server recalculates shipping at checkout.
function shippingCost(method: ShippingMethod | undefined, subtotal: number): number {
  if (!method) return 0;
  if (method.free_from_amount !== null && subtotal >= Number(method.free_from_amount)) return 0;
  return Number(method.cost);
}

function Checkout() {
  const { t, language } = useLanguage();
  const { user, accessToken } = useAuth();
  const { cart, cartCount, refresh } = useCart();
  const navigate = useNavigate();

  const [methods, setMethods] = useState<ShippingMethod[]>([]);
  const [methodId, setMethodId] = useState<number | null>(null);
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [city, setCity] = useState('');
  const [point, setPoint] = useState('');
  const [address, setAddress] = useState('');
  const [note, setNote] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    listShippingMethods()
      .then((list) => {
        setMethods(list);
        setMethodId((prev) => prev ?? list[0]?.id ?? null);
      })
      .catch((e: Error) => setError(e.message));
  }, []);

  // Prefill the account email once it is known; the user can still change it.
  useEffect(() => {
    if (user?.email) setEmail((prev) => prev || user.email);
  }, [user]);

  const method = methods.find((m) => m.id === methodId);
  const needsPoint = method ? POINT_PROVIDERS.includes(method.provider) : false;
  const subtotal = Number(cart.subtotal);
  const shipping = shippingCost(method, subtotal);
  const { currency } = cart;

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (methodId === null) return;
    setError(null);
    setSubmitting(true);
    try {
      const order = await createOrder(
        {
          recipient_name: name,
          recipient_phone: phone,
          customer_email: email,
          shipping_method_id: methodId,
          shipping_city: city,
          provider_point_id: needsPoint ? point : null,
          shipping_address_line: needsPoint ? null : address,
          customer_note: note.trim() || null,
        },
        accessToken,
        language,
      );
      navigate(`/orders/${order.order_number}`);
      void refresh(); // the server cart is now empty
    } catch (err) {
      setError((err as Error).message);
      void refresh(); // e.g. 409: show the current stock in the cart
    } finally {
      setSubmitting(false);
    }
  }

  if (cartCount <= 0) {
    return (
      <main className="section">
        <div className="container">
          <p className="empty-cart-message">
            {t('cart.emptyMessage')} <Link className="empty-cart-link" to="/categories">{t('cart.emptyLink')}</Link>
          </p>
        </div>
      </main>
    );
  }

  return (
    <main>
      <section className="page-hero">
        <div className="container">
          <p className="section__eyebrow">{t('checkout.eyebrow')}</p>
          <h1>{t('checkout.title')}</h1>
        </div>
      </section>

      <section className="section">
        <form className="container cart-layout" onSubmit={handleSubmit}>
          <div className="auth-form">
            <h2>{t('checkout.recipient')}</h2>
            <div className="field">
              <label htmlFor="recipientName">{t('checkout.name')}</label>
              <input id="recipientName" autoComplete="name" required minLength={2} maxLength={200}
                value={name} onChange={(e) => setName(e.target.value)} />
            </div>
            <div className="field">
              <label htmlFor="recipientPhone">{t('checkout.phone')}</label>
              <input id="recipientPhone" type="tel" autoComplete="tel" required placeholder="+380501234567"
                pattern={PHONE_PATTERN} title={t('auth.register.invalidPhone')}
                value={phone} onChange={(e) => setPhone(e.target.value)} />
            </div>
            <div className="field">
              <label htmlFor="customerEmail">Email</label>
              <input id="customerEmail" type="email" autoComplete="email" required
                value={email} onChange={(e) => setEmail(e.target.value)} />
            </div>

            <h2>{t('checkout.delivery')}</h2>
            <fieldset className="shipping-options">
              <legend className="visually-hidden">{t('checkout.delivery')}</legend>
              {methods.map((m) => (
                <label key={m.id} className={`shipping-option ${m.id === methodId ? 'is-active' : ''}`}>
                  <input type="radio" name="shippingMethod" value={m.id}
                    checked={m.id === methodId} onChange={() => setMethodId(m.id)} />
                  <span>{t(`checkout.provider.${m.provider}`)}</span>
                  <span className="shipping-option__meta">
                    {m.delivery_days_min !== null && m.delivery_days_max !== null &&
                      `${m.delivery_days_min}–${m.delivery_days_max} ${t('checkout.days')} · `}
                    {shippingCost(m, subtotal) === 0 ? t('checkout.free') : `${m.currency} ${m.cost}`}
                  </span>
                </label>
              ))}
            </fieldset>
            <div className="field">
              <label htmlFor="city">{t('checkout.city')}</label>
              <input id="city" autoComplete="address-level2" required minLength={2} maxLength={100}
                value={city} onChange={(e) => setCity(e.target.value)} />
            </div>
            {needsPoint ? (
              <div className="field">
                <label htmlFor="point">{t('checkout.point')}</label>
                <input id="point" required maxLength={64} placeholder={t('checkout.pointPlaceholder')}
                  value={point} onChange={(e) => setPoint(e.target.value)} />
              </div>
            ) : (
              <div className="field">
                <label htmlFor="address">{t('checkout.address')}</label>
                <input id="address" autoComplete="street-address" required minLength={3} maxLength={255}
                  value={address} onChange={(e) => setAddress(e.target.value)} />
              </div>
            )}
            <div className="field">
              <label htmlFor="note">{t('checkout.note')}</label>
              <textarea id="note" maxLength={1000} value={note} onChange={(e) => setNote(e.target.value)} />
            </div>
          </div>

          <aside className="cart-summary">
            <h2>{t('cart.orderSummary')}</h2>
            {cart.items.map((line) => (
              <div className="cart-row" key={line.id}>
                <span>{line.name}{line.size ? ` · ${line.size}` : ''} × {line.quantity}</span>
                <span>{currency} {line.line_total}</span>
              </div>
            ))}
            <div className="cart-row"><span>{t('cart.subtotal')}</span><span>{currency} {cart.subtotal}</span></div>
            <div className="cart-row">
              <span>{t('checkout.shipping')}</span>
              <span>{shipping === 0 ? t('checkout.free') : `${currency} ${shipping.toFixed(2)}`}</span>
            </div>
            <div className="cart-row cart-row--total">
              <span>{t('cart.total')}</span><span>{currency} {(subtotal + shipping).toFixed(2)}</span>
            </div>
            {error && <p className="auth-form__error" role="alert">{error}</p>}
            <button className="btn btn--primary" type="submit" disabled={submitting || methodId === null}>
              {submitting ? t('checkout.submitting') : t('checkout.submit')}
            </button>
            <Link className="btn btn--ghost" to="/cart">{t('checkout.backToCart')}</Link>
          </aside>
        </form>
      </section>
    </main>
  );
}

export default Checkout;
