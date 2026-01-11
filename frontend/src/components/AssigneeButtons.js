import React from 'react';
import './AssigneeButtons.css';

/**
 * Компонент списка исполнителей (справа)
 * Отображает все кнопки исполнителей вертикально
 */
const AssigneeButtons = ({ employees, onSelect, selectedIds = [], multiMode = false }) => {
  const handleClick = (userId) => {
    if (multiMode) {
      // В режиме мультивыбора переключаем выбор
      if (selectedIds.includes(userId)) {
        onSelect(selectedIds.filter(id => id !== userId));
      } else {
        onSelect([...selectedIds, userId]);
      }
    } else {
      // В обычном режиме сразу назначаем
      onSelect([userId]);
    }
  };

  return (
    <div className="assignee-buttons">
      <div className="assignee-buttons-title">
        {multiMode ? 'Выберите исполнителей' : 'Исполнители'}
      </div>
      <div className="assignee-buttons-list">
        {employees.map((emp) => {
          const isSelected = selectedIds.includes(emp.user_id);
          return (
            <button
              key={emp.user_id}
              className={`assignee-btn ${isSelected ? 'selected' : ''}`}
              onClick={() => handleClick(emp.user_id)}
            >
              <span className="assignee-avatar">
                {emp.name.charAt(0)}
              </span>
              <span className="assignee-name">{emp.name}</span>
              {isSelected && multiMode && (
                <span className="assignee-check">✓</span>
              )}
            </button>
          );
        })}
      </div>
    </div>
  );
};

export default AssigneeButtons;
