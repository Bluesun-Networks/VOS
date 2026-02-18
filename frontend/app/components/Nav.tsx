'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const links = [
  { href: '/', label: 'Upload' },
  { href: '/documents', label: 'Documents' },
];

export function Nav() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  // Hide nav on document detail pages (they have their own top bar)
  if (pathname.match(/^\/documents\/[^/]+$/)) return null;

  return (
    <nav className="flex-shrink-0 border-b border-[#2a2a3a] bg-[#0c0c12] px-4 sm:px-6 py-2.5">
      <div className="flex items-center justify-between">
        <Link href="/" className="text-sm font-bold tracking-tight text-neutral-300 hover:text-white transition-colors">
          VOS
        </Link>

        {/* Desktop links */}
        <div className="hidden sm:flex items-center gap-4">
          {links.map(({ href, label }) => {
            const isActive = href === '/' ? pathname === '/' : pathname.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                className={`text-xs tracking-wide uppercase transition-colors ${
                  isActive
                    ? 'text-indigo-400'
                    : 'text-neutral-500 hover:text-neutral-300'
                }`}
              >
                {label}
              </Link>
            );
          })}
        </div>

        {/* Mobile hamburger */}
        <button
          onClick={() => setMobileOpen(!mobileOpen)}
          className="sm:hidden p-1.5 text-neutral-400 hover:text-white transition-colors touch-manipulation"
          aria-label="Toggle menu"
        >
          {mobileOpen ? (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          ) : (
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          )}
        </button>
      </div>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="sm:hidden pt-2 pb-1 space-y-1">
          {links.map(({ href, label }) => {
            const isActive = href === '/' ? pathname === '/' : pathname.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                onClick={() => setMobileOpen(false)}
                className={`block py-2 px-2 rounded-md text-sm transition-colors ${
                  isActive
                    ? 'text-indigo-400 bg-indigo-500/10'
                    : 'text-neutral-400 hover:text-white hover:bg-[#1a1a25]'
                }`}
              >
                {label}
              </Link>
            );
          })}
        </div>
      )}
    </nav>
  );
}

export default Nav;
