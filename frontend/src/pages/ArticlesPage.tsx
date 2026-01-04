import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import { getArticles } from '../api'
import ArticleCard from '../components/ArticleCard'
import FilterBar from '../components/FilterBar'

export default function ArticlesPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const q = searchParams.get('q') ?? ''
  const sentiment = searchParams.get('sentiment') ?? ''

  const queryParams = useMemo(() => ({ q, sentiment }), [q, sentiment])

  const { data, isLoading, error } = useQuery({
    queryKey: ['articles', queryParams],
    queryFn: () => getArticles(queryParams),
  })

  const handleFilter = (params: { q: string; sentiment: string }) => {
    const next = new URLSearchParams(searchParams)
    params.q ? next.set('q', params.q) : next.delete('q')
    params.sentiment ? next.set('sentiment', params.sentiment) : next.delete('sentiment')
    setSearchParams(next)
  }

  return (
    <div className="space-y-4">
      <FilterBar defaultSearch={q} defaultSentiment={sentiment} onChange={handleFilter} />
      {isLoading && <div className="text-sm text-slate-500">불러오는 중...</div>}
      {error && (
        <div className="text-sm text-red-600">
          데이터를 불러오지 못했습니다: {(error as Error).message}
        </div>
      )}
      {!isLoading && data && data.items.length === 0 && (
        <div className="text-sm text-slate-500">표시할 기사가 없습니다.</div>
      )}
      <div className="grid gap-3">
        {data?.items.map((article) => (
          <ArticleCard key={article.id} article={article} />
        ))}
      </div>
    </div>
  )
}

