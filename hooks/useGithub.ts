import { useState, useCallback } from 'react';
import { FileType, Question, Registration, QuestionFile, RegistrationFile } from '@/lib/types';
import { githubService } from '@/lib/github';
import { useToast } from './useToast';

export function useGithub() {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState<QuestionFile | RegistrationFile | null>(null);
  const { showToast } = useToast();

  const fetchData = useCallback(async (fileType: FileType) => {
    setLoading(true);
    try {
      let result;
      if (fileType === 'kayitol') {
        result = await githubService.getRegistrations();
      } else {
        result = await githubService.getQuestions(fileType);
      }
      setData(result);
      return result;
    } catch (error) {
      showToast('error', 'Veri yüklenirken hata oluştu');
      throw error;
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  const saveData = useCallback(async (fileType: FileType, data: QuestionFile | RegistrationFile) => {
    setLoading(true);
    try {
      await githubService.saveFile(fileType, data);
      showToast('success', 'Değişiklikler başarıyla kaydedildi');
      return true;
    } catch (error) {
      showToast('error', 'Kaydetme başarısız oldu');
      throw error;
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  const addQuestion = useCallback(async (fileType: FileType, question: Omit<Question, 'id'>) => {
    if (fileType === 'kayitol') {
      throw new Error('Invalid operation for registrations');
    }

    setLoading(true);
    try {
      const currentData = await githubService.getQuestions(fileType);
      const newQuestion: Question = {
        ...question,
        id: `${fileType}-${Date.now()}`,
      };
      
      currentData.items.push(newQuestion);
      await githubService.saveFile(fileType, currentData);
      setData(currentData);
      showToast('success', 'Soru başarıyla eklendi');
      return newQuestion;
    } catch (error) {
      showToast('error', 'Soru eklenirken hata oluştu');
      throw error;
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  const updateQuestion = useCallback(async (fileType: FileType, questionId: string, updates: Partial<Question>) => {
    if (fileType === 'kayitol') {
      throw new Error('Invalid operation for registrations');
    }

    setLoading(true);
    try {
      const currentData = await githubService.getQuestions(fileType);
      const index = currentData.items.findIndex(q => q.id === questionId);
      
      if (index === -1) {
        throw new Error('Question not found');
      }
      
      currentData.items[index] = { ...currentData.items[index], ...updates };
      await githubService.saveFile(fileType, currentData);
      setData(currentData);
      showToast('success', 'Soru başarıyla güncellendi');
    } catch (error) {
      showToast('error', 'Soru güncellenirken hata oluştu');
      throw error;
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  const deleteQuestion = useCallback(async (fileType: FileType, questionId: string) => {
    if (fileType === 'kayitol') {
      throw new Error('Invalid operation for registrations');
    }

    setLoading(true);
    try {
      const currentData = await githubService.getQuestions(fileType);
      currentData.items = currentData.items.filter(q => q.id !== questionId);
      await githubService.saveFile(fileType, currentData);
      setData(currentData);
      showToast('success', 'Soru başarıyla silindi');
    } catch (error) {
      showToast('error', 'Soru silinirken hata oluştu');
      throw error;
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  const addRegistration = useCallback(async (registration: Omit<Registration, 'id'>) => {
    setLoading(true);
    try {
      const currentData = await githubService.getRegistrations();
      const newRegistration: Registration = {
        ...registration,
        id: `kayit-${Date.now()}`,
      };
      
      currentData.items.push(newRegistration);
      await githubService.saveFile('kayitol', currentData);
      setData(currentData);
      showToast('success', 'Kayıt başarıyla eklendi');
      return newRegistration;
    } catch (error) {
      showToast('error', 'Kayıt eklenirken hata oluştu');
      throw error;
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  const updateRegistration = useCallback(async (registrationId: string, updates: Partial<Registration>) => {
    setLoading(true);
    try {
      const currentData = await githubService.getRegistrations();
      const index = currentData.items.findIndex(r => r.id === registrationId);
      
      if (index === -1) {
        throw new Error('Registration not found');
      }
      
      currentData.items[index] = { ...currentData.items[index], ...updates };
      await githubService.saveFile('kayitol', currentData);
      setData(currentData);
      showToast('success', 'Kayıt başarıyla güncellendi');
    } catch (error) {
      showToast('error', 'Kayıt güncellenirken hata oluştu');
      throw error;
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  const deleteRegistration = useCallback(async (registrationId: string) => {
    setLoading(true);
    try {
      const currentData = await githubService.getRegistrations();
      currentData.items = currentData.items.filter(r => r.id !== registrationId);
      await githubService.saveFile('kayitol', currentData);
      setData(currentData);
      showToast('success', 'Kayıt başarıyla silindi');
    } catch (error) {
      showToast('error', 'Kayıt silinirken hata oluştu');
      throw error;
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  const uploadImage = useCallback(async (file: File, questionId: string) => {
    setLoading(true);
    try {
      const imageUrl = await githubService.uploadImage(file, questionId);
      showToast('success', 'Resim başarıyla yüklendi');
      return imageUrl;
    } catch (error) {
      showToast('error', 'Resim yüklenirken hata oluştu');
      throw error;
    } finally {
      setLoading(false);
    }
  }, [showToast]);

  return {
    loading,
    data,
    fetchData,
    saveData,
    addQuestion,
    updateQuestion,
    deleteQuestion,
    addRegistration,
    updateRegistration,
    deleteRegistration,
    uploadImage,
  };
}
