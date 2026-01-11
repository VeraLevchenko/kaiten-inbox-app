import React, { useState, useEffect } from 'react';
import { getFileUrl } from '../services/api';
import './FileTabs.css';

const FileTabs = ({ files, incomingNo, cardId }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [prevCardId, setPrevCardId] = useState(null);
  const [publicUrl, setPublicUrl] = useState('http://localhost:8000');

  // Получаем публичный URL от backend
  useEffect(() => {
    fetch('http://localhost:8000/api/public-url')
      .then(r => r.json())
      .then(data => {
        console.log('[DEBUG] Got public URL:', data.public_url);
        setPublicUrl(data.public_url);
      })
      .catch(err => console.error('[ERROR] Failed to get public URL:', err));
  }, []);

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

  const renderFileContent = (file) => {
    const ext = file.ext.toLowerCase();
    const localUrl = getFileUrl(incomingNo, file.name);

    // Изображения - показываем как <img>
    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp', 'svg'].includes(ext)) {
      return (
        <div className="file-image-wrapper">
          <img 
            src={localUrl} 
            alt={file.name}
            className="file-viewer-image"
          />
        </div>
      );
    }

    // PDF - показываем во встроенном iframe
    if (ext === 'pdf') {
      return (
        <iframe
          src={localUrl}
          title={file.name}
          className="file-viewer-iframe"
        />
      );
    }

   // DOCX - показываем через Google Docs Viewer
    if (['docx', 'doc'].includes(ext)) {
      const filePublicUrl = `${publicUrl}/public-files/${incomingNo}/${encodeURIComponent(file.name)}`;
      const viewerUrl = `https://docs.google.com/viewer?url=${encodeURIComponent(filePublicUrl)}&embedded=true`;
      
      console.log('[DEBUG] DOCX Google viewer URL:', viewerUrl);
      
      return (
        <iframe
          src={viewerUrl}
          title={file.name}
          className="file-viewer-iframe"
        />
      );
    }

    // HTML и TXT - показываем во встроенном iframe
    if (ext === 'html' || ext === 'htm' || ext === 'txt') {
      return (
        <iframe
          src={localUrl}
          title={file.name}
          className="file-viewer-iframe"
        />
      );
    }

    // Для остальных файлов (XLSX и т.д.) - показываем кнопку скачивания
    return (
      <div className="file-download-wrapper">
        <div className="file-info">
          <div className="file-icon">
            {(ext === 'xlsx' || ext === 'xls') && '📊'}
            {(ext === 'pptx' || ext === 'ppt') && '📊'}
            {!['xlsx', 'xls', 'pptx', 'ppt'].includes(ext) && '📎'}
          </div>
          <div className="file-details">
            <div className="file-name">{file.name}</div>
            <div className="file-ext">{ext.toUpperCase()}</div>
          </div>
        </div>
        <a
          href={localUrl}
          download={file.name}
          target="_blank"
          rel="noopener noreferrer"
          className="file-download-btn"
        >
          Скачать файл
        </a>
      </div>
    );
  };

  const getFileIcon = (ext) => {
    const lower = ext.toLowerCase();
    if (['jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'].includes(lower)) return '🖼️';
    if (lower === 'pdf') return '📕';
    if (lower === 'txt') return '📄';
    if (lower === 'html' || lower === 'htm') return '🌐';
    if (lower === 'docx' || lower === 'doc') return '📘';
    if (lower === 'xlsx' || lower === 'xls') return '📊';
    if (lower === 'pptx' || lower === 'ppt') return '📊';
    return '📎';
  };

  return (
    <div className="file-tabs">
      <div className="tabs-header">
        {files.map((file, index) => (
          <button
            key={index}
            className={`tab ${activeTab === index ? 'active' : ''}`}
            onClick={() => setActiveTab(index)}
          >
            <span className="tab-icon">
              {getFileIcon(file.ext)}
            </span>
            <span className="tab-name">{file.name}</span>
          </button>
        ))}
      </div>
      <div className="tabs-content">
        {renderFileContent(activeFile)}
      </div>
    </div>
  );
};

export default FileTabs;