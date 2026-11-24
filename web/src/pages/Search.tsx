import '../styles/site.css';
import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import ItemCard from '../components/ItemCard/ItemCard';
import CatalogFilters, { type PanelFilters } from '../components/CatalogFilters';
import { toItem } from '../api/catalogApi';
import { searchProducts } from '../api/searchApi';
import { useAuth } from '../context/authContext';
import { useLanguage } from '../context/languageContext';
import { useTracking } from '../context/trackingContext';
import type { Item, SearchMode } from '../types';

const MODES: SearchMode[] = ['hybrid', 'semantic', 'lexical'];
const NO_FILTERS: PanelFilters = {};
// shortcut: one request with the API maximum instead of "show more"; each extra page would log
// one more search_queries row for the same query. Switch to offset paging if results exceed 100.
const PAGE_SIZE = 100;

function Search() {
  const { t, language } = useLanguage();
  const { accessToken } = useAuth();
  const { track, canTrack } = useTracking();
  const [searchParams, setSearchParams] = useSearchParams();
  const q = (searchParams.get('q') ?? '').trim();
  // The mode switch is a dev-only demo tool; the production build always asks for hybrid.
  const requested = searchParams.get('mode') as SearchMode | null;
  const mode: SearchMode = import.meta.env.DEV && requested && MODES.includes(requested) ? requested : 'hybrid';

  const [filters, setFilters] = useState<PanelFilters>(NO_FILTERS);
  const [items, setItems] = useState<Item[]>([]);
  const [total, setTotal] = useState(0);
  const [modeUsed, setModeUsed] = useState<SearchMode | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!q) {
      setItems([]);
      setTotal(0);
      setModeUsed(null);
      return;
    }
    let active = true; // ignore responses that arrive after the query/filters changed again
    setLoading(true);
    setError(null);
    // accessToken/canTrack are read but not dependencies: logging in must not re-run (and re-log) the search.
    searchProducts({ q, mode, limit: PAGE_SIZE, locale: language, ...filters }, accessToken, canTrack)
      .then((res) => {
        if (!active) return;
        setItems(res.items.map(toItem));
        setTotal(res.total);
        setModeUsed(res.mode_used);
      })
      .catch(() => active && setError(t('product.loadError')))
      .finally(() => active && setLoading(false));
    return () => { active = false; };
  }, [q, mode, filters, language]);

  // A click on a result: Search event with the product and its position (track() is a no-op without consent).
  const openResult = (productId: number, position: number) =>
    track({ event_type: 'Search', product_id: productId, metadata: { query: q, mode: modeUsed ?? mode, position } });

  const update = (patch: Partial<PanelFilters>) => setFilters((prev) => ({ ...prev, ...patch }));

  // Typing updates ?q= in place (replace: no history entry per pause); the dev ?mode= is kept.
  const changeQuery = (next: string) => {
    const params = new URLSearchParams(searchParams);
    if (next) params.set('q', next);
    else params.delete('q');
    setSearchParams(params, { replace: true });
  };

  return (
    <main>
      <section className="page-hero">
        <div className="container">
          <p className="section__eyebrow">{t('search.eyebrow')}</p>
          <h1>{q ? `«${q}»` : t('search.title')}</h1>
          {modeUsed && (
            <p className="search-meta">
              {t('search.found')}: {total} · {t('search.mode')}: {t(`search.modes.${modeUsed}`)}
            </p>
          )}
          {import.meta.env.DEV && q && (
            <label className="search-meta">
              {t('search.mode')} (dev){' '}
              <select value={mode} onChange={(e) => setSearchParams({ q, mode: e.target.value })}>
                {MODES.map((m) => <option key={m} value={m}>{t(`search.modes.${m}`)}</option>)}
              </select>
            </label>
          )}
        </div>
      </section>

      <section className="section">
        <div className="container">
          <CatalogFilters filters={filters} onChange={update} onReset={() => setFilters(NO_FILTERS)} showSort={false} query={q} onSearch={changeQuery} />

          {!q && <p>{t('search.prompt')}</p>}
          {loading && <p>{t('product.loading')}</p>}
          {error && <p role="alert">{error}</p>}
          {q && !loading && !error && items.length === 0 && <p>{t('search.empty')}</p>}
          <div className="product-grid">
            {items.map((item, index) => (
              <ItemCard key={item.id} item={item} onOpen={() => openResult(item.id, index + 1)} />
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}

export default Search;
