'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function Nav() {
  const pathname = usePathname();

  const links = [
    { href: '/', label: 'Upload' },
    { href: '/documents', label: 'Documents' },
  ];

  return (
    <nav className="flex-shrink-0 border-b border-[#2a2a3a] bg-[#0c0c12] px-6 py-2.5 flex items-center justify-between">
      <Link href="/" className="text-sm font-bold tracking-tight text-neutral-300 hover:text-white transition-colors">
        VOS
      </Link>
      <div className="flex items-center gap-4">
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
    </nav>
  );
}
