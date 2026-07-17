'use client';

import { FileType, QuestionFile, RegistrationFile } from '@/lib/types';
import { useGithub } from '@/hooks/useGithub';
import { Save } from 'lucide-react';

interface SaveButtonProps {
  fileType: FileType;
  data: QuestionFile | RegistrationFile | null;
}

export default function SaveButton({ fileType, data }: SaveButtonProps) {
  const { saveData, loading } = useGithub();

  const handleSave = async () => {
    if (!data) return;
    await saveData(fileType, data);
  };

  return (
    <button
      onClick={handleSave}
      disabled={loading || !data}
      className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors disabled:opacity-50"
    >
      <Save className="w-4 h-4" />
      {loading ? 'Kaydediliyor...' : 'GitHub\'a Kaydet'}
    </button>
  );
}
