import {Link} from "react-router-dom"
import '../styles/site.css';
import { useCart } from '../context';
import CartLine from '../components/ItemCard/CartLine';
import type { Item,CartContextValue} from '../types';
import { useLanguage } from '../context/languageContext';
function Cart() {
  const { t } = useLanguage();
  const {cartItems, cartCount} = useCart() as CartContextValue;
  const subtotal = cartItems.reduce((acc: number, item: Item) => acc + item.price * (item.quantity ?? 1), 0);
  const currency = cartItems[0]?.currency ?? 'UAH';

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
            {cartCount<=0 ? (<p className='empty-cart-message'>{t('cart.emptyMessage')} <Link className="empty-cart-link" to="/categories">{t('cart.emptyLink')}</Link></p>) :
            (cartItems.map((item: Item) => (
              <CartLine key={item.id} item={item} />
            )))}
          </div>

          <aside className="cart-summary">
            <h2>{t('cart.orderSummary')}</h2>
            <div className="cart-row"><span>{t('cart.subtotal')}</span><span>{currency} {subtotal}</span></div>
            <div className="cart-row cart-row--total"><span>{t('cart.total')}</span><span>{currency} {subtotal}</span></div>
            <button className="btn btn--primary" type="button">{t('cart.checkout')}</button>
            <Link className="btn btn--ghost" to="/categories" style={{marginTop: '0.75rem', width: '100%'}}>{t('cart.continueShopping')}</Link>
          </aside>
        </div>
      </section>
    </main>
     
    )
}
export default Cart;