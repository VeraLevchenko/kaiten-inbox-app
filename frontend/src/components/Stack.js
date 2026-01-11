import React from 'react';
import { motion } from 'framer-motion';
import './Stack.css';

/**
 * Компонент стопки документов (узкая и высокая)
 * Визуализирует количество писем как стопку книг
 */
const Stack = ({ title, count, position = 'left' }) => {
  // Высота стопки пропорциональна количеству
  const stackHeight = Math.min(count * 8, 400); // макс 400px

  return (
    <div className={`stack-container stack-${position}`}>
      <div className="stack-title">{title}</div>
      <div className="stack-wrapper">
        <motion.div
          className="stack"
          initial={{ height: 0 }}
          animate={{ height: stackHeight }}
          transition={{ duration: 0.5 }}
        >
          {/* Визуализация "книг" в стопке */}
          {Array.from({ length: Math.min(count, 20) }).map((_, index) => (
            <div
              key={index}
              className="stack-item"
              style={{
                bottom: `${index * 4}px`,
                transform: `translateX(${(index % 3) * 2}px)`,
              }}
            />
          ))}
        </motion.div>
        <div className="stack-count">{count}</div>
      </div>
    </div>
  );
};

export default Stack;
