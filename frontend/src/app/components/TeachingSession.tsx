import React, { useEffect, useState } from 'react';
import AvatarTeacher from './AvatarTeacher';

interface Slide {
  slide_number: number;
  content?: string;
  image_available?: boolean;
}

interface TeachingSessionProps {
  selectedSlideDeckId: number | null;
}

export default function TeachingSession({ selectedSlideDeckId }: TeachingSessionProps) {
  const [slides, setSlides] = useState<Slide[]>([]);
  const [current, setCurrent] = useState(0);
  const [loadingSlides, setLoadingSlides] = useState(false);
  const [explanation, setExplanation] = useState<string | null>(null);
  const [explaining, setExplaining] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  useEffect(() => {
    if (!selectedSlideDeckId) {
      setSlides([]);
      setCurrent(0);
      setExplanation(null);
      return;
    }
    setLoadingSlides(true);
    setError(null);
    fetch(`${apiUrl}/api/v1/ai/slides/${selectedSlideDeckId}`, {
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch slides');
        return res.json();
      })
      .then(data => {
        setSlides(data.slides || []);
        setCurrent(0);
        setExplanation(null);
      })
      .catch(err => setError(err.message))
      .finally(() => setLoadingSlides(false));
  }, [selectedSlideDeckId, apiUrl]);

  useEffect(() => {
    setImageUrl(null);
    if (
      selectedSlideDeckId &&
      slides.length > 0 &&
      slides[current]?.image_available
    ) {
      const fetchImage = async () => {
        try {
          const res = await fetch(
            `${apiUrl}/api/v1/ai/slide-image/${selectedSlideDeckId}/${slides[current].slide_number}`,
            {
              headers: {
                Authorization: `Bearer ${localStorage.getItem('token')}`,
              },
            }
          );
          if (!res.ok) throw new Error('Failed to fetch image');
          const blob = await res.blob();
          const url = URL.createObjectURL(blob);
          setImageUrl(url);
        } catch (err) {
          setImageUrl(null);
        }
      };
      fetchImage();
      // Cleanup blob URL on slide change
      return () => {
        if (imageUrl) URL.revokeObjectURL(imageUrl);
      };
    }
  }, [selectedSlideDeckId, slides, current, apiUrl]);

  const handlePrev = () => {
    setCurrent(c => Math.max(0, c - 1));
    setExplanation(null);
  };
  const handleNext = () => {
    setCurrent(c => Math.min(slides.length - 1, c + 1));
    setExplanation(null);
  };

  const handleExplain = async () => {
    if (!selectedSlideDeckId || !slides[current]) return;
    setExplaining(true);
    setError(null);
    setExplanation(null);
    try {
      const res = await fetch(`${apiUrl}/api/v1/ai/explain-slide`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({
          slide_deck_id: selectedSlideDeckId,
          slide_number: slides[current].slide_number
        })
      });
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to get explanation');
      }
      const data = await res.json();
      setExplanation(data.explanation);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get explanation');
    } finally {
      setExplaining(false);
    }
  };

  if (!selectedSlideDeckId) return null;

  return (
    <div className="bg-white p-4 md:p-6 rounded-lg shadow border border-gray-200 my-4 md:my-8">
      <h2 className="text-xl font-semibold mb-4">Teaching Session</h2>
      <AvatarTeacher state={explaining ? 'thinking' : explanation ? 'answering' : 'idle'} />
      {loadingSlides ? (
        <div className="flex items-center justify-center h-64">
          <div className="text-gray-600">Loading slides...</div>
        </div>
      ) : error ? (
        <div className="text-red-600 p-4 bg-red-50 rounded">{error}</div>
      ) : slides.length === 0 ? (
        <div className="text-gray-500 p-4 bg-gray-50 rounded">No slides found for this deck.</div>
      ) : (
        <>
          <div className="mb-4">
            <div className="font-bold mb-2 text-center md:text-left">Slide {slides[current].slide_number} of {slides.length}</div>
            <div className="flex items-center justify-center">
              <div
                className="relative bg-white shadow-lg rounded-lg border mx-auto w-full max-w-4xl"
                style={{
                  aspectRatio: '16/9',
                  minHeight: '360px',
                  maxHeight: 'calc(100vh - 400px)',
                  display: 'flex',
                  flexDirection: 'column',
                  overflow: 'hidden'
                }}
              >
                {slides[current].image_available ? (
                  <div className="w-full h-full flex flex-col justify-start items-center p-4 overflow-hidden">
                    {imageUrl ? (
                      <div className="relative w-full h-full flex flex-col">
                        <div className="flex-1 min-h-0 relative">
                          <img
                            src={imageUrl}
                            alt={`Slide ${slides[current].slide_number}`}
                            className="absolute inset-0 w-full h-full object-contain"
                          />
                        </div>
                        {slides[current].content && (
                          <div className="mt-4 w-full">
                            <div className={`text-xl md:text-2xl font-bold break-words px-2 py-1 rounded transition-colors duration-200 ${explanation ? 'bg-yellow-200' : ''}`}>
                              {slides[current].content.split('\n')[0]}
                            </div>
                          </div>
                        )}
                      </div>
                    ) : (
                      <div className="w-full h-full flex items-center justify-center text-gray-400">
                        (Image unavailable)
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="w-full h-full flex flex-col p-4 overflow-hidden">
                    <div className="flex-1 min-h-0 flex flex-col">
                      {slides[current].content ? (
                        <>
                          <div className={`text-xl md:text-2xl font-bold mb-4 break-words px-2 py-1 rounded transition-colors duration-200 ${explanation ? 'bg-yellow-200' : ''}`}>
                            {slides[current].content.split('\n')[0]}
                          </div>
                          <div className="flex-1 min-h-0 overflow-y-auto custom-scrollbar">
                            <div className="text-base whitespace-pre-line break-words">
                              {slides[current].content.split('\n').slice(1).join('\n')}
                            </div>
                          </div>
                        </>
                      ) : (
                        <div className="flex-1 flex items-center justify-center text-gray-400">
                          (Empty slide)
                        </div>
                      )}
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
          <div className="flex flex-wrap items-center justify-center gap-2 mb-4">
            <button 
              onClick={handlePrev} 
              disabled={current === 0} 
              className="btn-secondary flex-1 md:flex-none min-w-[120px]"
            >
              Previous
            </button>
            <button 
              onClick={handleNext} 
              disabled={current === slides.length - 1} 
              className="btn-secondary flex-1 md:flex-none min-w-[120px]"
            >
              Next
            </button>
            <button 
              onClick={handleExplain} 
              disabled={explaining} 
              className="btn-primary flex-1 md:flex-none min-w-[160px]"
            >
              {explaining ? 'Explaining...' : 'Teach me this slide'}
            </button>
          </div>
          {explanation && (
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded overflow-hidden">
              <div className="font-semibold mb-2">AI Teacher's Explanation:</div>
              <div className="prose max-w-none whitespace-pre-line overflow-y-auto custom-scrollbar" style={{ maxHeight: '300px' }}>
                {explanation}
              </div>
            </div>
          )}
        </>
      )}
      <style jsx global>{`
        .custom-scrollbar {
          scrollbar-width: thin;
          scrollbar-color: #CBD5E0 #EDF2F7;
        }
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
          height: 8px;
        }
        .custom-scrollbar::-webkit-scrollbar-track {
          background: #EDF2F7;
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background-color: #CBD5E0;
          border-radius: 4px;
        }
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background-color: #A0AEC0;
        }
      `}</style>
    </div>
  );
} 