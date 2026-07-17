export interface Question {
  id: string;
  question: string;
  options: string[];
  correctAnswer: string;
  explanation: string;
  imageUrl?: string;
}

export interface Registration {
  id: string;
  fullName: string;
  phone: string;
  courseType: string;
  registerDate: string;
  status: 'active' | 'inactive' | 'completed';
}

export interface QuestionFile {
  title: string;
  type: 'questions';
  items: Question[];
}

export interface RegistrationFile {
  title: string;
  type: 'registrations';
  items: Registration[];
}

export type FileType = 'trafik' | 'saglik' | 'hayat' | 'karisik' | 'kayitol';

export interface FileConfig {
  id: FileType;
  label: string;
  fileName: string;
  type: 'questions' | 'registrations';
}

export const FILE_CONFIGS: FileConfig[] = [
  { id: 'trafik', label: 'Trafik Soruları', fileName: 'trafik.json', type: 'questions' },
  { id: 'saglik', label: 'Sağlık Soruları', fileName: 'saglik.json', type: 'questions' },
  { id: 'hayat', label: 'Hayat Bilgisi Soruları', fileName: 'hayat.json', type: 'questions' },
  { id: 'karisik', label: 'Karışık Sorular', fileName: 'karisik.json', type: 'questions' },
  { id: 'kayitol', label: 'Kayıtlar', fileName: 'kayitol.json', type: 'registrations' },
];
