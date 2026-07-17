'use client';

import { useToast } from '@/hooks/useToast';
import { CheckCircle, XCircle, Info, X } from 'lucide-react';

const toastIcons = {
  success: <CheckCircle className="w-5 h-5 text-green-500" />,
  error: <XCircle className="w-5 h-5 text-red-500" />,
  info: <Info className="w-5 h-5 text-blue-500" />,
};

export function ToastProvider({ children }: { children: React.ReactNode }) {
  return (
    <>
      {children}
      <ToastContainer />
    </>
  );
}

function ToastContainer() {
  const { toasts, removeToast } = useToast();

  return (
    <div className="fixed bottom-4 right-4 z-50 space-y-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`flex items-center gap-3 p-4 bg-white rounded-lg shadow-lg border ${
            toast.type === 'success' ? 'border-green-500' :
            toast.type === 'error' ? 'border-red-500' :
            'border-blue-500'
          } min-w-[300px] animate-slide-up`}
        >
          {toastIcons[toast.type]}
          <span className="flex-1 text-sm text-gray-800">{toast.message}</span>
          <button
            onClick={() => removeToast(toast.id)}
            className="p-1 hover:bg-gray-100 rounded"
          >
            <X className="w-4 h-4 text-gray-500" />
          </button>
        </div>
      ))}
    </div>
  );
}
