'use client';

import { useState } from 'react';
import { Registration } from '@/lib/types';
import RegistrationForm from './RegistrationForm';
import { useGithub } from '@/hooks/useGithub';
import { Pencil, Trash2, Plus, CheckCircle, XCircle, Clock } from 'lucide-react';

interface RegistrationListProps {
  registrations: Registration[];
}

const statusColors = {
  active: 'bg-green-100 text-green-800',
  inactive: 'bg-gray-100 text-gray-800',
  completed: 'bg-blue-100 text-blue-800',
};

const statusIcons = {
  active: <CheckCircle className="w-4 h-4" />,
  inactive: <XCircle className="w-4 h-4" />,
  completed: <Clock className="w-4 h-4" />,
};

export default function RegistrationList({ registrations }: RegistrationListProps) {
  const [editingRegistration, setEditingRegistration] = useState<Registration | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const { deleteRegistration } = useGithub();

  const handleDelete = async (id: string) => {
    if (confirm('Bu kaydı silmek istediğinizden emin misiniz?')) {
      await deleteRegistration(id);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b flex justify-between items-center">
        <h2 className="text-lg font-semibold">Kayıtlar</h2>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Yeni Kayıt Ekle
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">ID</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Ad Soyad</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Telefon</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Kurs Türü</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Kayıt Tarihi</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Durum</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">İşlemler</th>
            </tr>
          </thead>
          <tbody>
            {registrations.map((registration) => (
              <tr key={registration.id} className="border-t hover:bg-gray-50">
                <td className="px-4 py-3 text-sm text-gray-600">{registration.id}</td>
                <td className="px-4 py-3 text-sm text-gray-800">{registration.fullName}</td>
                <td className="px-4 py-3 text-sm text-gray-600">{registration.phone}</td>
                <td className="px-4 py-3 text-sm text-gray-600">{registration.courseType}</td>
                <td className="px-4 py-3 text-sm text-gray-600">
                  {new Date(registration.registerDate).toLocaleDateString('tr-TR')}
                </td>
                <td className="px-4 py-3">
                  <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${statusColors[registration.status]}`}>
                    {statusIcons[registration.status]}
                    {registration.status === 'active' ? 'Aktif' : 
                     registration.status === 'inactive' ? 'Pasif' : 'Tamamlandı'}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setEditingRegistration(registration)}
                      className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                    >
                      <Pencil className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(registration.id)}
                      className="p-1 text-red-600 hover:bg-red-50 rounded"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {editingRegistration && (
        <RegistrationForm
          registration={editingRegistration}
          onClose={() => setEditingRegistration(null)}
        />
      )}

      {showAddModal && (
        <RegistrationForm
          onClose={() => setShowAddModal(false)}
        />
      )}
    </div>
  );
}
