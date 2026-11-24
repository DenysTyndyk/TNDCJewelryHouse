import { useEffect, useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { suggestProducts, type Suggestion } from '../api/recoApi';
import { useLanguage } from '../context/languageContext';
import type { MetalColor, MetalType, ProductFilters, SortOrder } from '../types';

export type PanelFilters = Pick<ProductFilters, 'metal' | 'color' | 'fineness' | 'gemstone' | 'price_max' | 'in_stock' | 'sort'>;

const METALS: MetalType[] = ['Gold', 'Silver', 'Platinum'];
const COLORS: MetalColor[] = ['White', 'Yellow', 'Rose', 'Bicolor'];
const FINENESS = [375, 500, 585, 750, 875, 925, 958, 999]; // same list as the DB check constraint
// shortcut: same slugs as the seed and the `gemstones.*` i18n keys; switch to a /gemstones endpoint if admins add stones
const GEMSTONES = ['diamond', 'sapphire', 'ruby', 'emerald', 'amethyst', 'topaz', 'pearl', 'cubic_zirconia'];
const SORTS: SortOrder[] = ['recommended', 'newest', 'price_asc', 'price_desc', 'popular'];

type Props = {
  filters: PanelFilters;
  onChange: (patch: Partial<PanelFilters>) => void;
  onReset: () => void;
  showSort?: boolean; // search results are ordered by relevance, so the sort select is hidden there
  query: string; // the query the page currently shows results for
  onSearch: (q: string) => void; // '' clears the search
};

const SEARCH_DEBOUNCE_MS = 500;
const SUGGEST_DEBOUNCE_MS = 250; // shorter than the grid search: suggestions should appear while typing
const SUGGEST_MIN_CHARS = 2;     // the API rejects shorter queries

function CatalogFilters({ filters, onChange, onReset, showSort = true, query, onSearch }: Props) {
  const { t, language } = useLanguage();
  const [text, setText] = useState(query);
  const [hits, setHits] = useState<Suggestion[]>([]);

  // Name suggestions: abort keeps a slow, stale answer from overwriting a fresh one.
  useEffect(() => {
    const q = text.trim();
    if (q.length < SUGGEST_MIN_CHARS) { setHits([]); return; }
    const ctrl = new AbortController();
    const timer = setTimeout(() => {
      suggestProducts(q, language, ctrl.signal).then(setHits).catch(() => { /* suggestions are optional */ });
    }, SUGGEST_DEBOUNCE_MS);
    return () => { clearTimeout(timer); ctrl.abort(); };
  }, [text, language]);

  // Live search: fire once typing pauses, so "каблучка" is one request (and one search_queries row), not eight.
  // A single character is skipped: it matches nothing lexically and only costs an embedder call.
  useEffect(() => {
    const q = text.trim();
    if (q === query || q.length === 1) return;
    const timer = setTimeout(() => onSearch(q), SEARCH_DEBOUNCE_MS);
    return () => clearTimeout(timer);
  }, [text, query]);

  // Enter searches immediately instead of waiting for the debounce.
  const submit = (e: FormEvent) => {
    e.preventDefault();
    const q = text.trim();
    setHits([]);
    if (q !== query) onSearch(q);
  };

  return (
    <form className="catalog-filters" aria-label="Product filters" role="search" onSubmit={submit}>
      <div className="catalog-filters__search">
        <label>
          {t('search.label')}
          <input
            type="search"
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={(e) => { if (e.key === 'Escape') setHits([]); }}
            placeholder={t('search.placeholder')}
            maxLength={200}
            autoComplete="off"
          />
        </label>
        {hits.length > 0 && (
          <ul className="catalog-filters__suggestions">
            {hits.map((h) => (
              <li key={h.slug}><Link to={`/products/${h.slug}`}>{h.name}</Link></li>
            ))}
          </ul>
        )}
      </div>
      <label>
        {t('product.specs.metal')}
        <select value={filters.metal ?? ''} onChange={(e) => onChange({ metal: (e.target.value || undefined) as MetalType | undefined })}>
          <option value="">{t('categories.panel.any')}</option>
          {METALS.map((m) => <option key={m} value={m}>{t(`product.metal.${m}`)}</option>)}
        </select>
      </label>
      <label>
        {t('product.specs.color')}
        <select value={filters.color ?? ''} onChange={(e) => onChange({ color: (e.target.value || undefined) as MetalColor | undefined })}>
          <option value="">{t('categories.panel.any')}</option>
          {COLORS.map((c) => <option key={c} value={c}>{t(`product.color.${c}`)}</option>)}
        </select>
      </label>
      <label>
        {t('product.specs.fineness')}
        <select value={filters.fineness ?? ''} onChange={(e) => onChange({ fineness: e.target.value ? Number(e.target.value) : undefined })}>
          <option value="">{t('categories.panel.any')}</option>
          {FINENESS.map((f) => <option key={f} value={f}>{f}</option>)}
        </select>
      </label>
      <label>
        {t('product.specs.gemstones')}
        <select value={filters.gemstone ?? ''} onChange={(e) => onChange({ gemstone: e.target.value || undefined })}>
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
          onChange={(e) => onChange({ price_max: e.target.value ? Number(e.target.value) : undefined })}
        />
      </label>
      <label className="catalog-filters__check">
        <input type="checkbox" checked={!!filters.in_stock} onChange={(e) => onChange({ in_stock: e.target.checked || undefined })} />
        {t('categories.panel.inStock')}
      </label>
      {showSort && (
        <label>
          {t('categories.panel.sort')}
          <select value={filters.sort} onChange={(e) => onChange({ sort: e.target.value as SortOrder })}>
            {SORTS.map((s) => <option key={s} value={s}>{t(`categories.sort.${s}`)}</option>)}
          </select>
        </label>
      )}
      <button className="filter" type="button" onClick={onReset}>{t('categories.panel.reset')}</button>
    </form>
  );
}

export default CatalogFilters;
