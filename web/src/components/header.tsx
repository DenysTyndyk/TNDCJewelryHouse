import '../styles/site.css';
import { Link, NavLink, useLocation } from 'react-router-dom';
import { useCart } from '../context/cartContext';
import { useEffect, useState } from 'react';

const navLinks: { to: string; label: string; end?: boolean }[] = [
  { to: '/', label: 'Home', end: true },
  { to: '/categories', label: 'Categories' },
  { to: '/about', label: 'About' },
  { to: '/contact', label: 'Contact' },
];

function Header() {
  const [isNavOpen, setIsNavOpen] = useState(false);
  const { cartCount } = useCart();
  const location = useLocation();

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
          aria-label={isNavOpen ? 'Close menu' : 'Open menu'}
          onClick={toggleMenu}
        >
          <span className="nav-toggle__lines" aria-hidden="true">
            <span className="nav-toggle__bar" />
            <span className="nav-toggle__bar" />
            <span className="nav-toggle__bar" />
          </span>
          <span className="nav-toggle__label">{isNavOpen ? 'Close' : 'Menu'}</span>
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
            Cart
            <span className="nav__cart-count">{cartCount}</span>
          </NavLink>
        </nav>
      </div>

      <button
        type="button"
        className={`nav-backdrop${isNavOpen ? ' is-visible' : ''}`}
        aria-hidden={!isNavOpen}
        tabIndex={isNavOpen ? 0 : -1}
        aria-label="Close menu"
        onClick={closeMenu}
      />
    </header>
  );
}

export default Header;
