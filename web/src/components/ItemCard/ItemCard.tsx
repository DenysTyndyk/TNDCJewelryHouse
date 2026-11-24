import '../../styles/site.css';
import ImageSliderOnHover from "./ImageSliderOnHover.jsx";
import { useCart } from '../../context/cartContext';
import { useLanguage } from '../../context/languageContext';
import type { Item } from '../../types'
import { Link } from 'react-router-dom';

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
// The list has no variant_id, so the card links to the product page to pick a variant.
// onOpen: optional hook for pages that log which result was opened (search clicks).
function ItemCard({ item, onOpen }: { item: Item; onOpen?: () => void }) {
    const { cart } = useCart();
    const { t } = useLanguage();
    const isInCart = cart.items.some((line) => line.product_slug === item.slug);
  return (
    <article className="product">
      <ImageSliderOnHover images = {item.images} alt={item.title}/>
      <div className="product__meta">
        <span className="product__cat">{item.category}</span>
<h3 className="product__name"><Link to={`/products/${item.slug}`} onClick={onOpen}>{item.title}</Link></h3>
        {item.description && <p className="product__description">{item.description}</p>}
        <div className="product__price-row">
<span className="product__price">{item.currency ?? 'UAH'} {item.price}</span>
          <Link to={isInCart ? '/cart' : `/products/${item.slug}`} className="add-to-cart-btn" onClick={onOpen} aria-label={isInCart ? t('product.goToCart') : t('product.addToCart')}>
            {activeCart_svg}
          </Link>
        </div>
      </div>
    </article>
  );
}

export default ItemCard;
