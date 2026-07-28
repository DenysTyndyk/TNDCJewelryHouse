import '../styles/site.css';
import { useState } from 'react';
import data from '../mockProducts/data.json';
import ItemCard from '../components/ItemCard/ItemCard';
import { useLocation } from 'react-router-dom';
function Categories() {
  const location = useLocation();
  const initialCategory = location.state?.category || 'all';
  const [selectedCategory, setSelectedCategory] = useState(initialCategory);
  const items = (data as { items: any[] }).items || [];
  const filteredItems = selectedCategory === 'all' 
    ? items 
    : items.filter((item) => item.category === selectedCategory);

    return (
        <main>
      <section className="page-hero">
        <div className="container">
          <p className="section__eyebrow">Collection</p>
          <h1>Categories</h1>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="filters" role="group" aria-label="Category filters">
            <button className={`filter ${selectedCategory === 'all' ? 'is-active' : ''}`} onClick={() => setSelectedCategory('all')} type="button" aria-pressed={selectedCategory === 'all'}>All</button>
            <button className={`filter ${selectedCategory === 'Earrings' ? 'is-active' : ''}`} onClick={() => setSelectedCategory('Earrings')} type="button" aria-pressed={selectedCategory === 'earrings'}>Earrings</button>
            <button className={`filter ${selectedCategory === 'Necklaces' ? 'is-active' : ''}`} onClick={() => setSelectedCategory('Necklaces')} type="button" aria-pressed={selectedCategory === 'necklaces'}>Necklaces</button>
            <button className={`filter ${selectedCategory === 'Rings' ? 'is-active' : ''}`} onClick={() => setSelectedCategory('Rings')} type="button" aria-pressed={selectedCategory === 'rings'}>Rings</button>
            <button className={`filter ${selectedCategory === 'Bracelets' ? 'is-active' : ''}`} onClick={() => setSelectedCategory('Bracelets')} type="button" aria-pressed={selectedCategory === 'bracelets'}>Bracelets</button>
          </div>

         <div className="product-grid">
            {filteredItems.map((item) => (
              <ItemCard key={item.id} item={item} />
            ))}
          </div>
        </div>
      </section>
    </main>
    )
}
export default Categories;