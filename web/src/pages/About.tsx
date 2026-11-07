import '../styles/site.css';
import { useLanguage } from '../context/languageContext';
function About() {
    const { t } = useLanguage();
    return (
        <main>
      <section className="page-hero">
        <div className="container">
          <p className="section__eyebrow">{t('about.eyebrow')}</p>
          <h1>{t('about.title')}</h1>
          <p>{t('about.lead')}</p>
        </div>
      </section>

      <section className="section">
        <div className="container split">
          <div className="prose">
            <p style={{ whiteSpace: 'pre-line' }}>
              {t('about.paragraph1')}
            </p>
            <hr className="divider" />
            <p>
              {t('about.assortmentTitle')}<br/><br/>
              {t('about.assortmentText')}<br/>
              · {t('about.assortmentList1')}<br/>
              · {t('about.assortmentList2')}<br/>
              · {t('about.assortmentList3')}
            </p>
            <hr className="divider" />
            <p>
              {t('about.philosophyTitle')} <br/><br/>
              {t('about.philosophyQuote')}<br/>
              {t('about.philosophyAuthor')}
            </p>
            <p>
              {t('about.whyUsTitle')}<br/><br/>
              {t('about.whyUs1')}<br/>
              {t('about.whyUs2')}<br/>
              {t('about.whyUs3')}<br/>
              {t('about.whyUs4')}<br/>
              {t('about.whyUs5')}
            </p>

            <hr className="divider" />
          </div>

          <dl className="stat-list">
            <div>
              <dt>{t('about.statCraftLabel')}</dt>
              <dd>{t('about.statCraftValue')}</dd>
            </div>
            <div>
              <dt>{t('about.statLanguagesLabel')}</dt>
              <dd>Polski · English · Українська</dd>
            </div>
            <div>
              <dt>{t('about.statPromiseLabel')}</dt>
              <dd>{t('about.statPromiseValue')}</dd>
            </div>
          </dl>
        </div>
      </section>
    </main>
    )
}
export default About;