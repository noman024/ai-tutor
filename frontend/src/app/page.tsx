'use client';

import React from 'react';
import { useRouter } from 'next/navigation';

export default function Home(): React.JSX.Element {
  const router = useRouter();
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-between font-mono text-sm">
        <h1 className="text-4xl font-bold text-center mb-8">
          Welcome to AI Tutor
        </h1>
        <p className="text-center text-lg mb-8">
          Your personalized learning platform powered by AI
        </p>
        <div className="flex justify-center space-x-4 mb-6">
          <button className="btn-primary" onClick={() => router.push('/register')}>
            Get Started
          </button>
          <button className="btn-secondary" onClick={() => router.push('/about')}>
            Learn More
          </button>
        </div>
        <div className="flex justify-center space-x-4">
          <button className="btn-secondary" onClick={() => router.push('/register')}>
            Register
          </button>
          <button className="btn-secondary" onClick={() => router.push('/login')}>
            Login
          </button>
        </div>
      </div>
    </main>
  );
} 