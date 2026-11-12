import '../styles/site.css';
import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import ItemCard from '../components/ItemCard/ItemCard';
import { listCategories, listProducts, toItem } from '../api/catalogApi';
import type { CategoryNode, Item, MetalColor, MetalType, ProductFilters, SortOrder } from '../types';
import { useLanguage } from '../context/languageContext';

type PanelFilters = Pick<ProductFilters, 'metal' | 'color' | 'fineness' | 'gemstone' | 'price_max' | 'in_stock' | 'sort'>;

const METALS: MetalType[] = ['Gold', 'Silver', 'Platinum'];
const COLORS: MetalColor[] = ['White', 'Yellow', 'Rose', 'Bicolor'];
const FINENESS = [375, 500, 585, 750, 875, 925, 958, 999]; // same list as the DB check constraint
// shortcut: same slugs as the seed and the `gemstones.*` i18n keys; switch to a /gemstones endpoint if admins add stones
const GEMSTONES = ['diamond', 'sapphire', 'ruby', 'emerald', 'amethyst', 'topaz', 'pearl', 'cubic_zirconia'];
const SORTS: SortOrder[] = ['newest', 'price_asc', 'price_desc', 'popular'];
const EMPTY_FILTERS: PanelFilters = { sort: 'newest' };

function Categories() {
  const { t, language } = useLanguage();
  const location = useLocation();
  const [selectedCategory, setSelectedCategory] = useState<string>(location.state?.category || 'all');
  const [filters, setFilters] = useState<PanelFilters>(EMPTY_FILTERS);
  const [categories, setCategories] = useState<CategoryNode[]>([]);
  const [items, setItems] = useState<Item[]>([]);
  const [nextCursor, setNextCursor] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listCategories(language).then(setCategories).catch(() => setCategories([]));
  }, [language]);

  const query = { ...filters, category: selectedCategory === 'all' ? undefined : selectedCategory, locale: language };

  useEffect(() => {
    let active = true; // ignore responses that arrive after the filters changed again
    setLoading(true);
    setError(null);
    listProducts(query)
      .then((page) => {
        if (!active) return;
        setItems(page.items.map(toItem));
        setNextCursor(page.next_cursor ?? null);
      })
      .catch(() => active && setError(t('product.loadError')))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [selectedCategory, filters, language]);

  const loadMore = () => {
    if (!nextCursor) return;
    setLoading(true);
    listProducts({ ...query, cursor: nextCursor })
      .then((page) => {
        setItems((prev) => [...prev, ...page.items.map(toItem)]);
        setNextCursor(page.next_cursor ?? null);
      })
      .catch(() => setError(t('product.loadError')))
      .finally(() => setLoading(false));
  };

  const update = (patch: Partial<PanelFilters>) => setFilters((prev) => ({ ...prev, ...patch }));

  const filterButton = (slug: string, label: string) => (
    <button key={slug} className={`filter ${selectedCategory === slug ? 'is-active' : ''}`} onClick={() => setSelectedCategory(slug)} type="button" aria-pressed={selectedCategory === slug}>{label}</button>
  );

  return (
    <main>
      <section className="page-hero">
        <div className="container">
          <p className="section__eyebrow">{t('categories.eyebrow')}</p>
          <h1>{t('categories.title')}</h1>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="filters" role="group" aria-label="Category filters">
            {filterButton('all', t('categories.filterAll'))}
            {categories.map((c) => filterButton(c.slug, c.name))}
          </div>

          <form className="catalog-filters" aria-label="Product filters" onSubmit={(e) => e.preventDefault()}>
            <label>
              {t('product.specs.metal')}
              <select value={filters.metal ?? ''} onChange={(e) => update({ metal: (e.target.value || undefined) as MetalType | undefined })}>
                <option value="">{t('categories.panel.any')}</option>
                {METALS.map((m) => <option key={m} value={m}>{t(`product.metal.${m}`)}</option>)}
              </select>
            </label>
            <label>
              {t('product.specs.color')}
              <select value={filters.color ?? ''} onChange={(e) => update({ color: (e.target.value || undefined) as MetalColor | undefined })}>
                <option value="">{t('categories.panel.any')}</option>
                {COLORS.map((c) => <option key={c} value={c}>{t(`product.color.${c}`)}</option>)}
              </select>
            </label>
            <label>
              {t('product.specs.fineness')}
              <select value={filters.fineness ?? ''} onChange={(e) => update({ fineness: e.target.value ? Number(e.target.value) : undefined })}>
                <option value="">{t('categories.panel.any')}</option>
                {FINENESS.map((f) => <option key={f} value={f}>{f}</option>)}
              </select>
            </label>
            <label>
              {t('product.specs.gemstones')}
              <select value={filters.gemstone ?? ''} onChange={(e) => update({ gemstone: e.target.value || undefined })}>
                <option value="">{t('categories.panel.any')}</option>
                {GEMSTONES.map((g) => <option key={g} value={g}>{t(`gemstones.${g}`)}</option>)}
              </select>
            </label>
            <label>
              {t('categories.panel.priceMax')}
              <input
                type="number"
                min={0}
                step={100}
                inputMode="numeric"
                value={filters.price_max ?? ''}
                onChange={(e) => update({ price_max: e.target.value ? Number(e.target.value) : undefined })}
              />
            </label>
            <label className="catalog-filters__check">
              <input type="checkbox" checked={!!filters.in_stock} onChange={(e) => update({ in_stock: e.target.checked || undefined })} />
              {t('categories.panel.inStock')}
            </label>
            <label>
              {t('categories.panel.sort')}
              <select value={filters.sort} onChange={(e) => update({ sort: e.target.value as SortOrder })}>
                {SORTS.map((s) => <option key={s} value={s}>{t(`categories.sort.${s}`)}</option>)}
              </select>
            </label>
            <button className="filter" type="button" onClick={() => setFilters(EMPTY_FILTERS)}>{t('categories.panel.reset')}</button>
          </form>

          {loading && <p>{t('product.loading')}</p>}
          {error && <p role="alert">{error}</p>}
          {!loading && !error && items.length === 0 && <p>{t('categories.panel.empty')}</p>}
          <div className="product-grid">
            {items.map((item) => (
              <ItemCard key={item.id} item={item} />
            ))}
          </div>
          {nextCursor && !loading && (
            <button className="filter" type="button" onClick={loadMore}>{t('categories.panel.more')}</button>
          )}
        </div>
      </section>
    </main>
  );
}
export default Categories;
