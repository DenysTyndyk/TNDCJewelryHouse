import { useState } from 'react';
import { Link } from 'react-router-dom';
import * as authApi from '../api/authApi';
import '../styles/site.css';

function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [done, setDone] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitting(true);
    try {
      await authApi.forgotPassword(email);
    } finally {
      setSubmitting(false);
      setDone(true);
    }
  }

  if (done) {
    return (
      <main>
        <section className="section auth-section">
          <div className="auth-card">
            <h1>Перевірте пошту</h1>
            <p className="auth-card__subtitle">
              Якщо ця email-адреса зареєстрована, на неї надіслано лист з посиланням для скидання пароля.
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
          <h1>Забули пароль?</h1>
          <p className="auth-card__subtitle">Вкажіть email — надішлемо посилання для скидання пароля</p>

          <form className="auth-form" onSubmit={handleSubmit}>
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
            <button className="btn btn--primary" type="submit" disabled={submitting}>
              {submitting ? 'Надсилаємо…' : 'Надіслати посилання'}
            </button>
          </form>

          <p className="auth-card__footer">
            Згадали пароль? <Link to="/login">Увійти</Link>
          </p>
        </div>
      </section>
    </main>
  );
}

export default ForgotPassword;
