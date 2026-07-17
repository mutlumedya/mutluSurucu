import { Octokit } from 'octokit';
import { QuestionFile, RegistrationFile, FileType, FILE_CONFIGS } from './types';

class GitHubService {
  private octokit: Octokit;
  private owner: string;
  private repo: string;
  private branch: string = 'main';

  constructor() {
    const token = process.env.GITHUB_TOKEN;
    const owner = process.env.GITHUB_OWNER;
    const repo = process.env.GITHUB_REPO;

    if (!token || !owner || !repo) {
      throw new Error('GitHub environment variables are not set');
    }

    this.octokit = new Octokit({ auth: token });
    this.owner = owner;
    this.repo = repo;
  }

  private async getFileContent(fileName: string): Promise<any> {
    try {
      const response = await this.octokit.rest.repos.getContent({
        owner: this.owner,
        repo: this.repo,
        path: fileName,
        ref: this.branch,
      });

      if ('content' in response.data) {
        const content = Buffer.from(response.data.content, 'base64').toString('utf-8');
        return {
          content: JSON.parse(content),
          sha: response.data.sha
        };
      }
      throw new Error('File not found');
    } catch (error: any) {
      if (error.status === 404) {
        return null;
      }
      throw error;
    }
  }

  async getQuestions(fileType: FileType): Promise<QuestionFile> {
    const config = FILE_CONFIGS.find(f => f.id === fileType);
    if (!config || config.type !== 'questions') {
      throw new Error('Invalid question file type');
    }

    const result = await this.getFileContent(config.fileName);
    if (!result) {
      return {
        title: config.label,
        type: 'questions',
        items: []
      };
    }
    return result.content;
  }

  async getRegistrations(): Promise<RegistrationFile> {
    const config = FILE_CONFIGS.find(f => f.id === 'kayitol');
    if (!config) throw new Error('Registration config not found');

    const result = await this.getFileContent(config.fileName);
    if (!result) {
      return {
        title: 'Kayıtlar',
        type: 'registrations',
        items: []
      };
    }
    return result.content;
  }

  async saveFile(fileType: FileType, data: QuestionFile | RegistrationFile): Promise<void> {
    const config = FILE_CONFIGS.find(f => f.id === fileType);
    if (!config) throw new Error('File config not found');

    const content = JSON.stringify(data, null, 2);
    const encodedContent = Buffer.from(content).toString('base64');

    try {
      const existing = await this.getFileContent(config.fileName);
      
      if (existing) {
        await this.octokit.rest.repos.createOrUpdateFileContents({
          owner: this.owner,
          repo: this.repo,
          path: config.fileName,
          message: `Update ${config.fileName}`,
          content: encodedContent,
          sha: existing.sha,
          branch: this.branch,
        });
      } else {
        await this.octokit.rest.repos.createOrUpdateFileContents({
          owner: this.owner,
          repo: this.repo,
          path: config.fileName,
          message: `Create ${config.fileName}`,
          content: encodedContent,
          branch: this.branch,
        });
      }
    } catch (error) {
      console.error('Error saving file:', error);
      throw new Error(`Failed to save ${config.fileName}`);
    }
  }

  async uploadImage(imageFile: File, questionId: string): Promise<string> {
    const fileExtension = imageFile.name.split('.').pop();
    const fileName = `images/${questionId}.${fileExtension}`;
    const base64Content = await this.fileToBase64(imageFile);

    try {
      const existing = await this.getFileContent(fileName);
      
      await this.octokit.rest.repos.createOrUpdateFileContents({
        owner: this.owner,
        repo: this.repo,
        path: fileName,
        message: `Upload image ${questionId}`,
        content: base64Content.split(',')[1],
        sha: existing?.sha,
        branch: this.branch,
      });

      return `https://raw.githubusercontent.com/${this.owner}/${this.repo}/${this.branch}/${fileName}`;
    } catch (error) {
      console.error('Error uploading image:', error);
      throw new Error('Failed to upload image');
    }
  }

  private async fileToBase64(file: File): Promise<string> {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.readAsDataURL(file);
      reader.onload = () => resolve(reader.result as string);
      reader.onerror = error => reject(error);
    });
  }
}

export const githubService = new GitHubService();
