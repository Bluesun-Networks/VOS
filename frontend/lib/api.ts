import { API_BASE_URL } from './config';

// ---------- Structured error handling ----------

export class VosApiError extends Error {
  code: string;
  detail: string;
  status: number;

  constructor(status: number, code: string, detail: string) {
    super(detail);
    this.name = 'VosApiError';
    this.status = status;
    this.code = code;
    this.detail = detail;
  }
}

/**
 * Extract a structured error from a failed fetch response.
 * Falls back to a generic message if the body isn't our ErrorResponse shape.
 */
async function throwApiError(res: Response, fallback: string): Promise<never> {
  let code = 'unknown';
  let detail = fallback;
  try {
    const body = await res.json();
    if (body.error) code = body.error;
    if (body.detail) detail = body.detail;
  } catch {
    // body wasn't JSON — use the fallback message
  }
  throw new VosApiError(res.status, code, detail);
}

// ---------- Interfaces ----------

export interface Document {
  id: string;
  title: string;
  description?: string;
  content: string;
  is_archived: boolean;
  created_at: string;
  updated_at: string;
  review_count: number;
}

export interface Persona {
  id: string;
  name: string;
  description?: string;
  system_prompt: string;
  tone: string;
  focus_areas: string[];
  color: string;
  weight: number;
}

export interface Comment {
  id: string;
  content: string;
  persona_id: string;
  persona_name: string;
  persona_color: string;
  start_line: number;
  end_line: number;
  created_at: string;
}

export interface ReviewSummary {
  id: string;
  document_id: string;
  persona_ids: string[];
  status: string;
  created_at: string;
  completed_at?: string;
  comment_count: number;
}

export interface PersonaStatus {
  persona_id: string;
  persona_name: string;
  persona_color: string;
  status: 'queued' | 'running' | 'completed';
}

export interface MetaCommentSource {
  persona_id: string;
  persona_name: string;
  persona_color: string;
  original_content: string;
}

export interface MetaComment {
  id: string;
  content: string;
  start_line: number;
  end_line: number;
  sources: MetaCommentSource[];
  category: string;
  priority: string;
  created_at: string;
}

export interface MetaReview {
  comments: MetaComment[];
  verdict: 'ship_it' | 'fix_first' | 'major_rework';
  confidence: number;
}

export async function fetchDocuments(includeArchived = false): Promise<Document[]> {
  const params = includeArchived ? '?include_archived=true' : '';
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${params}`);
  if (!res.ok) await throwApiError(res, 'Failed to fetch documents');
  return res.json();
}

export async function fetchDocument(id: string): Promise<Document> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${id}`);
  if (!res.ok) await throwApiError(res, 'Failed to fetch document');
  return res.json();
}

export async function fetchPersonas(): Promise<Persona[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/personas/`);
  if (!res.ok) await throwApiError(res, 'Failed to fetch personas');
  return res.json();
}

export async function updatePersona(personaId: string, data: { weight?: number }): Promise<Persona> {
  const res = await fetch(`${API_BASE_URL}/api/v1/personas/${personaId}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data),
  });
  if (!res.ok) await throwApiError(res, 'Failed to update persona');
  return res.json();
}

export async function uploadFile(file: File): Promise<{ document_id: string; title: string }> {
  const formData = new FormData();
  formData.append('file', file);
  const res = await fetch(`${API_BASE_URL}/api/v1/reviews/upload`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) await throwApiError(res, 'Upload failed');
  return res.json();
}

export async function uploadRaw(content: string, title?: string): Promise<{ document_id: string; title: string }> {
  const res = await fetch(`${API_BASE_URL}/api/v1/reviews/upload/raw`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, title }),
  });
  if (!res.ok) await throwApiError(res, 'Upload failed');
  return res.json();
}

export async function fetchReviews(docId: string): Promise<ReviewSummary[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/reviews/${docId}/reviews`);
  if (!res.ok) await throwApiError(res, 'Failed to fetch reviews');
  return res.json();
}

export async function fetchLatestComments(docId: string): Promise<Comment[]> {
  const res = await fetch(`${API_BASE_URL}/api/v1/reviews/${docId}/reviews/latest/comments`);
  if (!res.ok) return [];
  return res.json();
}

export async function synthesizeMetaReview(docId: string, reviewId: string): Promise<MetaReview> {
  const res = await fetch(`${API_BASE_URL}/api/v1/reviews/${docId}/reviews/${reviewId}/meta`, {
    method: 'POST',
  });
  if (!res.ok) await throwApiError(res, 'Failed to synthesize meta review');
  return res.json();
}

export async function fetchMetaComments(docId: string, reviewId: string): Promise<MetaReview> {
  const res = await fetch(`${API_BASE_URL}/api/v1/reviews/${docId}/reviews/${reviewId}/meta`);
  if (!res.ok) return { comments: [], verdict: 'ship_it', confidence: 0 };
  return res.json();
}

export async function archiveDocument(docId: string): Promise<Document> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${docId}/archive`, {
    method: 'POST',
  });
  if (!res.ok) await throwApiError(res, 'Failed to archive document');
  return res.json();
}

export async function restoreDocument(docId: string): Promise<Document> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${docId}/restore`, {
    method: 'POST',
  });
  if (!res.ok) await throwApiError(res, 'Failed to restore document');
  return res.json();
}

export async function deleteDocument(docId: string): Promise<void> {
  const res = await fetch(`${API_BASE_URL}/api/v1/documents/${docId}`, {
    method: 'DELETE',
  });
  if (!res.ok) await throwApiError(res, 'Failed to delete document');
}

export function startReviewStream(
  docId: string,
  personaIds: string[],
  onEvent: (event: {
    type: string;
    persona_id?: string;
    persona_name?: string;
    persona_color?: string;
    status?: string;
    comment?: Comment;
    total_comments?: number;
    review_id?: string;
    error?: string;
    detail?: string;
  }) => void,
  onError: (err: Error) => void,
): AbortController {
  const controller = new AbortController();

  (async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/reviews/${docId}/review`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ persona_ids: personaIds }),
        signal: controller.signal,
      });

      if (!res.ok) await throwApiError(res, 'Failed to start review');

      const reader = res.body?.getReader();
      const decoder = new TextDecoder();
      if (!reader) throw new Error('No response body');

      let buffer = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6));
              // Surface SSE error events as proper errors
              if (data.type === 'error') {
                onError(new VosApiError(
                  502,
                  data.error || 'stream_error',
                  data.detail || 'Review stream encountered an error',
                ));
              } else {
                onEvent(data);
              }
            } catch {
              // skip malformed SSE lines
            }
          }
        }
      }
    } catch (err) {
      if (err instanceof Error && err.name !== 'AbortError') {
        onError(err);
      }
    }
  })();

  return controller;
}
