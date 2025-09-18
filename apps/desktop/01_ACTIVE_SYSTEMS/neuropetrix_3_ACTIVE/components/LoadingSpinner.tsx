
import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: 'medical' | 'blue' | 'green' | 'purple';
  text?: string;
  showText?: boolean;
}

export default function LoadingSpinner({ 
  size = 'md', 
  color = 'medical', 
  text = 'Yükleniyor...',
  showText = true 
}: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16'
  };

  const colorClasses = {
    medical: 'border-medical-600',
    blue: 'border-blue-600',
    green: 'border-green-600',
    purple: 'border-purple-600'
  };

  return (
    <div className="flex flex-col items-center justify-center p-6">
      <div className={`${sizeClasses[size]} animate-spin rounded-full border-2 border-gray-200 border-t-2 border-t-${colorClasses[color]}`}></div>
      {showText && (
        <p className="mt-4 text-sm text-medical-600 font-medium">{text}</p>
      )}
    </div>
  );
}

// Page Loading Component
export function PageLoading() {
  return (
    <div className="min-h-screen bg-medical-50 flex items-center justify-center">
      <div className="text-center">
        <div className="animate-spin rounded-full h-20 w-20 border-b-2 border-medical-600 mx-auto mb-6"></div>
        <h2 className="text-2xl font-bold text-medical-900 mb-2">NeuroPETrix</h2>
        <p className="text-medical-600 text-lg">Sayfa yükleniyor...</p>
        <div className="mt-4 flex justify-center space-x-2">
          <div className="w-2 h-2 bg-medical-400 rounded-full animate-bounce"></div>
          <div className="w-2 h-2 bg-medical-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-2 h-2 bg-medical-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        </div>
      </div>
    </div>
  );
}

// Content Loading Component
export function ContentLoading({ message = 'İçerik yükleniyor...' }: { message?: string }) {
  return (
    <div className="flex items-center justify-center py-12">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-medical-600 mx-auto mb-4"></div>
        <p className="text-medical-600">{message}</p>
      </div>
    </div>
  );
}

// Skeleton Loading Component
export function SkeletonCard() {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-medical-200 p-6 animate-pulse">
      <div className="flex items-center space-x-4 mb-4">
        <div className="w-12 h-12 bg-medical-200 rounded-full"></div>
        <div className="flex-1">
          <div className="h-4 bg-medical-200 rounded w-3/4 mb-2"></div>
          <div className="h-3 bg-medical-200 rounded w-1/2"></div>
        </div>
      </div>
      <div className="space-y-3">
        <div className="h-3 bg-medical-200 rounded"></div>
        <div className="h-3 bg-medical-200 rounded w-5/6"></div>
        <div className="h-3 bg-medical-200 rounded w-4/6"></div>
      </div>
    </div>
  );
}

// Progress Bar Component
export function ProgressBar({ 
  progress, 
  total = 100, 
  label = 'İlerleme',
  showPercentage = true 
}: { 
  progress: number; 
  total?: number; 
  label?: string;
  showPercentage?: boolean;
}) {
  const percentage = Math.min((progress / total) * 100, 100);
  
  return (
    <div className="w-full">
      {label && (
        <div className="flex justify-between items-center mb-2">
          <span className="text-sm font-medium text-medical-700">{label}</span>
          {showPercentage && (
            <span className="text-sm font-medium text-medical-600">{Math.round(percentage)}%</span>
          )}
        </div>
      )}
      <div className="w-full bg-medical-200 rounded-full h-2">
        <div 
          className="bg-medical-600 h-2 rounded-full transition-all duration-300 ease-out"
          style={{ width: `${percentage}%` }}
        ></div>
      </div>
    </div>
  );
}
