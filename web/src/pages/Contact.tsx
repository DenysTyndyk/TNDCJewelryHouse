import '../styles/site.css';
import { useLanguage } from '../context/languageContext';
function Contact() {
    const { t } = useLanguage();
    return (

        <main>
      <section className="page-hero">
        <div className="container">
          <p className="section__eyebrow">{t('contact.eyebrow')}</p>
          <h1>{t('contact.title')}</h1>
        </div>
      </section>

      <section className="section">
        <div className="container split">
          <form className="contact-form" action="#" method="get">
            <div className="field">
              <label htmlFor="name">{t('contact.name')}</label>
              <input id="name" name="name" type="text" autoComplete="name" placeholder={t('contact.namePlaceholder')} />
            </div>
            <div className="field">
              <label htmlFor="email">{t('contact.email')}</label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
              />
            </div>
            <div className="field">
              <label htmlFor="lang">{t('contact.preferredLanguage')}</label>
              <select id="lang" name="lang">
                <option>Polski</option>
                <option>English</option>
                <option>Українська</option>
              </select>
            </div>
            <div className="field">
              <label htmlFor="message">{t('contact.message')}</label>
              <textarea id="message" name="message" placeholder={t('contact.messagePlaceholder')}></textarea>
            </div>
            <button className="btn btn--primary" type="submit">{t('contact.send')}</button>
          </form>

          <div>
            <div className="map-panel--embed" role="img" aria-label={t('contact.mapAlt')}>
              <div>
              <iframe
        src="https://www.google.com/maps/embed?pb=!1m17!1m12!1m3!1d1117.8425869586451!2d28.428206269734616!3d49.22953499821158!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m2!1m1!2zNDnCsDEzJzQ2LjMiTiAyOMKwMjUnNDMuOSJF!5e1!3m2!1suk!2spl!4v1785087674640!5m2!1suk!2spl"
        width="100%"
        height="450"
        allowFullScreen={true}
        style={{ border: 0 }}
        loading="lazy"
        referrerPolicy="no-referrer-when-downgrade"
        title="TNDC Jewelry House Location"
      ></iframe>
              </div>
            </div>
            <dl className="stat-list">
              <div>
                <dt>Email</dt>
                <dd>Tunduk_natasha@ukr.net</dd>
              </div>
              <div>
                <dt>{t('contact.hoursLabel')}</dt>
                <dd>{t('contact.hoursValue')}</dd>
              </div>
            </dl>
          </div>
        </div>
      </section>
    </main>
    )
}
export default Contact;