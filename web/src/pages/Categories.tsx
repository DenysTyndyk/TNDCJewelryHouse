import '../styles/site.css';
import { useEffect, useState } from 'react';
import { useLocation } from 'react-router-dom';
import ItemCard from '../components/ItemCard/ItemCard';
import CatalogFilters, { type PanelFilters } from '../components/CatalogFilters';
import { listCategories, listProducts, toItem } from '../api/catalogApi';
import { searchProducts } from '../api/searchApi';
import type { CategoryNode, Item, ProductPage } from '../types';
import { useAuth } from '../context/authContext';
import { useLanguage } from '../context/languageContext';
import { useTracking } from '../context/trackingContext';

const EMPTY_FILTERS: PanelFilters = { sort: 'newest' };

function Categories() {
  const { t, language } = useLanguage();
  const { track, canTrack } = useTracking();
  const { accessToken } = useAuth();
  const location = useLocation();
  const [q, setQ] = useState('');
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
    // With a query the grid shows ranked search results (same filters and category); sort/cursor do not apply.
    const request: Promise<ProductPage> = q
      ? searchProducts({ ...query, q, limit: 100 }, accessToken, canTrack).then((res) => ({ items: res.items, next_cursor: null }))
      : listProducts(query);
    request
      .then((page) => {
        if (!active) return;
        setItems(page.items.map(toItem));
        setNextCursor(page.next_cursor ?? null);
      })
      .catch(() => active && setError(t('product.loadError')))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [selectedCategory, filters, language, q]);

  // CategoryView: once a concrete category is selected and the category list (with ids) has loaded.
  useEffect(() => {
    if (!canTrack || selectedCategory === 'all') return;
    const category = categories.flatMap((c) => [c, ...c.children]).find((c) => c.slug === selectedCategory);
    if (category) track({ event_type: 'CategoryView', category_id: category.id });
  }, [selectedCategory, categories, canTrack]);

  // FilterApply: debounced, so typing "1500" in the price field is one event, not four.
  useEffect(() => {
    if (!canTrack || filters === EMPTY_FILTERS) return;
    const timer = setTimeout(() => {
      const metadata = Object.fromEntries(
        Object.entries(filters).filter(([, v]) => v !== undefined),
      ) as Record<string, string | number | boolean>;
      track({ event_type: 'FilterApply', metadata });
    }, 800);
    return () => clearTimeout(timer);
  }, [filters, canTrack]);

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

          <CatalogFilters
            filters={filters}
            onChange={update}
            onReset={() => setFilters(EMPTY_FILTERS)}
            showSort={!q}
            query={q}
            onSearch={setQ}
          />

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
