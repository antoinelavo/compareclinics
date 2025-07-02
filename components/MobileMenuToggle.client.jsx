// components/MobileMenuToggle.client.jsx
'use client';

import { useState } from 'react';
import Link from 'next/link';

export default function MobileMenuToggle() {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <>
      {/* Hamburger button (only on mobile) */}
      <button
        onClick={() => setSidebarOpen(true)}
        className="lg:hidden cursor-pointer p-2"
        aria-label="Open menu"
      >
        <svg viewBox="0 0 100 100" width="30" height="30" xmlns="http://www.w3.org/2000/svg">
          <path d="M20 40 H80" stroke="#000" strokeWidth="4" strokeLinecap="round" />
          <path d="M20 60 H80" stroke="#000" strokeWidth="4" strokeLinecap="round" />
          <path d="M20 80 H80" stroke="#000" strokeWidth="4" strokeLinecap="round" />
        </svg>
      </button>

      {/* Sidebar overlay */}
      {sidebarOpen && (
        <ul className="fixed top-0 right-0 h-screen w-[250px] bg-white shadow-xl flex flex-col items-center gap-[3em] pt-8 z-[999]">
          {/* Close button */}
          <li className="mb-8">
            <button
              onClick={() => setSidebarOpen(false)}
              aria-label="Close menu"
            >
              <svg viewBox="0 0 100 100" width="30" height="30" xmlns="http://www.w3.org/2000/svg">
                <path d="M20 20 L80 80" stroke="#000" strokeWidth="4" strokeLinecap="round" />
                <path d="M80 20 L20 80" stroke="#000" strokeWidth="4" strokeLinecap="round" />
              </svg>
            </button>
          </li>

          {[
            ['Blog', '/blog']
          ].map(([label, href]) => (
            <li key={href} className="w-full text-center">
              <Link 
                href={href}
                className="block w-full py-4 text-sm text-black hover:text-blue-500"
                onClick={() => setSidebarOpen(false)}
              >
                {label}
              </Link>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}