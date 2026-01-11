import React, { useState, useEffect } from 'react';
import './FileTabs.css';

/**
 * Компонент вкладок для просмотра файлов письма
 * Сохраняет выбранную вкладку при обновлении если card_id не изменился
 */
const FileTabs = ({ files, incomingNo, cardId }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [prevCardId, setPrevCardId] = useState(null);

  // Сброс вкладки только если изменился card_id
  useEffect(() => {
    if (cardId !== prevCardId) {
      setActiveTab(0);
      setPrevCardId(cardId);
    }
  }, [cardId, prevCardId]);

  if (!files || files.length === 0) {
    return (
      <div className="file-tabs-empty">
        <p>Нет файлов для отображения</p>
      </div>
    );
  }

  const activeFile = files[activeTab];

  // Рендер содержимого в зависимости от типа файла
  const renderFileContent = (file) => {
    const ext = file.ext.toLowerCase();

    // PDF - встроенный viewer
    if (ext === 'pdf') {
      return (
        <iframe
          src={file.url}
          title={file.name}
          className="file-viewer-iframe"
        />
      );
    }

    // HTML - встроенный viewer
    if (ext === 'html' || ext === 'htm') {
      return (
        <iframe
          src={file.url}
          title={file.name}
          className="file-viewer-iframe"
        />
      );
    }

    // Текстовые файлы - встроенный viewer через iframe
    if (ext === 'txt') {
      return (
        <iframe
          src={file.url}
          title={file.name}
          className="file-viewer-iframe"
        />
      );
    }

    // DOCX, XLSX и прочие - ссылка на скачивание
    return (
      <div className="file-download-wrapper">
        <div className="file-info">
          <div className="file-icon">
            {ext === 'docx' && '📄'}
            {ext === 'xlsx' && '📊'}
            {ext === 'doc' && '📄'}
            {ext === 'xls' && '📊'}
            {!['docx', 'xlsx', 'doc', 'xls'].includes(ext) && '📎'}
          </div>
          <div className="file-details">
            <div className="file-name">{file.name}</div>
            <div className="file-ext">{ext.toUpperCase()}</div>
          </div>
        </div>
        <a
          href={file.url}
          download={file.name}
          target="_blank"
          rel="noopener noreferrer"
          className="file-download-btn"
        >
          Скачать / Открыть
        </a>
      </div>
    );
  };

  return (
    <div className="file-tabs">
      {/* Вкладки */}
      <div className="tabs-header">
        {files.map((file, index) => (
          <button
            key={index}
            className={`tab ${activeTab === index ? 'active' : ''}`}
            onClick={() => setActiveTab(index)}
          >
            <span className="tab-icon">
              {file.ext === 'pdf' && '📕'}
              {file.ext === 'txt' && '📄'}
              {file.ext === 'html' && '🌐'}
              {file.ext === 'docx' && '📘'}
              {file.ext === 'xlsx' && '📊'}
              {!['pdf', 'txt', 'html', 'docx', 'xlsx'].includes(file.ext) && '📎'}
            </span>
            <span className="tab-name">{file.name}</span>
          </button>
        ))}
      </div>

      {/* Содержимое файла */}
      <div className="tabs-content">
        {renderFileContent(activeFile)}
      </div>
    </div>
  );
};

export default FileTabs;
