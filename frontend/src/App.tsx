import { Link, Outlet } from 'react-router-dom'

function App() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900">
      <header className="bg-primary shadow-sharp">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-6">
          <Link to="/" className="text-xl font-bold text-white transition-all duration-150 hover:-translate-y-0.5">
            Rokey News
          </Link>
          <nav className="text-sm text-gray-50">뉴스 요약 · 감성 분석</nav>
        </div>
      </header>
      <main className="mx-auto max-w-5xl px-6 py-20">
        <Outlet />
      </main>
    </div>
  )
}

export default App
