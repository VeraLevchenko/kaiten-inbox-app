import React, { useState } from 'react';
import './Login.css';

const Login = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8010'}/api/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok && data.success) {
        localStorage.setItem('authToken', data.token);
        localStorage.setItem('username', data.username);
        console.log('[LOGIN] Success:', data.username);
        onLoginSuccess(data.token, data.username);
      } else {
        setError(data.detail || 'Ошибка авторизации');
      }
    } catch (err) {
      console.error('[LOGIN] Error:', err);
      setError('Ошибка подключения к серверу');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-card">
        <div className="login-brand">
          <div className="login-brand-mark">
            <svg viewBox="0 0 24 24">
              <path d="M4 4h16v2H4V4zm0 4h16v2H4V8zm0 4h10v2H4v-2zm0 4h7v2H4v-2z"/>
              <path d="M17 14l-1.5 1.5L17 17l4-4-4-4-1.5 1.5L17 12" strokeWidth="0" fill="white" opacity="0.85"/>
            </svg>
          </div>
          <h1 className="login-title">Входящие письма</h1>
          <p className="login-subtitle">Система распределения документов</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Логин</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Введите логин"
              disabled={loading}
              autoFocus
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Пароль</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Введите пароль"
              disabled={loading}
              required
            />
          </div>

          {error && (
            <div className="error-message">{error}</div>
          )}

          <button
            type="submit"
            className="login-button"
            disabled={loading}
          >
            {loading ? 'Вход...' : 'Войти'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default Login;
