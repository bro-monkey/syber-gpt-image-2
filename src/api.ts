const API_BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '');

export type AppConfig = {
  base_url: string;
  usage_path: string;
  model: string;
  default_size: string;
  default_quality: string;
  user_name: string;
  api_key_set: boolean;
  api_key_hint: string;
};

export type HistoryItem = {
  id: string;
  mode: 'generate' | 'edit';
  prompt: string;
  model: string;
  size: string;
  quality: string;
  status: 'succeeded' | 'failed';
  image_url: string | null;
  image_path: string | null;
  input_image_url: string | null;
  input_image_path: string | null;
  revised_prompt: string | null;
  usage: Record<string, unknown> | null;
  provider_response: Record<string, unknown> | null;
  error: string | null;
  created_at: string;
  updated_at: string;
};

export type InspirationItem = {
  id: string;
  source_url: string;
  source_item_id: string;
  section: string;
  title: string;
  author: string | null;
  prompt: string;
  image_url: string | null;
  source_link: string | null;
  synced_at: string;
  created_at: string;
  updated_at: string;
};

export type InspirationStats = {
  total: number;
  last_synced_at: string | null;
  sections: number;
  section_counts: { section: string; count: number }[];
  source_url: string;
  sync_interval_seconds: number;
  last_error: string | null;
};

export type BalanceInfo = {
  ok: boolean;
  remaining: number | null;
  message?: string;
  raw: Record<string, unknown> | null;
};

export type AccountInfo = {
  user: {
    name: string;
    api_key_set: boolean;
    model: string;
    base_url: string;
  };
  balance: BalanceInfo;
  stats: {
    total: number;
    succeeded: number;
    edits: number;
    last_generation_at: string | null;
  };
};

export type LedgerEntry = {
  id: string;
  event_type: string;
  amount: number;
  currency: string;
  description: string;
  history_id: string | null;
  metadata: Record<string, unknown> | null;
  created_at: string;
};

export type GeneratePayload = {
  prompt: string;
  model?: string;
  size?: string;
  quality?: string;
  n?: number;
};

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      ...(options?.body instanceof FormData ? {} : { 'Content-Type': 'application/json' }),
      ...(options?.headers || {}),
    },
  });
  const text = await response.text();
  const data = text ? JSON.parse(text) : null;
  if (!response.ok) {
    const detail = data?.detail || data?.message || response.statusText;
    throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
  }
  return data as T;
}

export function getConfig() {
  return request<AppConfig>('/api/config');
}

export function saveConfig(config: Partial<AppConfig> & { api_key?: string; clear_api_key?: boolean }) {
  return request<AppConfig>('/api/config', {
    method: 'PUT',
    body: JSON.stringify(config),
  });
}

export function testConfig() {
  return request<{ ok: boolean; models: string[] }>('/api/config/test', { method: 'POST' });
}

export function getAccount() {
  return request<AccountInfo>('/api/account');
}

export function getBalance() {
  return request<BalanceInfo>('/api/balance');
}

export function getLedger(limit = 20) {
  return request<{ items: LedgerEntry[] }>(`/api/ledger?limit=${limit}`);
}

export function getHistory(params: { limit?: number; offset?: number; q?: string } = {}) {
  const search = new URLSearchParams();
  if (params.limit) search.set('limit', String(params.limit));
  if (params.offset) search.set('offset', String(params.offset));
  if (params.q) search.set('q', params.q);
  const query = search.toString();
  return request<{ items: HistoryItem[] }>(`/api/history${query ? `?${query}` : ''}`);
}

export function getInspirations(params: { limit?: number; offset?: number; q?: string; section?: string } = {}) {
  const search = new URLSearchParams();
  if (params.limit) search.set('limit', String(params.limit));
  if (params.offset) search.set('offset', String(params.offset));
  if (params.q) search.set('q', params.q);
  if (params.section) search.set('section', params.section);
  const query = search.toString();
  return request<{ items: InspirationItem[] }>(`/api/inspirations${query ? `?${query}` : ''}`);
}

export function getInspirationStats() {
  return request<InspirationStats>('/api/inspirations/stats');
}

export function syncInspirations() {
  return request<{ ok: boolean; parsed: number; count: number; synced_at: string }>('/api/inspirations/sync', {
    method: 'POST',
  });
}

export function deleteHistory(id: string) {
  return request<{ ok: boolean }>(`/api/history/${id}`, { method: 'DELETE' });
}

export function generateImage(payload: GeneratePayload) {
  return request<{ items: HistoryItem[]; provider: Record<string, unknown> }>('/api/images/generate', {
    method: 'POST',
    body: JSON.stringify({ n: 1, ...payload }),
  });
}

export function editImage(payload: GeneratePayload, image: File) {
  const form = new FormData();
  form.set('prompt', payload.prompt);
  if (payload.model) form.set('model', payload.model);
  if (payload.size) form.set('size', payload.size);
  if (payload.quality) form.set('quality', payload.quality);
  form.set('n', String(payload.n || 1));
  form.set('image', image);
  return request<{ items: HistoryItem[]; provider: Record<string, unknown> }>('/api/images/edit', {
    method: 'POST',
    body: form,
  });
}

export function formatBalance(balance: BalanceInfo | undefined) {
  if (!balance || balance.remaining === null || Number.isNaN(balance.remaining)) {
    return '--';
  }
  return balance.remaining.toFixed(4);
}

export function formatDate(value: string | null | undefined) {
  if (!value) return '--';
  return new Intl.DateTimeFormat(undefined, {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  }).format(new Date(value));
}
