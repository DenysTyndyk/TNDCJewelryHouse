import '../../styles/site.css';
import { useCart } from '../../context';
import { useLanguage } from '../../context/languageContext';
import { Link } from 'react-router-dom';
import type { CartLine as Line } from '../../types';
const removeFromCart_svg = <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
<path d="M3 6h18"/>
<path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
<path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/>
<line x1="10" y1="11" x2="10" y2="17"/>
<line x1="14" y1="11" x2="14" y2="17"/>
</svg> 
function CartLine({ line, currency }: { line: Line; currency: string }) {
    const {removeFromCart, setQuantity} = useCart() ;
    const { t } = useLanguage();
    const quantity = line.quantity;
    return (
        <article className="product product--cart-line">
          {line.image_url && <img className="product__thumb" src={line.image_url} alt={line.name} />}

          <div className="product__meta">
            <div className="product__info">
              <span className="product__cat">{line.size ? `${line.sku} · ${line.size}` : line.sku}</span>
              <h3 className="product__name"><Link to={`/products/${line.product_slug}`}>{line.name}</Link></h3>
            </div>

            <div className="product__price-row">
              <div className="qty-stepper" role="group" aria-label={t('cart.quantity')}>
                <button type="button" onClick={() => setQuantity(line.id, quantity - 1)} disabled={quantity <= 1} aria-label={t('cart.decrease')}>−</button>
                <span aria-live="polite">{quantity}</span>
                <button type="button" onClick={() => setQuantity(line.id, quantity + 1)} disabled={quantity >= line.available} aria-label={t('cart.increase')}>+</button>
              </div>
              <span className="product__price">{currency} {line.line_total}</span>
              <button
                onClick={() => removeFromCart(line.id)}
                className="remove-from-cart-btn" 
                type="button" 
                aria-label={t('product.removeFromCart')}
              >
                {removeFromCart_svg}
              </button>
            </div>
          </div>
        </article>
      );
    }

export default CartLine;
