import type { Metadata } from 'next';
import './globals.css';
import { Header } from '@/components/layout/Header';

export const metadata: Metadata = {
  title: 'SkyGuard AI — Self-Healing Edge-to-Cloud Anomaly Detection for AWS',
  description:
    'Real-time 3D Digital Twin and multivariate deep learning anomaly detection for Automatic Weather Stations.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#080c14] text-slate-100 antialiased flex flex-col selection:bg-cyan-500/30 selection:text-cyan-200">
        <Header />
        <main className="flex-1 flex flex-col overflow-hidden">{children}</main>
      </body>
    </html>
  );
}
