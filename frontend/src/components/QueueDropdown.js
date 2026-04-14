import React, { useState, useEffect, useRef } from 'react';
import './QueueDropdown.css';

/**
 * Выпадающий список писем в очереди.
 * Позволяет выбрать конкретное письмо для обработки.
 */
const QueueDropdown = ({ items = [], currentCardId, onSelect }) => {
  const [isOpen, setIsOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    if (!isOpen) return;
    const handleClickOutside = (e) => {
      if (ref.current && !ref.current.contains(e.target)) {
        setIsOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  const handleSelect = (item) => {
    onSelect(item.card_id);
    setIsOpen(false);
  };

  return (
    <div className="queue-dropdown" ref={ref}>
      <button
        className={`queue-dropdown-toggle ${isOpen ? 'open' : ''}`}
        onClick={() => setIsOpen(!isOpen)}
        title="Выбрать письмо из очереди"
      >
        <span className="queue-dropdown-label">
          Очередь
          <span className="queue-dropdown-count">{items.length}</span>
        </span>
        <span className="queue-dropdown-arrow">{isOpen ? '▲' : '▼'}</span>
      </button>

      {isOpen && (
        <div className="queue-dropdown-list">
          {items.length === 0 ? (
            <div className="queue-dropdown-empty">Очередь пуста</div>
          ) : (
            items.map((item) => {
              const isActive = item.card_id === currentCardId;
              return (
                <button
                  key={item.card_id}
                  className={`queue-dropdown-item
                    ${isActive ? 'active' : ''}
                    ${item.is_deferred ? 'deferred' : ''}
                  `}
                  onClick={() => handleSelect(item)}
                  title={item.title}
                >
                  <span className="queue-item-no">№ {item.incoming_no}</span>
                  <span className="queue-item-title">{item.title}</span>
                  {item.is_deferred && (
                    <span className="queue-item-deferred-tag">отложено</span>
                  )}
                </button>
              );
            })
          )}
        </div>
      )}
    </div>
  );
};

export default QueueDropdown;
