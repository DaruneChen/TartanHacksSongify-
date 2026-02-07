import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Screen to Song',
  description: 'Turn your digital life into a personalized soundtrack',
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
