import '../styles/site.css';
import { Link, NavLink, useLocation } from 'react-router-dom';
import { useCart } from '../context/cartContext';
import { useAuth } from '../context/authContext';
import { useLanguage, type Language } from '../context/languageContext';
import { useEffect, useState } from 'react';

function Header() {
  const [isNavOpen, setIsNavOpen] = useState(false);
  const { cartCount } = useCart();
  const { user, changeLanguage } = useAuth();
  const { language, languages, t } = useLanguage();
  const location = useLocation();

  const navLinks: { to: string; label: string; end?: boolean }[] = [
    { to: '/', label: t('header.home'), end: true },
    { to: '/categories', label: t('header.categories') },
    { to: '/about', label: t('header.about') },
    { to: '/contact', label: t('header.contact') },
  ];

  const toggleMenu = () => setIsNavOpen((prev) => !prev);
  const closeMenu = () => setIsNavOpen(false);

  useEffect(() => {
    closeMenu();
  }, [location.pathname]);

  useEffect(() => {
    document.body.style.overflow = isNavOpen ? 'hidden' : '';
    return () => {
      document.body.style.overflow = '';
    };
  }, [isNavOpen]);

  return (
    <header className={`site-header${isNavOpen ? ' site-header--menu-open' : ''}`}>
      <div className="site-header__inner">
        <Link className="brand" to="/" aria-label="TNDC Jewelry House" onClick={closeMenu}>
          <img src="/brand/logo-dark.png" alt="TNDC Jewelry House" />
        </Link>

        <button
          className={`nav-toggle${isNavOpen ? ' nav-toggle--open' : ''}`}
          type="button"
          aria-expanded={isNavOpen}
          aria-controls="site-nav"
          aria-label={isNavOpen ? t('header.closeMenu') : t('header.openMenu')}
          onClick={toggleMenu}
        >
          <span className="nav-toggle__lines" aria-hidden="true">
            <span className="nav-toggle__bar" />
            <span className="nav-toggle__bar" />
            <span className="nav-toggle__bar" />
          </span>
          <span className="nav-toggle__label">{isNavOpen ? t('header.close') : t('header.menu')}</span>
        </button>

        <nav id="site-nav" className={`nav${isNavOpen ? ' is-open' : ''}`} aria-label="Main">
          <div className="nav__links">
            {navLinks.map(({ to, label, end }) => (
              <NavLink
                key={to}
                to={to}
                end={end}
                className={({ isActive }) => (isActive ? 'is-active' : undefined)}
                onClick={closeMenu}
              >
                {label}
              </NavLink>
            ))}
          </div>
          <NavLink
            className={({ isActive }) => `nav__cart${isActive ? ' is-active' : ''}`}
            to="/cart"
            onClick={closeMenu}
          >
            {t('header.cart')}
            <span className="nav__cart-count">{cartCount}</span>
          </NavLink>
          <NavLink
            className={({ isActive }) => `nav__account${isActive ? ' is-active' : ''}`}
            to={user ? '/account' : '/login'}
            onClick={closeMenu}
          >
            {user ? t('header.account') : t('header.login')}
          </NavLink>
          <select
            className="nav__lang"
            aria-label="Language"
            value={language}
            onChange={(e) => changeLanguage(e.target.value as Language)}
          >
            {languages.map((lang) => (
              <option key={lang} value={lang}>
                {t(`languageNames.${lang}`)}
              </option>
            ))}
          </select>
        </nav>
      </div>

      <button
        type="button"
        className={`nav-backdrop${isNavOpen ? ' is-visible' : ''}`}
        aria-hidden={!isNavOpen}
        tabIndex={isNavOpen ? 0 : -1}
        aria-label={t('header.closeMenu')}
        onClick={closeMenu}
      />
    </header>
  );
}

export default Header;
