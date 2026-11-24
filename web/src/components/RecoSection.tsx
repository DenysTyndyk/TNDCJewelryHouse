import '../styles/site.css';
import { useEffect, useState } from 'react';
import ItemCard from './ItemCard/ItemCard';
import { getRecommendations, type RecoResponse } from '../api/recoApi';
import { toItem } from '../api/catalogApi';
import { useAuth } from '../context/authContext';
import { useLanguage } from '../context/languageContext';
import { useTracking } from '../context/trackingContext';

// One grid row (.product-grid has 3 columns): skeleton and result have the same count,
// so swapping one for the other never changes the section height.
const VISIBLE = 3;

type Props = {
  title: string;
  path: string;      // e.g. "for-you", "similar/12"
  section: string;   // logged with the click, to compare sections in analytics
  exclude?: number;  // current product on its own page
};

function SkeletonCard() {
  // Same classes as ItemCard, so the placeholder takes exactly the card's box.
  return (
    <article className="product product--skeleton" aria-hidden="true">
      <div className="product__media" />
      <div className="product__meta">
        <span className="product__cat">&nbsp;</span>
        <h3 className="product__name">&nbsp;</h3>
        <div className="product__price-row"><span className="product__price">&nbsp;</span></div>
      </div>
    </article>
  );
}

export default function RecoSection({ title, path, section, exclude }: Props) {
  const { language } = useLanguage();
  const { accessToken } = useAuth();
  const { ready, canTrack, track } = useTracking();
  const [data, setData] = useState<RecoResponse | null>(null);

  useEffect(() => {
    if (!ready) return; // wait for auth, otherwise the guest list flashes before the user's one
    let active = true;
    setData(null);
    getRecommendations(path, { locale: language }, accessToken, canTrack)
      .then((r) => active && setData(r))
      .catch(() => active && setData({ algorithm: 'popularity', items: [] }));
    return () => { active = false; };
  }, [path, language, accessToken, canTrack, ready]);

  const items = data?.items.filter((p) => p.id !== exclude).slice(0, VISIBLE);
  // Sections sit at the bottom of the page, so collapsing an empty one moves nothing above it.
  if (items && items.length === 0) return null;

  return (
    <section className="section" aria-busy={!items} aria-label={title}>
      <div className="container">
        <h2 className="section__title">{title}</h2>
        <div className="product-grid">
          {!data || !items
            ? Array.from({ length: VISIBLE }, (_, i) => <SkeletonCard key={i} />)
            : items.map((p) => (
                <ItemCard
                  key={p.id}
                  item={toItem(p)}
                  onOpen={() => track({
                    event_type: 'ClickRecommendation',
                    product_id: p.id,
                    source: data.algorithm,
                    metadata: { section },
                  })}
                />
              ))}
        </div>
      </div>
    </section>
  );
}
