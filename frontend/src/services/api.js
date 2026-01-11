// API клиент для работы с backend

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Получить токен из localStorage
const getAuthToken = () => {
  return localStorage.getItem('authToken');
};

// Общая функция для запросов с авторизацией
const fetchWithAuth = async (url, options = {}) => {
  const token = getAuthToken();
  
  const headers = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  
  // Добавляем токен если есть
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  
  const response = await fetch(url, {
    ...options,
    headers,
  });
  
  // Если 401 - токен невалидный, разлогиниваем
  if (response.status === 401) {
    localStorage.removeItem('authToken');
    localStorage.removeItem('username');
    window.location.reload(); // Перезагружаем страницу -> покажется логин
    throw new Error('Unauthorized');
  }
  
  return response;
};

// Получить текущее состояние очереди
export const getState = async () => {
  const response = await fetchWithAuth(`${API_URL}/api/state`);
  return response.json();
};

// Назначить исполнителя
export const assignCard = async (data) => {
  const response = await fetchWithAuth(`${API_URL}/api/assign`, {
    method: 'POST',
    body: JSON.stringify(data),
  });
  return response.json();
};

// Пропустить карточку
export const skipCard = async (cardId) => {
  const response = await fetchWithAuth(`${API_URL}/api/skip`, {
    method: 'POST',
    body: JSON.stringify({
      card_id: cardId,
    }),
  });
  return response.json();
};

// Отменить последнее действие
export const undoLastAction = async () => {
  const response = await fetchWithAuth(`${API_URL}/api/undo`, {
    method: 'POST',
  });
  return response.json();
};

// Получить URL файла
export const getFileUrl = (incomingNo, filename) => {
  const token = getAuthToken();
  // Добавляем токен в URL
  return `${API_URL}/files/${incomingNo}/${filename}?token=${token}`;
};

// Проверить токен
export const verifyToken = async () => {
  try {
    const response = await fetchWithAuth(`${API_URL}/api/verify`);
    return response.json();
  } catch (err) {
    return null;
  }
};

// Выйти из системы
export const logout = async () => {
  try {
    await fetchWithAuth(`${API_URL}/api/logout`, { method: 'POST' });
  } catch (err) {
    console.error('[API] Logout error:', err);
  } finally {
    localStorage.removeItem('authToken');
    localStorage.removeItem('username');
  }
};