'use client';

import { useEffect } from 'react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error('Page error:', error);
  }, [error]);

  return (
    <div className="min-h-screen flex items-center justify-center px-6">
      <div className="text-center max-w-md">
        <div className="text-5xl mb-4">!</div>
        <h2 className="text-xl font-semibold text-[#e4e4ec] mb-2">Something went wrong</h2>
        <p className="text-sm text-[#8a8a9a] mb-6">
          {error.message || 'An unexpected error occurred. Please try again.'}
        </p>
        <div className="flex gap-3 justify-center">
          <button
            onClick={reset}
            className="px-5 py-2 bg-indigo-600 hover:bg-indigo-700 rounded-lg text-sm font-medium transition-colors"
          >
            Try again
          </button>
          <a
            href="/"
            className="px-5 py-2 border border-[#2a2a3a] hover:border-[#3a3a4a] rounded-lg text-sm text-[#8a8a9a] hover:text-[#c4c4d4] transition-colors"
          >
            Go home
          </a>
        </div>
      </div>
    </div>
  );
}
