'use client';

import { useState } from 'react';
import { Registration } from '@/lib/types';
import { useGithub } from '@/hooks/useGithub';
import { X } from 'lucide-react';

interface RegistrationFormProps {
  registration?: Registration;
  onClose: () => void;
}

export default function RegistrationForm({ registration, onClose }: RegistrationFormProps) {
  const [formData, setFormData] = useState<Partial<Registration>>(
    registration || {
      fullName: '',
      phone: '',
      courseType: 'Trafik',
      registerDate: new Date().toISOString().split('T')[0],
      status: 'active',
    }
  );
  const { addRegistration, updateRegistration, loading } = useGithub();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      if (registration) {
        await updateRegistration(registration.id, formData);
      } else {
        await addRegistration(formData as Omit<Registration, 'id'>);
      }
      onClose();
    } catch (error) {
      console.error('Error saving registration:', error);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg w-full max-w-md">
        <div className="p-4 border-b flex justify-between items-center">
          <h3 className="text-lg font-semibold">
            {registration ? 'Kaydı Düzenle' : 'Yeni Kayıt Ekle'}
          </h3>
          <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Ad Soyad
            </label>
            <input
              type="text"
              value={formData.fullName}
              onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Telefon
            </label>
            <input
              type="tel"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="0555 123 45 67"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Kurs Türü
            </label>
            <select
              value={formData.courseType}
              onChange={(e) => setFormData({ ...formData, courseType: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="Trafik">Trafik</option>
              <option value="Sağlık">Sağlık</option>
              <option value="Hayat Bilgisi">Hayat Bilgisi</option>
              <option value="Karışık">Karışık</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Kayıt Tarihi
            </label>
            <input
              type="date"
              value={formData.registerDate}
              onChange={(e) => setFormData({ ...formData, registerDate: e.target.value })}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Durum
            </label>
            <select
              value={formData.status}
              onChange={(e) => setFormData({ ...formData, status: e.target.value as Registration['status'] })}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              <option value="active">Aktif</option>
              <option value="inactive">Pasif</option>
              <option value="completed">Tamamlandı</option>
            </select>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-600 hover:bg-gray-100 rounded-lg"
            >
              İptal
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
            >
              {loading ? 'Kaydediliyor...' : (registration ? 'Güncelle' : 'Ekle')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
