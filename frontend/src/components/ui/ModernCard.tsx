import React from 'react';
import { styles } from '../../styles/theme';
import { cn } from '../../lib/utils';

interface ModernCardProps {
  children: React.ReactNode;
  title?: string;
  description?: string;
  icon?: React.ReactNode;
  hoverable?: boolean;
  padding?: 'sm' | 'md' | 'lg';
  className?: string;
  onClick?: () => void;
}

export const ModernCard: React.FC<ModernCardProps> = ({
  children,
  title,
  description,
  icon,
  hoverable = false,
  padding = 'md',
  className,
  onClick,
}) => {
  return (
    <div
      className={cn(
        styles.card.base,
        hoverable && styles.card.hover,
        styles.card.padding[padding],
        onClick && 'cursor-pointer',
        'transition-all duration-200 animate-fade-in',
        hoverable && 'hover:-translate-y-1',
        className
      )}
      onClick={onClick}
    >
      {(title || description || icon) && (
        <div className="mb-4">
          <div className="flex items-start space-x-3">
            {icon && (
              <div className="flex-shrink-0">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center text-blue-600">
                  {icon}
                </div>
              </div>
            )}
            <div className="flex-1">
              {title && (
                <h3 className="text-lg font-semibold text-gray-900">
                  {title}
                </h3>
              )}
              {description && (
                <p className="mt-1 text-sm text-gray-600">
                  {description}
                </p>
              )}
            </div>
          </div>
        </div>
      )}
      {children}
    </div>
  );
};