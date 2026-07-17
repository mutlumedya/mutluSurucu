'use client';

import { FileType, FILE_CONFIGS } from '@/lib/types';
import { Home, FileText, Users, Settings } from 'lucide-react';

interface SidebarProps {
  selectedFile: FileType;
  onFileSelect: (fileType: FileType) => void;
}

const iconMap = {
  trafik: <FileText className="w-5 h-5" />,
  saglik: <FileText className="w-5 h-5" />,
  hayat: <FileText className="w-5 h-5" />,
  karisik: <FileText className="w-5 h-5" />,
  kayitol: <Users className="w-5 h-5" />,
};

export default function Sidebar({ selectedFile, onFileSelect }: SidebarProps) {
  return (
    <aside className="w-64 bg-white border-r border-gray-200">
      <div className="p-4 border-b border-gray-200">
        <h1 className="text-xl font-bold text-blue-600">Mutlu Sürücü</h1>
        <p className="text-sm text-gray-500">Admin Panel</p>
      </div>
      
      <nav className="p-4">
        <div className="space-y-1">
          {FILE_CONFIGS.map((config) => (
            <button
              key={config.id}
              onClick={() => onFileSelect(config.id)}
              className={`
                w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors
                ${selectedFile === config.id 
                  ? 'bg-blue-50 text-blue-600' 
                  : 'text-gray-600 hover:bg-gray-50'}
              `}
            >
              {iconMap[config.id]}
              <span>{config.label}</span>
            </button>
          ))}
        </div>
      </nav>
    </aside>
  );
}
