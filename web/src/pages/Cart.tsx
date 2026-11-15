import {Link} from "react-router-dom"
import '../styles/site.css';
import { useCart } from '../context';
import CartLine from '../components/ItemCard/CartLine';
import { useLanguage } from '../context/languageContext';
function Cart() {
  const { t } = useLanguage();
  const { cart, cartCount, error } = useCart();
  const { subtotal, currency } = cart;

    return (
        <main>
      <section className="page-hero">
        <div className="container">
          <p className="section__eyebrow">{t('cart.eyebrow')}</p>
        </div>
      </section>

      <section className="section">
        <div className="container cart-layout">
          <div>
            {error && <p role="alert">{error}</p>}
            {cartCount<=0 ? (<p className='empty-cart-message'>{t('cart.emptyMessage')} <Link className="empty-cart-link" to="/categories">{t('cart.emptyLink')}</Link></p>) :
            (cart.items.map((line) => (
              <CartLine key={line.id} line={line} currency={currency} />
            )))}
          </div>

          <aside className="cart-summary">
            <h2>{t('cart.orderSummary')}</h2>
            <div className="cart-row"><span>{t('cart.subtotal')}</span><span>{currency} {subtotal}</span></div>
            <div className="cart-row cart-row--total"><span>{t('cart.total')}</span><span>{currency} {subtotal}</span></div>
            {cartCount > 0 && <Link className="btn btn--primary" to="/checkout">{t('cart.checkout')}</Link>}
            <Link className="btn btn--ghost" to="/categories" style={{marginTop: '0.75rem', width: '100%'}}>{t('cart.continueShopping')}</Link>
          </aside>
        </div>
      </section>
    </main>
     
    )
}
export default Cart;