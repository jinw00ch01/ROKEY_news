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

export function SentimentBadge({ label }: { label?: string }) {
  if (!label) return null
  const color =
    label === 'positive'
      ? 'bg-sentiment-positive/10 text-sentiment-positive'
      : label === 'negative'
        ? 'bg-sentiment-negative/10 text-sentiment-negative'
        : 'bg-sentiment-neutral/10 text-sentiment-neutral'
  return (
    <span className={`px-3 py-1.5 text-xs font-medium ${color}`}>
      {sentimentLabelMap[label] ?? label}
    </span>
  )
}

export default function ArticleCard({ article }: Props) {
  return (
    <article className="border border-primary/20 bg-white p-6 shadow-sharp transition-all duration-150 hover:-translate-y-0.5">
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-4">
          <Link
            to={`/article/${article.id}`}
            className="text-lg font-semibold text-gray-900 hover:text-primary"
          >
            {article.title}
          </Link>
          <div className="text-sm text-gray-600">
            {article.published_at
              ? new Date(article.published_at).toLocaleString()
              : '발행일 미상'}
          </div>
          {article.summary && (
            <p className="text-sm text-gray-700 max-h-16 overflow-hidden">{article.summary}</p>
          )}
          {article.keywords && article.keywords.length > 0 && (
            <div className="flex flex-wrap gap-2">
              {article.keywords.map((kw) => (
                <span
                  key={kw}
                  className="bg-accent/20 px-3 py-1 text-xs text-secondary"
                >
                  {kw}
                </span>
              ))}
            </div>
          )}
        </div>
        {article.sentiment_label && <SentimentBadge label={article.sentiment_label} />}
      </div>
    </article>
  )
}

