import React from 'react';

export default function AboutPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="bg-white p-8 rounded shadow-md w-full max-w-2xl">
        <h2 className="text-3xl font-bold mb-4 text-center">About AI Tutor</h2>
        <p className="mb-4 text-lg text-center">
          <strong>AI Tutor</strong> is an innovative educational platform that combines AI-powered teaching with interactive visualizations and lab simulations. Our mission is to provide personalized, engaging, and effective learning experiences for every student.
        </p>
        <ul className="list-disc pl-6 mb-4">
          <li>Personalized AI-powered teaching</li>
          <li>Interactive whiteboard and lab simulations</li>
          <li>Voice and visual explanations</li>
          <li>Support for file uploads (PDF, PPT, DOC, images)</li>
          <li>Progressive learning and real-time Q&A</li>
        </ul>
        <p className="text-center text-gray-600">
          Whether you are a student, educator, or lifelong learner, AI Tutor is here to help you master complex topics and enjoy the journey of learning!
        </p>
      </div>
    </div>
  );
} 