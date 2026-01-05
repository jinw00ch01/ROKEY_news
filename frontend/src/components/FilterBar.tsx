import { useState, type FormEvent } from 'react'

type Props = {
  defaultSearch?: string
  defaultSentiment?: string
  defaultSource?: string
  defaultFrom?: string
  defaultTo?: string
  defaultSort?: string
  onChange: (params: { q: string; sentiment: string; source: string; from: string; to: string; sort: string }) => void
}

const sentimentOptions = [
  { value: '', label: '전체' },
  { value: 'positive', label: '긍정' },
  { value: 'neutral', label: '중립' },
  { value: 'negative', label: '부정' },
]

const sortOptions = [
  { value: 'published_desc', label: '최신순' },
  { value: 'score_desc', label: '감성점수순' },
]

export default function FilterBar({
  defaultSearch = '',
  defaultSentiment = '',
  defaultSource = '',
  defaultFrom = '',
  defaultTo = '',
  defaultSort = 'published_desc',
  onChange,
}: Props) {
  const [q, setQ] = useState(defaultSearch)
  const [sentiment, setSentiment] = useState(defaultSentiment)
  const [source, setSource] = useState(defaultSource)
  const [fromDate, setFromDate] = useState(defaultFrom)
  const [toDate, setToDate] = useState(defaultTo)
  const [sort, setSort] = useState(defaultSort)

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    onChange({ q, sentiment, source, from: fromDate, to: toDate, sort })
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="mb-8 grid gap-8 border border-primary/20 bg-white p-6 shadow-sharp md:grid-cols-5 md:items-center"
    >
      <div className="md:col-span-2 flex items-center gap-2">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="검색어(제목/본문/키워드)"
          className="w-full border border-primary/30 px-3 py-2 text-sm shadow-inner focus:border-primary focus:outline-none"
        />
      </div>
      <div className="flex items-center gap-2">
        <input
          value={source}
          onChange={(e) => setSource(e.target.value)}
          placeholder="출처"
          className="w-32 border border-primary/30 px-3 py-2 text-sm shadow-inner focus:border-primary focus:outline-none"
        />
        <select
          value={sentiment}
          onChange={(e) => setSentiment(e.target.value)}
          className="border border-primary/30 px-3 py-2 text-sm shadow-inner focus:border-primary focus:outline-none"
        >
          {sentimentOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <select
          value={sort}
          onChange={(e) => setSort(e.target.value)}
          className="border border-primary/30 px-3 py-2 text-sm shadow-inner focus:border-primary focus:outline-none"
        >
          {sortOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <button
          type="submit"
          className="bg-primary px-5 py-2 text-sm font-semibold text-white transition-all duration-150 hover:-translate-y-0.5 hover:bg-secondary"
        >
          적용
        </button>
      </div>
      <div className="flex items-center gap-2">
        <input
          type="date"
          value={fromDate}
          onChange={(e) => setFromDate(e.target.value)}
          className="border border-primary/30 px-3 py-2 text-sm shadow-inner focus:border-primary focus:outline-none"
        />
        <input
          type="date"
          value={toDate}
          onChange={(e) => setToDate(e.target.value)}
          className="border border-primary/30 px-3 py-2 text-sm shadow-inner focus:border-primary focus:outline-none"
        />
      </div>
    </form>
  )
}

