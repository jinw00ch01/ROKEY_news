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
    if (params.q) next.set('q', params.q); else next.delete('q')
    if (params.sentiment) next.set('sentiment', params.sentiment); else next.delete('sentiment')
    if (params.source) next.set('source', params.source); else next.delete('source')
    if (params.from) next.set('from', params.from); else next.delete('from')
    if (params.to) next.set('to', params.to); else next.delete('to')
    if (params.sort) next.set('sort', params.sort); else next.delete('sort')
    setSearchParams(next)
  }

  return (
    <div className="space-y-16">
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
        <div className="grid grid-cols-4 gap-8 lg:grid-cols-3 md:grid-cols-2 sm:grid-cols-1">
          {[1, 2, 3, 4].map((k) => (
            <SkeletonCard key={k} />
          ))}
        </div>
      )}
      {error && (
        <div className="text-sm text-error">
          데이터를 불러오지 못했습니다: {(error as Error).message}
        </div>
      )}
      {!isLoading && data && data.items.length === 0 && (
        <div className="text-sm text-gray-600">표시할 기사가 없습니다.</div>
      )}
      <div className="grid grid-cols-4 gap-8 lg:grid-cols-3 md:grid-cols-2 sm:grid-cols-1">
        {data?.items.map((article) => (
          <ArticleCard key={article.id} article={article} />
        ))}
      </div>
    </div>
  )
}

