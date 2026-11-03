import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context';
import '../styles/site.css';

function Register() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);
  const { signUp } = useAuth();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    setError(null);
    const { error } = await signUp(email, password, firstName, lastName);
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
            <h1>Перевірте пошту</h1>
            <p className="auth-card__subtitle">
              Якщо ця email-адреса ще не зареєстрована, на неї надіслано лист з посиланням для
              підтвердження акаунта. Перейдіть за ним, а тоді увійдіть.
            </p>
            <Link className="btn btn--primary" to="/login" style={{ width: '100%', display: 'flex' }}>
              До сторінки входу
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
          <h1>Реєстрація</h1>
          <p className="auth-card__subtitle">Створіть акаунт TNDC Jewelry House</p>

          <form className="auth-form" onSubmit={handleSubmit}>
            <div className="field">
              <label htmlFor="firstName">Ім'я</label>
              <input
                id="firstName"
                name="firstName"
                type="text"
                autoComplete="given-name"
                placeholder="Ваше ім'я"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
              />
            </div>
            <div className="field">
              <label htmlFor="lastName">Прізвище</label>
              <input
                id="lastName"
                name="lastName"
                type="text"
                autoComplete="family-name"
                placeholder="Ваше прізвище"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
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
              <label htmlFor="password">Пароль</label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                placeholder="Мінімум 8 символів"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={8}
              />
            </div>

            {error && <p className="auth-form__error">{error}</p>}

            <button className="btn btn--primary" type="submit" disabled={submitting}>
              {submitting ? 'Реєструємо…' : 'Зареєструватись'}
            </button>
          </form>

          <p className="auth-card__footer">
            Вже є акаунт? <Link to="/login">Увійти</Link>
          </p>
        </div>
      </section>
    </main>
  );
}

export default Register;
