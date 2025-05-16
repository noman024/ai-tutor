"use client";
import React, { useEffect, useState } from 'react';
import Link from 'next/link';

export default function Navbar() {
  const [loggedIn, setLoggedIn] = useState(false);
  useEffect(() => {
    setLoggedIn(!!localStorage.getItem('token'));
    const handler = () => setLoggedIn(!!localStorage.getItem('token'));
    window.addEventListener('storage', handler);
    return () => window.removeEventListener('storage', handler);
  }, []);
  return (
    <nav className="bg-white shadow mb-8">
      <div className="container mx-auto px-4 py-3 flex justify-between items-center">
        <Link href="/" className="text-xl font-bold text-blue-700">AI Tutor</Link>
        <div className="space-x-4">
          <Link href="/about" className="hover:text-blue-600">About</Link>
          {loggedIn && <Link href="/dashboard" className="hover:text-blue-600">Dashboard</Link>}
          {!loggedIn && <Link href="/login" className="hover:text-blue-600">Login</Link>}
          {!loggedIn && <Link href="/register" className="hover:text-blue-600">Register</Link>}
          {loggedIn && <button onClick={() => {localStorage.removeItem('token'); setLoggedIn(false); window.location.href = '/login';}} className="hover:text-blue-600">Logout</button>}
        </div>
      </div>
    </nav>
  );
} 