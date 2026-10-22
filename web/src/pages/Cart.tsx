import { useState, useEffect } from 'react';
import {Link} from "react-router-dom"
import '../styles/site.css';
import { useCart } from '../context';
import CartLine from '../components/ItemCard/CartLine';
import type { Item,CartContextValue} from '../types';
function Cart() {
  const [subtotal, setSubtotal] = useState(0);
  const {cartItems, cartCount} = useCart() as CartContextValue;

  useEffect(() => {
    setSubtotal(cartItems.reduce((acc: number, item: Item) => acc + item.price, 0))
  }, [cartItems])

    return (
        <main>
      <section className="page-hero">
        <div className="container">
          <p className="section__eyebrow">Shopping</p>
        </div>
      </section>

      <section className="section">
        <div className="container cart-layout">
          <div>
            {cartCount<=0 ? (<p className='empty-cart-message'>Your cart is empty. Return to the shop to browse accessories <Link className="empty-cart-link" to="/categories">Click</Link></p>) :
            (cartItems.map((item: Item) => (
              <CartLine key={item.id} item={item} />
            )))}
          </div>

          <aside className="cart-summary">
            <h2>Order summary</h2>
            <div className="cart-row"><span>Subtotal</span><span>PLN {subtotal}</span></div>
            <div className="cart-row cart-row--total"><span>Total</span><span>PLN {subtotal}</span></div>
            <button className="btn btn--primary" type="button">Proceed to checkout</button>
            <Link className="btn btn--ghost" to="/categories" style={{marginTop: '0.75rem', width: '100%'}}>Continue shopping</Link>
          </aside>
        </div>
      </section>
    </main>
     
    )
}
export default Cart;