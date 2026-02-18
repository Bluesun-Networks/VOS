import Link from 'next/link'

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center">
      <h1 className="text-4xl font-bold text-[#e4e4ec]">404</h1>
      <p className="mt-2 text-[#8a8a9a]">Page not found</p>
      <Link href="/" className="mt-6 text-sm text-blue-400 hover:text-blue-300 underline">
        Back to home
      </Link>
    </div>
  )
}
