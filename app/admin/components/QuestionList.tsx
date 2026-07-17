'use client';

import { useState } from 'react';
import { Question, FileType } from '@/lib/types';
import QuestionForm from './QuestionForm';
import { useGithub } from '@/hooks/useGithub';
import { Pencil, Trash2, Eye, Plus } from 'lucide-react';

interface QuestionListProps {
  questions: Question[];
  fileType: FileType;
}

export default function QuestionList({ questions, fileType }: QuestionListProps) {
  const [editingQuestion, setEditingQuestion] = useState<Question | null>(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const { deleteQuestion } = useGithub();

  const handleDelete = async (id: string) => {
    if (confirm('Bu soruyu silmek istediğinizden emin misiniz?')) {
      await deleteQuestion(fileType, id);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow">
      <div className="p-4 border-b flex justify-between items-center">
        <h2 className="text-lg font-semibold">Sorular</h2>
        <button
          onClick={() => setShowAddModal(true)}
          className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
        >
          <Plus className="w-4 h-4" />
          Yeni Soru Ekle
        </button>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">ID</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Soru</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Doğru Cevap</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">Resim</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">İşlemler</th>
            </tr>
          </thead>
          <tbody>
            {questions.map((question) => (
              <tr key={question.id} className="border-t hover:bg-gray-50">
                <td className="px-4 py-3 text-sm text-gray-600">{question.id}</td>
                <td className="px-4 py-3 text-sm text-gray-800 max-w-md truncate">
                  {question.question}
                </td>
                <td className="px-4 py-3 text-sm">
                  <span className="px-2 py-1 bg-green-100 text-green-800 rounded-full">
                    {question.correctAnswer}
                  </span>
                </td>
                <td className="px-4 py-3 text-sm">
                  {question.imageUrl ? (
                    <img src={question.imageUrl} alt="Question" className="w-10 h-10 object-cover rounded" />
                  ) : (
                    <span className="text-gray-400">Yok</span>
                  )}
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setEditingQuestion(question)}
                      className="p-1 text-blue-600 hover:bg-blue-50 rounded"
                    >
                      <Pencil className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(question.id)}
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

      {editingQuestion && (
        <QuestionForm
          question={editingQuestion}
          fileType={fileType}
          onClose={() => setEditingQuestion(null)}
        />
      )}

      {showAddModal && (
        <QuestionForm
          fileType={fileType}
          onClose={() => setShowAddModal(false)}
        />
      )}
    </div>
  );
}
