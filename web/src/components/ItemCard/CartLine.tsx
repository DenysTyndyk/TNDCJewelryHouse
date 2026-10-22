import '../../styles/site.css';
import { useCart } from '../../context';
import type { Item } from '../../types';
const removeFromCart_svg = <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
<path d="M3 6h18"/>
<path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
<path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/>
<line x1="10" y1="11" x2="10" y2="17"/>
<line x1="14" y1="11" x2="14" y2="17"/>
</svg> 
function CartLine({ item }: { item: Item }) {
    const {toggleCart} = useCart() ;
    const thumbImage = item.images?.[0];
    return (
        <article className="product product--cart-line">
          <img className="product__thumb" src={thumbImage} alt={item.title} />
          
          <div className="product__meta">
            <div className="product__info">
              <span className="product__cat">{item.category}</span>
              <h3 className="product__name">{item.title}</h3>
            </div>
    
            <div className="product__price-row">
              <span className="product__price">PLN {item.price}</span>
              <button 
                onClick={() => toggleCart(item )}  
                className="remove-from-cart-btn" 
                type="button" 
                aria-label="Remove item from cart"
              >
                {removeFromCart_svg}
              </button>
            </div>
          </div>
        </article>
      );
    }

export default CartLine;
