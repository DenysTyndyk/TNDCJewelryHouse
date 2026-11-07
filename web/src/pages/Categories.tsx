import '../styles/site.css';
import { useState } from 'react';
import data from '../mockProducts/data.json';
import ItemCard from '../components/ItemCard/ItemCard';
import { useLocation } from 'react-router-dom';
import type { Item } from '../types';
import { useLanguage } from '../context/languageContext';
function Categories() {
  const { t } = useLanguage();
  const location = useLocation();
  const initialCategory = location.state?.category || 'all';
  const [selectedCategory, setSelectedCategory] = useState(initialCategory);
  const items = (data as { items: Item[] }).items || [];
  const filteredItems = selectedCategory === 'all' 
    ? items 
    : items.filter((item: Item) => item.category === selectedCategory);

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
            <button className={`filter ${selectedCategory === 'all' ? 'is-active' : ''}`} onClick={() => setSelectedCategory('all')} type="button" aria-pressed={selectedCategory === 'all'}>{t('categories.filterAll')}</button>
            <button className={`filter ${selectedCategory === 'Earrings' ? 'is-active' : ''}`} onClick={() => setSelectedCategory('Earrings')} type="button" aria-pressed={selectedCategory === 'earrings'}>{t('categories.filters.Earrings')}</button>
            <button className={`filter ${selectedCategory === 'Necklaces' ? 'is-active' : ''}`} onClick={() => setSelectedCategory('Necklaces')} type="button" aria-pressed={selectedCategory === 'necklaces'}>{t('categories.filters.Necklaces')}</button>
            <button className={`filter ${selectedCategory === 'Rings' ? 'is-active' : ''}`} onClick={() => setSelectedCategory('Rings')} type="button" aria-pressed={selectedCategory === 'rings'}>{t('categories.filters.Rings')}</button>
            <button className={`filter ${selectedCategory === 'Bracelets' ? 'is-active' : ''}`} onClick={() => setSelectedCategory('Bracelets')} type="button" aria-pressed={selectedCategory === 'bracelets'}>{t('categories.filters.Bracelets')}</button>
          </div>

         <div className="product-grid">
            {filteredItems.map((item: Item) => (
              <ItemCard key={item.id} item={item} />
            ))}
          </div>
        </div>
      </section>
    </main>
    )
}
export default Categories;