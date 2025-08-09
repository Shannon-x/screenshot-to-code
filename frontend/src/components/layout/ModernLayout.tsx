import React from 'react';
import { useLocale } from '../../hooks/useLocale';
import { ConnectionState } from '../../lib/websocket-manager';
import { FiWifi, FiWifiOff, FiRefreshCw } from 'react-icons/fi';

interface ModernLayoutProps {
  children: React.ReactNode;
  connectionState?: ConnectionState;
  onRetry?: () => void;
}

export const ModernLayout: React.FC<ModernLayoutProps> = ({ 
  children, 
  connectionState,
  onRetry
}) => {
  const { t } = useLocale();

  const getConnectionIcon = () => {
    switch (connectionState) {
      case ConnectionState.OPEN:
        return <FiWifi className="text-green-500" />;
      case ConnectionState.CONNECTING:
      case ConnectionState.RECONNECTING:
        return <FiRefreshCw className="text-yellow-500 animate-spin" />;
      case ConnectionState.ERROR:
      case ConnectionState.CLOSED:
        return <FiWifiOff className="text-red-500" />;
      default:
        return null;
    }
  };

  const getConnectionText = () => {
    switch (connectionState) {
      case ConnectionState.OPEN:
        return t('messages.connected');
      case ConnectionState.CONNECTING:
        return t('messages.connecting');
      case ConnectionState.RECONNECTING:
        return t('messages.reconnecting');
      case ConnectionState.ERROR:
        return t('errors.connectionFailed');
      case ConnectionState.CLOSED:
        return t('messages.disconnected');
      default:
        return '';
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* 顶部导航栏 */}
      <header className="bg-white/80 backdrop-blur-md border-b border-gray-200 sticky top-0 z-50 animate-fade-in">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo和标题 */}
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center">
                  <span className="text-white font-bold text-lg">S</span>
                </div>
                <h1 className="text-xl font-semibold text-gray-900">
                  {t('main.title')}
                </h1>
              </div>
            </div>

            {/* 连接状态指示器 */}
            {connectionState && (
              <div className="flex items-center space-x-2 text-sm animate-scale-in">
                {getConnectionIcon()}
                <span className="text-gray-600">{getConnectionText()}</span>
                {(connectionState === ConnectionState.ERROR || connectionState === ConnectionState.CLOSED) && onRetry && (
                  <button
                    onClick={onRetry}
                    className="ml-2 text-blue-600 hover:text-blue-700 underline"
                  >
                    {t('actions.retry')}
                  </button>
                )}
              </div>
            )}
          </div>
        </div>
      </header>

      {/* 主内容区域 */}
      <main className="flex-1">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 animate-fade-in">
          {children}
        </div>
      </main>

      {/* 底部信息栏 */}
      <footer className="bg-white/60 backdrop-blur-sm border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <p>{t('main.description')}</p>
            <div className="flex items-center space-x-4">
              <a 
                href="https://github.com/Shannon-x/screenshot-to-code"
                target="_blank"
                rel="noopener noreferrer"
                className="hover:text-blue-600 transition-colors"
              >
                GitHub
              </a>
              <a 
                href="/docs"
                className="hover:text-blue-600 transition-colors"
              >
                {t('help.documentation')}
              </a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};