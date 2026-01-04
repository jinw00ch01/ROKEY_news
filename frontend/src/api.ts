const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export type Article = {
  id: number
  source_id?: number
  title: string
  link: string
  published_at?: string
  summary?: string
  sentiment_label?: 'positive' | 'neutral' | 'negative'
  sentiment_score?: number
  keywords?: string[]
}

export type Analysis = {
  id: number
  article_id: number
  summary: string
  sentiment_label: 'positive' | 'neutral' | 'negative'
  sentiment_score: number
  keywords?: string[]
  json_meta?: Record<string, unknown>
  model_name?: string
  created_at?: string
}

export type ArticleListResponse = {
  items: Article[]
}

async function handleResponse<T>(res: Response): Promise<T> {
  if (!res.ok) {
    const text = await res.text()
    throw new Error(`API error ${res.status}: ${text}`)
  }
  return res.json() as Promise<T>
}

export async function getArticles(params: {
  q?: string
  sentiment?: string
  source?: string
  from?: string
  to?: string
  sort?: string
}): Promise<ArticleListResponse> {
  const qs = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value) qs.set(key, value)
  })
  const res = await fetch(`${API_BASE}/articles?${qs.toString()}`)
  return handleResponse<ArticleListResponse>(res)
}

export async function getArticle(id: string): Promise<Article> {
  const res = await fetch(`${API_BASE}/articles/${id}`)
  return handleResponse<Article>(res)
}

export async function getAnalysis(id: string): Promise<Analysis> {
  const res = await fetch(`${API_BASE}/analyses/${id}`)
  return handleResponse<Analysis>(res)
}

