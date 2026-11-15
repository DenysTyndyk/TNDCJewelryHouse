import { Link } from 'react-router-dom';
import { useLanguage } from '../context/languageContext';
import { useTracking } from '../context/trackingContext';

function ConsentBanner() {
  const { consent, ready, setConsent } = useTracking();
  const { t } = useLanguage();
  if (!ready || consent !== null) return null;

  return (
    <div className="consent-banner" role="region" aria-label={t('consent.title')}>
      <p>
        {t('consent.text')} <Link to="/privacy">{t('consent.privacyLink')}</Link>
      </p>
      <div className="consent-banner__actions">
        {/* Same style for both: refusing must be as easy as agreeing (EDPB guidelines 05/2020). */}
        <button type="button" className="btn btn--ghost" onClick={() => setConsent('denied')}>{t('consent.decline')}</button>
        <button type="button" className="btn btn--ghost" onClick={() => setConsent('granted')}>{t('consent.accept')}</button>
      </div>
    </div>
  );
}

export default ConsentBanner;
