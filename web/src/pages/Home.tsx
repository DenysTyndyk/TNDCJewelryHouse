import '../styles/site.css';
import { useState, useEffect } from 'react';
import ItemCard from '../components/ItemCard/ItemCard';
import data from '../mockProducts/data.json';
import {Link} from 'react-router-dom'
import type { Item } from '../types';
function Home() {
  const [newArrivals, setNewArrivals] = useState<Item[]>([]);
  useEffect(() => {
    setNewArrivals(data.items.slice(0, 3) as Item[]);
  }, []);
    return (
        <main>
      <section className="hero">
        <div className="hero__media" aria-hidden="true">
          <div className="hero__glow"></div>
          <img className="hero__ornament" src="/brand/moodboard.png" alt="" />
        </div>
        <div className="hero__content">
          <p className="hero__brand reveal">TNDC Jewelry House</p>
          <h1 className="hero__title reveal reveal-delay">Quiet luxury, family craft.</h1>
          <p className="hero__text reveal reveal-delay-2">
            Hand-finished pieces in gold and malachite — made for everyday elegance and lasting
            memory.
          </p>
          <div className="btn-group reveal reveal-delay-2">
            <Link className="btn btn--primary" to="/categories">Explore collection</Link>
            <Link className="btn btn--ghost" to="#new">New arrivals</Link>
          </div>
        </div>
      </section>

      <section className="section" id="new">
        <div className="container">
          <p className="section__eyebrow">Aktualne nowości</p>
          <h2 className="section__title">New arrivals</h2>
          <p className="section__lead">
            Fresh from the atelier — clover motifs, soft gold, and deep green stone.
          </p>
          <hr className="divider" />

          <div className="product-grid">
            {newArrivals.map((item) => (
              <ItemCard key={item.id} item={item} />
            ))}
          </div>
        </div>
      </section>

      <section className="section" style={{ paddingTop: 0 }}>
        <div className="container">
          <p className="section__eyebrow">Browse</p>
          <h2 className="section__title">Categories</h2>
          <div className="category-row">
            <Link className="category-tile" to="/categories" state={{ category: 'Earrings' }}> <span>Earrings</span></Link>
            <Link className="category-tile" to="/categories" state={{ category: 'Necklaces' }}> <span>Necklaces</span></Link>
            <Link className="category-tile" to="/categories" state={{ category: 'Rings' }}> <span>Rings</span></Link>
            <Link className="category-tile" to="/categories" state={{ category: 'Bracelets' }}> <span>Bracelets</span></Link>
          </div>
        </div>
      </section>
    </main>
    )
}
export default Home;