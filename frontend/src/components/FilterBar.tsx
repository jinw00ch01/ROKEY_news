import { useState, type FormEvent } from 'react'

type Props = {
  defaultSearch?: string
  defaultSentiment?: string
  onChange: (params: { q: string; sentiment: string }) => void
}

const sentimentOptions = [
  { value: '', label: '전체' },
  { value: 'positive', label: '긍정' },
  { value: 'neutral', label: '중립' },
  { value: 'negative', label: '부정' },
]

export default function FilterBar({ defaultSearch = '', defaultSentiment = '', onChange }: Props) {
  const [q, setQ] = useState(defaultSearch)
  const [sentiment, setSentiment] = useState(defaultSentiment)

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    onChange({ q, sentiment })
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="mb-4 flex flex-col gap-3 rounded-lg border border-slate-200 bg-white p-4 shadow-sm md:flex-row md:items-center"
    >
      <div className="flex flex-1 items-center gap-2">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="검색어(제목/본문/키워드)"
          className="w-full rounded-md border border-slate-200 px-3 py-2 text-sm shadow-inner focus:border-slate-400 focus:outline-none"
        />
      </div>
      <div className="flex items-center gap-2">
        <select
          value={sentiment}
          onChange={(e) => setSentiment(e.target.value)}
          className="rounded-md border border-slate-200 px-3 py-2 text-sm shadow-inner focus:border-slate-400 focus:outline-none"
        >
          {sentimentOptions.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
        <button
          type="submit"
          className="rounded-md bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-800"
        >
          적용
        </button>
      </div>
    </form>
  )
}

