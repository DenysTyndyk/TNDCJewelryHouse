import '../../styles/site.css';
import ImageSliderOnHover from "./ImageSliderOnHover.jsx";
import {useState} from 'react'
import {useCart} from '../../context/cartContext.jsx'
const activeCart_svg = <svg
xmlns="http://www.w3.org/2000/svg"
width="18"
height="18"
viewBox="0 0 24 24"
fill="none"
stroke="currentColor"
strokeWidth="1.5"
strokeLinecap="round"
strokeLinejoin="round"
aria-hidden="true"
>
<path d="M6 2L3 6v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2V6l-3-4z" />
<line x1="3" y1="6" x2="21" y2="6" />
<path d="M16 10a4 4 0 0 1-8 0" />
<line x1="12" y1="14" x2="12" y2="18" />
<line x1="10" y1="16" x2="14" y2="16" />
</svg>
const removeFromCart_svg = <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
<path d="M3 6h18"/>
<path d="M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
<path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6"/>
<line x1="10" y1="11" x2="10" y2="17"/>
<line x1="14" y1="11" x2="14" y2="17"/>
</svg> 
function ItemCard({ item }) {
    const {toggleCart, cartItems} = useCart();
    const isInCart = cartItems.find((it) => it.id === item.id)
  return (
    <article className="product">
      <ImageSliderOnHover images = {item.images} alt={item.title}/>
      <div className="product__meta">
        <span className="product__cat">{item.category}</span>
        <h3 className="product__name">{item.title}</h3>
        {item.description && <p className="product__description">{item.description}</p>}
        <div className="product__price-row">
          <span className="product__price">PLN {item.price}</span>
          <button onClick={() => toggleCart(item)}  className="add-to-cart-btn" type="button" aria-label="Add to cart">
            {isInCart ? removeFromCart_svg : activeCart_svg}
          </button>
        </div>
      </div>
    </article>
  );
}

export default ItemCard;
