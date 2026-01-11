import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Stack from './components/Stack';
import FileTabs from './components/FileTabs';
import AssigneeButtons from './components/AssigneeButtons';
import Login from './components/Login';
import { getState, assignCard, skipCard, undoLastAction, verifyToken, logout } from './services/api';
import './App.css';

// Импортируем список исполнителей
import employeesData from './employees.json';

function App() {
  // Состояние авторизации
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAuthLoading, setIsAuthLoading] = useState(true);
  const [username, setUsername] = useState('');

  // Состояние приложения
  const [state, setState] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  // Режимы работы
  const [multiMode, setMultiMode] = useState(false);
  const [selectedEmployees, setSelectedEmployees] = useState([]);
  const [commentText, setCommentText] = useState('');
  const [showCommentModal, setShowCommentModal] = useState(false);

  // Проверяем токен при загрузке
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('authToken');
      const savedUsername = localStorage.getItem('username');
      
      if (token && savedUsername) {
        // Проверяем что токен валидный
        const result = await verifyToken();
        if (result && result.username) {
          setIsAuthenticated(true);
          setUsername(result.username);
          console.log('[APP] Authenticated as:', result.username);
        } else {
          // Токен невалидный - чистим
          localStorage.removeItem('authToken');
          localStorage.removeItem('username');
        }
      }
      
      setIsAuthLoading(false);
    };

    checkAuth();
  }, []);

  // Загрузка состояния при старте (только если авторизован)
  useEffect(() => {
    if (!isAuthenticated) return;
    
    loadState();
    
    // Автообновление каждые 5 секунд
    const interval = setInterval(() => {
      loadState();
    }, 5000);
    
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isAuthenticated]);

  // Обработчик успешного логина
  const handleLoginSuccess = (token, username) => {
    setIsAuthenticated(true);
    setUsername(username);
    console.log('[APP] Login success:', username);
  };

  // Обработчик выхода
  const handleLogout = async () => {
    await logout();
    setIsAuthenticated(false);
    setUsername('');
    setState(null);
    console.log('[APP] Logged out');
  };

  // Функция загрузки состояния
  const loadState = async () => {
    if (!isAuthenticated) return;
    
    try {
      setLoading(true);
      const data = await getState();
      setState(data);
      setError(null);
    } catch (err) {
      console.error('Failed to load state:', err);
      setError('Не удалось загрузить данные');
    } finally {
      setLoading(false);
    }
  };

  // Назначить исполнителя
  const handleAssign = async (userIds) => {
    if (!state?.current_card) return;
    
    console.log('[DEBUG] handleAssign called with userIds:', userIds);
    console.log('[DEBUG] userIds type:', typeof userIds);
    console.log('[DEBUG] userIds is array:', Array.isArray(userIds));
    console.log('[DEBUG] userIds[0]:', userIds[0]);
    
    try {
      setLoading(true);
      
      const data = {
        card_id: state.current_card.card_id,
        owner_id: userIds[0],
        co_owner_ids: userIds.slice(1),
        comment_text: commentText,
        multi: userIds.length > 1,
      };
      
      console.log('[DEBUG] Sending data to backend:', data);
      console.log('[DEBUG] owner_id:', data.owner_id);
      console.log('[DEBUG] owner_id type:', typeof data.owner_id);
      
      const newState = await assignCard(data);
      setState(newState);
      
      // Сброс состояния
      setMultiMode(false);
      setSelectedEmployees([]);
      setCommentText('');
      setShowCommentModal(false);
      setError(null);
      
      console.log('[DEBUG] Assignment successful!');
    } catch (err) {
      console.error('[ERROR] Failed to assign:', err);
      setError('Не удалось назначить исполнителя');
    } finally {
      setLoading(false);
    }
  };

  // Пропустить письмо
  const handleSkip = async () => {
    if (!state?.current_card) return;
    
    try {
      setLoading(true);
      const newState = await skipCard(state.current_card.card_id);
      setState(newState);
      setError(null);
    } catch (err) {
      console.error('Failed to skip:', err);
      setError('Не удалось пропустить письмо');
    } finally {
      setLoading(false);
    }
  };

  // Отменить последнее действие
  const handleUndo = async () => {
    try {
      setLoading(true);
      const newState = await undoLastAction();
      setState(newState);
      setError(null);
    } catch (err) {
      console.error('Failed to undo:', err);
      setError('Не удалось отменить действие');
    } finally {
      setLoading(false);
    }
  };

  // Обработка выбора исполнителя
  const handleEmployeeSelect = (userIds) => {
    console.log('[DEBUG] handleEmployeeSelect called with:', userIds);
    
    if (multiMode) {
      setSelectedEmployees(userIds);
    } else {
      // В обычном режиме сразу назначаем
      handleAssign(userIds);
    }
  };

  // Подтверждение назначения в мульти-режиме
  const handleConfirmMulti = () => {
    console.log('[DEBUG] handleConfirmMulti called, selectedEmployees:', selectedEmployees);
    
    if (selectedEmployees.length > 0) {
      handleAssign(selectedEmployees);
    }
  };

  // Показываем загрузку проверки авторизации
  if (isAuthLoading) {
    return (
      <div className="app-loading">
        <div className="spinner" />
        <p>Загрузка...</p>
      </div>
    );
  }

  // Если не авторизован - показываем логин
  if (!isAuthenticated) {
    return (
      <div className="app">
        <Login onLoginSuccess={handleLoginSuccess} />
      </div>
    );
  }

  // Если загружаем данные первый раз
  if (loading && !state) {
    return (
      <div className="app-loading">
        <div className="spinner" />
        <p>Загрузка данных...</p>
      </div>
    );
  }

  // Главный экран приложения (авторизован)
  return (
    <div className="app">
      {/* Заголовок с кнопкой выхода */}
      <header className="app-header">
        <h1>Распределение входящих писем</h1>
        <div className="header-info">
          <div className="user-info">
            <span className="user-icon">👤</span>
            <span className="username">{username}</span>
          </div>
          <button onClick={handleLogout} className="logout-button">
            Выход
          </button>
        </div>
        {error && <div className="error-message">{error}</div>}
      </header>

      {/* Основной контент */}
      <div className="app-content">
        {/* Левая панель - стопки */}
        <aside className="stacks-panel">
          <Stack 
            title="Очередь" 
            count={state?.queue_count || 0} 
            position="left"
          />
          <Stack 
            title="Назначить исполнителя" 
            count={state?.assigned_session_count || 0} 
            position="left"
          />
        </aside>

        {/* Центральная панель - просмотр письма */}
        <main className="main-panel">
          {/* Кнопки действий */}
          <div className="action-buttons">
            <button 
              className="btn btn-secondary"
              onClick={handleSkip}
              disabled={!state?.current_card || loading}
            >
              Пропустить
            </button>
            <button 
              className="btn btn-secondary"
              onClick={() => setShowCommentModal(true)}
              disabled={!state?.current_card || loading}
            >
              Комментарий
            </button>
            <button 
              className={`btn btn-secondary ${multiMode ? 'active' : ''}`}
              onClick={() => {
                setMultiMode(!multiMode);
                setSelectedEmployees([]);
              }}
              disabled={!state?.current_card || loading}
            >
              Несколько исполнителей
            </button>
            <button 
              className="btn btn-danger"
              onClick={handleUndo}
              disabled={loading}
            >
              Отмена
            </button>
            
            {multiMode && selectedEmployees.length > 0 && (
              <button 
                className="btn btn-primary"
                onClick={handleConfirmMulti}
                disabled={loading}
              >
                Назначить выбранных ({selectedEmployees.length})
              </button>
            )}
          </div>

          {/* Просмотр текущего письма */}
          <div className="letter-viewer">
            {state?.current_card ? (
              <AnimatePresence mode="wait">
                <motion.div
                  key={state.current_card.card_id}
                  initial={{ opacity: 0, x: 100 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -100 }}
                  transition={{ duration: 0.3 }}
                  className="letter-content"
                >
                  <div className="letter-header">
                    <h2>{state.current_card.title}</h2>
                    <span className="letter-number">
                      № {state.current_card.incoming_no}
                    </span>
                  </div>
                  
                  <FileTabs 
                    files={state.current_card.files}
                    incomingNo={state.current_card.incoming_no}
                    cardId={state.current_card.card_id}
                  />
                </motion.div>
              </AnimatePresence>
            ) : (
              <div className="no-letters">
                <p>📭 Нет писем в очереди</p>
              </div>
            )}
          </div>
        </main>

        {/* Правая панель - исполнители */}
        <aside className="assignees-panel">
          <AssigneeButtons 
            employees={employeesData}
            onSelect={handleEmployeeSelect}
            selectedIds={selectedEmployees}
            multiMode={multiMode}
          />
        </aside>
      </div>

      {/* Модальное окно комментария */}
      {showCommentModal && (
        <div className="modal-overlay" onClick={() => setShowCommentModal(false)}>
          <div className="modal" onClick={(e) => e.stopPropagation()}>
            <h3>Резолюция</h3>
            <textarea
              value={commentText}
              onChange={(e) => setCommentText(e.target.value)}
              placeholder="Введите текст резолюции..."
              rows={6}
              autoFocus
            />
            <div className="modal-buttons">
              <button 
                className="btn btn-secondary"
                onClick={() => setShowCommentModal(false)}
              >
                Отмена
              </button>
              <button 
                className="btn btn-primary"
                onClick={() => setShowCommentModal(false)}
              >
                Сохранить
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;