import Header from '@/components/Header.server';
import Footer from '@/components/Footer.server';
import '@/styles/globals.css';
import Script from 'next/script'

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

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={inter.variable}>
      <head>
        <Script
          strategy="afterInteractive"
          src="https://www.googletagmanager.com/gtag/js?id=G-ZT9SKBMMYE"
        />
        <Script
          id="gtag-init"
          strategy="afterInteractive"
          dangerouslySetInnerHTML={{
            __html: `
              window.dataLayer = window.dataLayer || [];
              function gtag(){dataLayer.push(arguments);}
              gtag('js', new Date());
              gtag('config', 'G-ZT9SKBMMYE', { page_path: window.location.pathname });
            `,
          }}
        />

      </head>
      <body className="min-h-screen min-w-screen bg-gray-50">
        <Header />
        {children}
        <Footer />
      </body>
    </html>
  );
}
