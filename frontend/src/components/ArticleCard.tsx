import { Link } from 'react-router-dom'
import type { Article } from '../api'

type Props = {
  article: Article
}

const sentimentLabelMap: Record<string, string> = {
  positive: '긍정',
  neutral: '중립',
  negative: '부정',
}

export function sentimentBadge(label?: string) {
  if (!label) return null
  const color =
    label === 'positive'
      ? 'bg-sentiment-positive/10 text-sentiment-positive'
      : label === 'negative'
        ? 'bg-sentiment-negative/10 text-sentiment-negative'
        : 'bg-sentiment-neutral/10 text-sentiment-neutral'
  return (
    <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${color}`}>
      {sentimentLabelMap[label] ?? label}
    </span>
  )
}

export default function ArticleCard({ article }: Props) {
  return (
    <article className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-start justify-between gap-2">
        <div className="space-y-2">
          <Link
            to={`/article/${article.id}`}
            className="text-lg font-semibold text-slate-900 hover:underline"
          >
            {article.title}
          </Link>
          <div className="text-sm text-slate-500">
            {article.published_at
              ? new Date(article.published_at).toLocaleString()
              : '발행일 미상'}
          </div>
          {article.summary && (
            <p className="text-sm text-slate-700 max-h-16 overflow-hidden">{article.summary}</p>
          )}
          {article.keywords && article.keywords.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {article.keywords.map((kw) => (
                <span
                  key={kw}
                  className="rounded-full bg-slate-100 px-2 py-1 text-xs text-slate-600"
                >
                  {kw}
                </span>
              ))}
            </div>
          )}
        </div>
        {sentimentBadge(article.sentiment_label)}
      </div>
    </article>
  )
}

