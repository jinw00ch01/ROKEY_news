import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { getArticle } from '../api'
import { SentimentBadge } from '../components/ArticleCard'

export default function ArticleDetailPage() {
  const { id } = useParams<{ id: string }>()

  const { data, isLoading, error } = useQuery({
    queryKey: ['article', id],
    queryFn: () => getArticle(id || ''),
    enabled: Boolean(id),
  })

  if (isLoading) return <div className="text-sm text-gray-600">불러오는 중...</div>
  if (error) {
    return (
      <div className="text-sm text-error">
        데이터를 불러오지 못했습니다: {(error as Error).message}
      </div>
    )
  }
  if (!data) return null

  return (
    <div className="space-y-8">
      <Link to="/" className="inline-block text-sm text-primary transition-all duration-150 hover:-translate-x-1 hover:text-secondary">
        ← 목록으로
      </Link>
      <div className="space-y-6 border border-primary/20 bg-white p-10 shadow-sharp">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">{data.title}</h1>
            <div className="mt-3 text-sm text-gray-600">
              {data.published_at
                ? new Date(data.published_at).toLocaleString()
                : '발행일 미상'}
            </div>
          </div>
          {data.sentiment_label && <SentimentBadge label={data.sentiment_label} />}
        </div>
        {data.summary && <p className="text-base leading-relaxed text-gray-800">{data.summary}</p>}
        {data.keywords && data.keywords.length > 0 && (
          <div className="flex flex-wrap gap-2">
            {data.keywords.map((kw) => (
              <span
                key={kw}
                className="bg-accent/20 px-3 py-1.5 text-xs text-secondary"
              >
                {kw}
              </span>
            ))}
          </div>
        )}
        <div className="pt-4 text-sm">
          <a
            href={data.link}
            target="_blank"
            rel="noreferrer"
            className="text-primary underline transition-all duration-150 hover:text-secondary"
          >
            원문 보기
          </a>
        </div>
      </div>
    </div>
  )
}

