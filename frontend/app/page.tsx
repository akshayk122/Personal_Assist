'use client';

import { useState } from 'react';

export default function Home() {
  const [input, setInput] = useState('');
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;
    
    setIsLoading(true);
    try {
      const res = await fetch('http://localhost:8400/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: input  // This matches the API's QueryRequest model
        })
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || `HTTP error! status: ${res.status}`);
      }
      
      const data = await res.json();
      setResponse(data.message || 'No response received');
    } catch (error) {
      console.error('Error:', error);
      setResponse(`Error: ${error instanceof Error ? error.message : 'Failed to get response'}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8 text-center">
          AI Assistant
        </h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {/* Input Section */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-700 mb-4">
              Your Message
            </h2>
            <form onSubmit={handleSubmit} className="space-y-4">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                className="w-full h-64 p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
                placeholder="Type your message here..."
              />
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className={`w-full py-3 px-4 rounded-lg text-white font-medium ${
                  isLoading || !input.trim()
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-blue-600 hover:bg-blue-700'
                }`}
              >
                {isLoading ? 'Processing...' : 'Submit'}
              </button>
            </form>
          </div>

          {/* Response Section */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-700 mb-4">
              Response
            </h2>
            <div className={`h-64 p-4 bg-gray-50 rounded-lg overflow-auto ${
              isLoading ? 'animate-pulse' : ''
            }`}>
              {isLoading ? (
                <div className="flex items-center justify-center h-full">
                  <div className="text-gray-500">Processing your request...</div>
                </div>
              ) : response ? (
                <pre className="whitespace-pre-wrap text-gray-700">{response}</pre>
              ) : (
                <div className="text-gray-500 text-center h-full flex items-center justify-center">
                  Response will appear here
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </main>
  );
} 