import Header from '@/components/Header.server';
import Footer from '@/components/Footer.server';
import '@/styles/globals.css';
import { Inter } from "next/font/google";

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',    // optional: if you want to expose it as a CSS variable
  weight: ['400', '700'],       // choose the font-weights you need
  display: 'swap',              // recommended for performance
})
export const metadata = {
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({ Component, pageProps }) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="min-h-screen min-w-screen bg-gray-50">
        <Header />
        <Component {...pageProps} />
        <Footer />
      </body>
    </html>
  );
}
