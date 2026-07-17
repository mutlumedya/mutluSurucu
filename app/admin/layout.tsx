'use client';

import { useState } from 'react';
import Sidebar from './components/Sidebar';
import { FileType } from '@/lib/types';
import { ToastProvider } from '@/components/ui/toast';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const [selectedFile, setSelectedFile] = useState<FileType>('trafik');

  return (
    <ToastProvider>
      <div className="flex h-screen bg-gray-50">
        <Sidebar selectedFile={selectedFile} onFileSelect={setSelectedFile} />
        <main className="flex-1 overflow-y-auto p-6">
          {children}
        </main>
      </div>
    </ToastProvider>
  );
}
