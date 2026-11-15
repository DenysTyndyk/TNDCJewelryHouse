import '../styles/site.css';
import {Link} from "react-router-dom"
import { useLanguage } from '../context/languageContext';
function Footer() {
    const { t } = useLanguage();
    return (
        <footer className="site-footer">
        <div className="site-footer__inner">
          <span>{t('footer.copyright')}</span>
          <Link to="/contact">{t('footer.visit')}</Link>
            <div className="footer-socials">
    <Link to="https://www.instagram.com/tndcjewelry_house" target="_blank" rel="noopener noreferrer" aria-label="Instagram">
    <img src="/social_icons/instagram-svg.svg" alt="instagram" width="24" height="24" />
    </Link>
    <Link to="https://www.facebook.com/share/1DGr6wELGT/?mibextid=wwXIfr" target="_blank" rel="noopener noreferrer" aria-label="Facebook">
    <img src="/social_icons/facebook-svg.svg" alt="instagram" width="24" height="24" />
    </Link>
          </div>
          </div>
      </footer>
    )
}
export default Footer;