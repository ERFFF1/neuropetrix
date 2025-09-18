import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'NeuroPETRIX v3.0',
  description: 'AI-Powered Medical Imaging Analysis Platform',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
