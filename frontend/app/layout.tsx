import type { Metadata, Viewport } from 'next'
import './globals.css'
import { Nav } from './components/Nav'

export const metadata: Metadata = {
  title: 'VOS - Document Review',
  description: 'Voxora · Opinari · Scrutara — AI-powered multi-persona document review',
}

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 1,
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#0a0a0f] text-[#e4e4ec] antialiased overflow-x-hidden">
        <Nav />
        {children}
      </body>
    </html>
  )
}
