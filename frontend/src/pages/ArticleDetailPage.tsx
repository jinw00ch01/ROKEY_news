import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { getArticle } from '../api'
import { sentimentBadge } from '../components/ArticleCard'

export default function ArticleDetailPage() {
  const { id } = useParams<{ id: string }>()

  const { data, isLoading, error } = useQuery({
    queryKey: ['article', id],
    queryFn: () => getArticle(id || ''),
    enabled: Boolean(id),
  })

  if (isLoading) return <div className="text-sm text-slate-500">불러오는 중...</div>
  if (error) {
    return (
      <div className="text-sm text-red-600">
        데이터를 불러오지 못했습니다: {(error as Error).message}
      </div>
    )
  }
  if (!data) return null

  return (
    <div className="space-y-4">
      <Link to="/" className="text-sm text-slate-600 hover:underline">
        ← 목록으로
      </Link>
      <div className="space-y-3 rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex items-start justify-between gap-2">
          <div>
            <h1 className="text-2xl font-semibold text-slate-900">{data.title}</h1>
            <div className="mt-2 text-sm text-slate-500">
              {data.published_at
                ? new Date(data.published_at).toLocaleString()
                : '발행일 미상'}
            </div>
          </div>
          {sentimentBadge(data.sentiment_label)}
        </div>
        {data.summary && <p className="text-base text-slate-800">{data.summary}</p>}
        {data.keywords && data.keywords.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {data.keywords.map((kw) => (
              <span
                key={kw}
                className="rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-600"
              >
                {kw}
              </span>
            ))}
          </div>
        )}
        <div className="pt-2 text-sm">
          <a
            href={data.link}
            target="_blank"
            rel="noreferrer"
            className="text-slate-700 underline"
          >
            원문 보기
          </a>
        </div>
      </div>
    </div>
  )
}

