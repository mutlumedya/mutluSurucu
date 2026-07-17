'use client';

import { useSearchParams } from 'next/navigation';
import { useEffect, useState } from 'react';
import { useGithub } from '@/hooks/useGithub';
import QuestionList from './components/QuestionList';
import RegistrationList from './components/RegistrationList';
import SaveButton from './components/SaveButton';
import SearchBar from './components/SearchBar';
import { FileType } from '@/lib/types';

export default function AdminPage() {
  const searchParams = useSearchParams();
  const fileType = (searchParams.get('file') as FileType) || 'trafik';
  const { loading, data, fetchData } = useGithub();
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    fetchData(fileType);
  }, [fileType, fetchData]);

  const isRegistration = fileType === 'kayitol';
  const filteredData = data?.items?.filter((item: any) => {
    if (!searchTerm) return true;
    const searchLower = searchTerm.toLowerCase();
    if (isRegistration) {
      return item.fullName?.toLowerCase().includes(searchLower) ||
             item.phone?.includes(searchTerm) ||
             item.courseType?.toLowerCase().includes(searchLower);
    } else {
      return item.question?.toLowerCase().includes(searchLower);
    }
  }) || [];

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">Yükleniyor...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div className="flex items-center gap-4">
          <SearchBar value={searchTerm} onChange={setSearchTerm} />
        </div>
        <SaveButton fileType={fileType} data={data} />
      </div>

      {isRegistration ? (
        <RegistrationList registrations={filteredData} />
      ) : (
        <QuestionList questions={filteredData} fileType={fileType} />
      )}
    </div>
  );
}
