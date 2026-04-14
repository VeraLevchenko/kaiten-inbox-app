import React from 'react';
import './InboxList.css';

/**
 * Список входящих (инбоксов) для выбора очереди.
 * Отображается в левой панели над очередью.
 */
const InboxList = ({ inboxes = [], onSelect }) => {
  if (inboxes.length <= 1) return null; // Показываем только если инбоксов > 1

  return (
    <div className="inbox-list">
      <div className="inbox-list-label">Входящие</div>
      {inboxes.map((inbox) => (
        <button
          key={inbox.id}
          className={`inbox-list-item ${inbox.is_active ? 'active' : ''}`}
          onClick={() => !inbox.is_active && onSelect(inbox.id)}
          title={inbox.name}
        >
          <span className="inbox-list-name">{inbox.name}</span>
          {inbox.is_active && <span className="inbox-active-dot" />}
        </button>
      ))}
    </div>
  );
};

export default InboxList;
