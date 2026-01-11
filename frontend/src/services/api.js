/**
 * API сервис для работы с backend
 */

const API_BASE_URL = 'http://localhost:8000';

/**
 * Получить текущее состояние очереди
 */
export const getState = async () => {
  const response = await fetch(`${API_BASE_URL}/api/state`);
  if (!response.ok) {
    throw new Error('Failed to fetch state');
  }
  return response.json();
};

/**
 * Назначить исполнителя
 */
export const assignCard = async (data) => {
  const response = await fetch(`${API_BASE_URL}/api/assign`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  if (!response.ok) {
    throw new Error('Failed to assign card');
  }
  return response.json();
};

/**
 * Пропустить письмо
 */
export const skipCard = async (cardId) => {
  const response = await fetch(`${API_BASE_URL}/api/skip`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ card_id: cardId }),
  });
  if (!response.ok) {
    throw new Error('Failed to skip card');
  }
  return response.json();
};

/**
 * Отменить последнее действие
 */
export const undoLastAction = async () => {
  const response = await fetch(`${API_BASE_URL}/api/undo`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({}),
  });
  if (!response.ok) {
    throw new Error('Failed to undo');
  }
  return response.json();
};

/**
 * Получить URL файла
 */
export const getFileUrl = (incomingNo, filename) => {
  return `${API_BASE_URL}/files/${incomingNo}/${filename}`;
};
