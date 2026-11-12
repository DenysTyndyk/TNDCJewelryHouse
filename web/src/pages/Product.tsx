import '../styles/site.css';
import { useEffect, useState } from 'react';
import { Link, useParams } from 'react-router-dom';
import ImageSliderOnHover from '../components/ItemCard/ImageSliderOnHover.jsx';
import { getProductBySlug } from '../api/catalogApi';
import { useLanguage } from '../context/languageContext';
import { useCart } from '../context/cartContext';
import type { ProductDetail, ProductVariant,ProductGemstone } from '../types';

type T = (key: string) => string;

function variantLabel(v: ProductVariant, t: T): string {
  return [
    v.metal_type && t(`product.metal.${v.metal_type}`),
    v.metal_color && t(`product.color.${v.metal_color}`),
    v.fineness,
    v.size,
    v.length_mm && `${v.length_mm} ${t('product.units.mm')}`,
  ].filter(Boolean).join(' · ') || v.sku;
}

function gemstoneName(g: ProductGemstone, t: T): string {
  const key = `gemstones.${g.slug}`;
  const label = t(key);
  return label === key ? g.name : label;
}


function Product() {
  const { slug = '' } = useParams();
  const { t, language } = useLanguage();
  const { addToCart, isInCart } = useCart();
  const [product, setProduct] = useState<ProductDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [variantId, setVariantId] = useState<number | null>(null);

  useEffect(() => {
    let active = true;
    setError(null);
    getProductBySlug(slug, language)
      .then((p) => {
        if (!active) return;
        setProduct(p);
        setVariantId((prev) =>
          p.variants.some((v) => v.id === prev) ? prev : (p.variants.find((v) => v.in_stock) ?? p.variants[0])?.id ?? null,
        );
      })
      .catch((e: Error) => active && setError(e.message));
    return () => { active = false; };
  }, [slug, language]);

  if (error) {
    return (
      <main className="section"><div className="container">
        <p role="alert">{error === 'Product not found' ? t('product.notFound') : error}</p>
        <Link to="/categories">{t('header.categories')}</Link>
      </div></main>
    );
  }
  if (!product) return <main className="section"><div className="container"><p>{t('product.loading')}</p></div></main>;

  const variant = product.variants.find((v) => v.id === variantId);
  const images = product.images.filter((img) => img.variant_id === null || img.variant_id === variantId).map((img) => img.url);
  const specs: [string, string | number | null][] = variant
    ? [
        [t('product.specs.sku'), variant.sku],
        [t('product.specs.metal'), variant.metal_type ? t(`product.metal.${variant.metal_type}`) : null],
        [t('product.specs.color'), variant.metal_color ? t(`product.color.${variant.metal_color}`) : null],
        [t('product.specs.fineness'), variant.fineness],
        [t('product.specs.weight'), variant.weight ? `${Number(variant.weight)} ${t('product.units.g')}` : null],
        [t('product.specs.length'), variant.length_mm ? `${variant.length_mm} ${t('product.units.mm')}` : null],
        [t('product.specs.size'), variant.size],
      ]
    : [];
  const stones = product.gemstones.filter((g) => g.variant_id === null || g.variant_id === variantId);

  return (
    <main className="section">
      <div className="container product-page">
        <Link className="section__eyebrow" to="/categories" state={{ category: product.category.slug }}>{product.category.name}</Link>
        <h1>{product.name}</h1>
        <div className="product-page__gallery">
          <ImageSliderOnHover images={images} alt={product.name} />
        </div>
        {product.description && <p className="section__lead">{product.description}</p>}

        {product.variants.length > 1 && (
          <div className="filters" role="group" aria-label={t('product.variant')}>
            {product.variants.map((v) => (
              <button key={v.id} type="button" className={`filter ${v.id === variantId ? 'is-active' : ''}`} aria-pressed={v.id === variantId} onClick={() => setVariantId(v.id)}>
                {variantLabel(v, t)}
              </button>
            ))}
          </div>
        )}

        {variant && (
          <>
            <p className="product__price">
              {variant.sale_price
                ? <><s>{variant.currency} {variant.price}</s> {variant.currency} {variant.sale_price}</>
                : <>{variant.currency} {variant.price}</>}
            </p>
            {!variant.in_stock && <p>{t('product.outOfStock')}</p>}
            {isInCart(product.id) ? (
              <Link className="btn btn--ghost" to="/cart">{t('product.goToCart')}</Link>
            ) : (
              <button
                className="btn btn--primary"
                type="button"
                disabled={!variant.in_stock}
                onClick={() => addToCart({
                  id: product.id,
                  slug: product.slug,
                  title: product.name,
                  price: Number(variant.sale_price ?? variant.price),
                  currency: variant.currency,
                  description: '',
                  category: product.category.slug,
                  images: images.slice(0, 1),
                })}
              >
                {t('product.addToCart')}
              </button>
            )}
                        <h2 className="product-specs__title">{t('product.specs.title')}</h2>
            <dl className="product-specs">
              {specs
                .filter(([, value]) => value !== null && value !== '')
                .map(([label, value]) => (
                  <div key={label} className="product-specs__row">
                    <dt>{label}</dt>
                    <dd>{value}</dd>
                  </div>
                ))}
              {stones.length > 0 && (
                <div className="product-specs__row">
                  <dt>{t('product.specs.gemstones')}</dt>
                  <dd>
                    {stones.map((g, i) => (
                      <p key={i}>
                        {[
                          gemstoneName(g, t),
                          `${g.quantity} ${t('product.units.pcs')}`,
                          g.carat && `${Number(g.carat)} ${t('product.units.ct')}`,
                          g.cut_type,
                          g.color_grade && g.clarity_grade && `${g.color_grade}/${g.clarity_grade}`,
                          t(`product.gemstoneType.${g.gemstone_type}`),
                          g.is_center_stone && t('product.centerStone'),
                        ].filter(Boolean).join(', ')}
                      </p>
                    ))}
                  </dd>
                </div>
              )}
            </dl>

          </>
        )}
      </div>
    </main>
  );
}
export default Product;
