'use client';

import { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Label } from '@/components/ui/label';
import { Sparkles, Send, Lightbulb, Loader2, Pencil } from 'lucide-react';

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
          message: input
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
    <div className="min-h-screen flex flex-col relative">
      {/* Background image with overlay */}
      <div className="fixed inset-0 -z-10">
        <img
          src="/personal_assistant.png"
          alt="Personal Assistant Background"
          className="w-full h-full object-cover object-center opacity-60"
        />
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50/80 via-white/70 to-blue-200/80" />
      </div>

      {/* Sticky Header */}
      <header className="sticky top-0 z-30 w-full bg-white/80 backdrop-blur border-b border-blue-100 shadow-sm animate-fade-in-down">
        <div className="max-w-5xl mx-auto flex items-center gap-3 py-3 px-4">
          <span className="bg-gradient-to-tr from-blue-400 via-blue-300 to-blue-100 rounded-full p-2 shadow-lg">
            <Sparkles className="w-7 h-7 text-blue-700" />
          </span>
          <span className="text-2xl font-extrabold text-blue-900 tracking-tight font-serif drop-shadow-sm">Personal Assistant</span>
          <span className="ml-auto text-xs text-blue-400 font-mono tracking-widest">v1.0</span>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 flex items-center justify-center py-8 px-2 md:px-0 animate-fade-in-up">
        <div className="w-full max-w-5xl mx-auto rounded-2xl shadow-2xl bg-white/90 backdrop-blur-md p-6 md:p-12 border border-blue-100">
          <div className="flex flex-col items-center mb-8">
            <h1 className="text-4xl md:text-5xl font-extrabold text-blue-900 mb-1 text-center tracking-tight drop-shadow-sm">
              <span className="text-blue-600">My Assistant</span>
            </h1>
            <p className="text-center text-lg text-blue-700 font-medium">Your smart meeting & expense companion</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-10">
            {/* Input Section */}
            <Card className="bg-white/95 rounded-xl shadow-md flex flex-col border border-blue-100 hover:shadow-lg transition-shadow duration-200">
              <CardHeader className="flex flex-row items-center gap-2 pb-2">
                <Pencil className="text-blue-400 w-5 h-5" />
                <CardTitle className="text-xl font-semibold text-blue-800">Your Message</CardTitle>
              </CardHeader>
              <CardContent className="flex flex-col flex-1 gap-4">
                <form onSubmit={handleSubmit} className="flex flex-col flex-1 gap-4">
                  <Label htmlFor="user-message" className="sr-only">Message</Label>
                  <Textarea
                    id="user-message"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    className="h-40 md:h-64 text-blue-900 bg-white/60 placeholder:text-blue-400 font-medium transition-all duration-200 border-2 border-blue-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-300 focus:outline-none rounded-2xl shadow-xl backdrop-blur-md hover:border-blue-400 hover:shadow-2xl px-5 py-4 text-lg"
                    placeholder="Type your message here..."
                    disabled={isLoading}
                  />
                  <Button
                    type="submit"
                    disabled={isLoading || !input.trim()}
                    className="mt-auto w-full text-lg font-semibold flex items-center justify-center gap-2 shadow-lg rounded-xl bg-gradient-to-r from-blue-600 to-blue-800 hover:from-blue-700 hover:to-blue-900 hover:scale-[1.04] focus:ring-2 focus:ring-blue-400 focus:outline-none transition-all duration-150 group"
                    size="lg"
                  >
                    {isLoading ? (
                      <span className="flex items-center gap-2"><Loader2 className="animate-spin h-5 w-5" />Processing...</span>
                    ) : <><span className="group-hover:translate-x-1 transition-transform duration-150"><Send className="w-5 h-5" /></span> Submit</>}
                  </Button>
                </form>
              </CardContent>
            </Card>

            {/* Response Section */}
            <Card className="bg-white/95 rounded-xl shadow-md flex flex-col border border-blue-100 hover:shadow-lg transition-shadow duration-200">
              <CardHeader className="flex flex-row items-center gap-2 pb-2">
                <Lightbulb className="text-yellow-400 w-5 h-5" />
                <CardTitle className="text-xl font-semibold text-blue-800">Response</CardTitle>
              </CardHeader>
              <CardContent className="flex-1 h-40 md:h-64 p-0">
                <div className={`h-full p-4 bg-blue-50/60 rounded-lg overflow-auto border-2 border-blue-200 transition-all duration-200 ${isLoading ? 'animate-pulse' : ''}`}>
                  {isLoading ? (
                    <div className="flex items-center justify-center h-full">
                      <span className="flex items-center gap-2 text-blue-400 font-medium"><Loader2 className="animate-spin h-5 w-5" />Processing your request...</span>
                    </div>
                  ) : response ? (
                    <pre className="whitespace-pre-wrap text-blue-900 font-medium text-base animate-fade-in-up" style={{minHeight: '2rem'}}>{response}</pre>
                  ) : (
                    <div className="text-blue-300 text-center h-full flex items-center justify-center font-medium">
                      Response will appear here
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="w-full py-4 text-center text-xs text-blue-400 bg-white/80 border-t border-blue-100 mt-8 animate-fade-in-up">
        &copy; {new Date().getFullYear()} Astra Assistant &mdash; Built with <span className="text-blue-500">Next.js</span> & <span className="text-blue-500">shadcn/ui</span>
      </footer>

      {/* Animations */}
      <style jsx global>{`
        @keyframes fade-in-up {
          0% { opacity: 0; transform: translateY(20px); }
          100% { opacity: 1; transform: translateY(0); }
        }
        @keyframes fade-in-down {
          0% { opacity: 0; transform: translateY(-20px); }
          100% { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in-up { animation: fade-in-up 0.7s cubic-bezier(.4,0,.2,1) both; }
        .animate-fade-in-down { animation: fade-in-down 0.7s cubic-bezier(.4,0,.2,1) both; }
      `}</style>
    </div>
  );
} 