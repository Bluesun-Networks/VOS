const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface Document {
  id: string;
  title: string;
  description?: string;
  repo_path: string;
  current_branch: string;
  created_at: string;
  updated_at: string;
  versions: DocumentVersion[];
}

export interface DocumentVersion {
  commit_hash: string;
  message: string;
  author: string;
  timestamp: string;
}

export interface Persona {
  id: string;
  name: string;
  description?: string;
  system_prompt: string;
  tone: string;
  focus_areas: string[];
  color: string;
}

export interface Comment {
  id: string;
  content: string;
  persona_id: string;
  persona_name: string;
  persona_color: string;
  document_id: string;
  version_hash: string;
  anchor: {
    file_path: string;
    start_line: number;
    end_line: number;
  };
  created_at: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE) {
    this.baseUrl = baseUrl;
  }

  private async fetch<T>(path: string, options?: RequestInit): Promise<T> {
    const res = await fetch(`${this.baseUrl}${path}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });
    
    if (!res.ok) {
      throw new Error(`API error: ${res.status}`);
    }
    
    return res.json();
  }

  // Documents
  async listDocuments(): Promise<Document[]> {
    return this.fetch('/api/v1/documents/');
  }

  async getDocument(id: string): Promise<Document> {
    return this.fetch(`/api/v1/documents/${id}`);
  }

  async createDocument(data: { title: string; content: string; description?: string }): Promise<Document> {
    return this.fetch('/api/v1/documents/', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getDocumentContent(id: string, version?: string): Promise<{ content: string; version: string | null }> {
    const params = version ? `?version=${version}` : '';
    return this.fetch(`/api/v1/documents/${id}/content${params}`);
  }

  async updateDocument(id: string, content: string, message: string): Promise<Document> {
    return this.fetch(`/api/v1/documents/${id}`, {
      method: 'PUT',
      body: JSON.stringify({ content, message }),
    });
  }

  async getDocumentDiff(id: string, fromVersion: string, toVersion?: string): Promise<{ diff: string }> {
    const params = toVersion ? `?from_version=${fromVersion}&to_version=${toVersion}` : `?from_version=${fromVersion}`;
    return this.fetch(`/api/v1/documents/${id}/diff${params}`);
  }

  // Personas
  async listPersonas(): Promise<Persona[]> {
    return this.fetch('/api/v1/personas/');
  }

  async getPersona(id: string): Promise<Persona> {
    return this.fetch(`/api/v1/personas/${id}`);
  }
}

export const api = new ApiClient();
