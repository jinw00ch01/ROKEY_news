import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useSearchParams } from 'react-router-dom'
import { getArticles } from '../api'
import ArticleCard from '../components/ArticleCard'
import FilterBar from '../components/FilterBar'
import SkeletonCard from '../components/SkeletonCard'

export default function ArticlesPage() {
  const [searchParams, setSearchParams] = useSearchParams()
  const q = searchParams.get('q') ?? ''
  const sentiment = searchParams.get('sentiment') ?? ''
  const source = searchParams.get('source') ?? ''
  const from = searchParams.get('from') ?? ''
  const to = searchParams.get('to') ?? ''
  const sort = searchParams.get('sort') ?? 'published_desc'

  const queryParams = useMemo(() => ({ q, sentiment, source, from, to, sort }), [q, sentiment, source, from, to, sort])

  const { data, isLoading, error } = useQuery({
    queryKey: ['articles', queryParams],
    queryFn: () => getArticles(queryParams),
  })

  const handleFilter = (params: { q: string; sentiment: string; source: string; from: string; to: string; sort: string }) => {
    const next = new URLSearchParams(searchParams)
    params.q ? next.set('q', params.q) : next.delete('q')
    params.sentiment ? next.set('sentiment', params.sentiment) : next.delete('sentiment')
    params.source ? next.set('source', params.source) : next.delete('source')
    params.from ? next.set('from', params.from) : next.delete('from')
    params.to ? next.set('to', params.to) : next.delete('to')
    params.sort ? next.set('sort', params.sort) : next.delete('sort')
    setSearchParams(next)
  }

  return (
    <div className="space-y-4">
      <FilterBar
        defaultSearch={q}
        defaultSentiment={sentiment}
        defaultSource={source}
        defaultFrom={from}
        defaultTo={to}
        defaultSort={sort}
        onChange={handleFilter}
      />
      {isLoading && (
        <div className="grid gap-3">
          {[1, 2, 3].map((k) => (
            <SkeletonCard key={k} />
          ))}
        </div>
      )}
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

