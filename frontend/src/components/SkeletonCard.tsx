export default function SkeletonCard() {
  return (
    <div className="animate-pulse border border-primary/20 bg-white p-6 shadow-sharp">
      <div className="h-5 w-3/4 bg-accent/30" />
      <div className="mt-3 h-4 w-1/2 bg-accent/30" />
      <div className="mt-4 space-y-2">
        <div className="h-3 w-full bg-accent/30" />
        <div className="h-3 w-5/6 bg-accent/30" />
      </div>
    </div>
  )
}

