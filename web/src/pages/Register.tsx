import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context';
import { useLanguage } from '../context/languageContext';
import '../styles/site.css';

const PHONE_PATTERN = /^\+[1-9]\d{7,14}$/;

function Register() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);
  const { signUp } = useAuth();
  const { t } = useLanguage();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);

    if (password !== confirmPassword) {
      setError(t('auth.register.passwordMismatch'));
      return;
    }
    if (phoneNumber && !PHONE_PATTERN.test(phoneNumber)) {
      setError(t('auth.register.invalidPhone'));
      return;
    }

    setSubmitting(true);
    const { error } = await signUp(email, password, firstName, lastName, phoneNumber || undefined);
    setSubmitting(false);
    if (error) {
      setError(error);
      return;
    }
    setDone(true);
  }

  if (done) {
    return (
      <main>
        <section className="section auth-section">
          <div className="auth-card">
            <h1>{t('auth.register.doneTitle')}</h1>
            <p className="auth-card__subtitle">
              {t('auth.register.doneSubtitle')}
            </p>
            <Link className="btn btn--primary" to="/login" style={{ width: '100%', display: 'flex' }}>
              {t('auth.register.toLogin')}
            </Link>
          </div>
        </section>
      </main>
    );
  }

  return (
    <main>
      <section className="section auth-section">
        <div className="auth-card">
          <h1>{t('auth.register.title')}</h1>
          <p className="auth-card__subtitle">{t('auth.register.subtitle')}</p>

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="field">
              <label htmlFor="firstName">{t('auth.register.firstName')}</label>
              <input
                id="firstName"
                name="firstName"
                type="text"
                autoComplete="given-name"
                placeholder={t('auth.register.firstNamePlaceholder')}
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
              />
            </div>
            <div className="field">
              <label htmlFor="lastName">{t('auth.register.lastName')}</label>
              <input
                id="lastName"
                name="lastName"
                type="text"
                autoComplete="family-name"
                placeholder={t('auth.register.lastNamePlaceholder')}
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
              />
            </div>
            <div className="field">
              <label htmlFor="phoneNumber">{t('auth.register.phoneNumber')}</label>
              <input
                id="phoneNumber"
                name="phoneNumber"
                type="tel"
                autoComplete="tel"
                placeholder="+380501234567"
                value={phoneNumber}
                onChange={(e) => setPhoneNumber(e.target.value)}
              />
            </div>
            <div className="field">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </div>
            <div className="field">
              <label htmlFor="password">{t('auth.register.password')}</label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                placeholder={t('auth.register.passwordPlaceholder')}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={8}
              />
            </div>
            <div className="field">
              <label htmlFor="confirmPassword">{t('auth.register.confirmPassword')}</label>
              <input
                id="confirmPassword"
                name="confirmPassword"
                type="password"
                autoComplete="new-password"
                placeholder={t('auth.register.confirmPasswordPlaceholder')}
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={8}
              />
            </div>

            {error && <p className="auth-form__error">{error}</p>}

            <button className="btn btn--primary" type="submit" disabled={submitting}>
              {submitting ? t('auth.register.submitting') : t('auth.register.submit')}
            </button>
          </form>

          <p className="auth-card__footer">
            {t('auth.register.haveAccount')} <Link to="/login">{t('auth.register.signIn')}</Link>
          </p>
        </div>
      </section>
    </main>
  );
}

export default Register;
