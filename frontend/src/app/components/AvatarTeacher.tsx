import React from 'react';

interface AvatarTeacherProps {
  state: 'idle' | 'thinking' | 'answering';
}

export default function AvatarTeacher({ state }: AvatarTeacherProps) {
  // Simple SVG avatar (can be replaced with a more advanced one later)
  // Add a pulsing animation for 'thinking', and a smile for 'answering'
  return (
    <div className="flex flex-col items-center mb-4">
      <div className={`transition-all duration-300 ${state === 'thinking' ? 'animate-pulse' : ''}`}>
        {/* SVG Avatar */}
        <svg width="80" height="80" viewBox="0 0 80 80" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="40" cy="40" r="38" fill="#E0E7FF" stroke="#6366F1" strokeWidth="4" />
          <ellipse cx="40" cy="38" rx="20" ry="22" fill="#fff" stroke="#6366F1" strokeWidth="2" />
          <ellipse cx="40" cy="32" rx="8" ry="7" fill="#6366F1" />
          {/* Eyes */}
          <ellipse cx="36" cy="36" rx="2" ry="2.5" fill="#222" />
          <ellipse cx="44" cy="36" rx="2" ry="2.5" fill="#222" />
          {/* Smile or neutral */}
          {state === 'answering' ? (
            <path d="M36 44 Q40 48 44 44" stroke="#222" strokeWidth="2" fill="none" />
          ) : (
            <path d="M36 44 Q40 46 44 44" stroke="#222" strokeWidth="2" fill="none" />
          )}
        </svg>
      </div>
      <div className="mt-2 text-sm text-gray-700">
        {state === 'idle' && 'Your AI Teacher is ready!'}
        {state === 'thinking' && 'Thinking...'}
        {state === 'answering' && 'Here is your answer!'}
      </div>
    </div>
  );
} 