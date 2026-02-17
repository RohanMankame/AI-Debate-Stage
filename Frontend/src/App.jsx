import React, { useState } from 'react';
import { Sparkles } from 'lucide-react';
import SetupForm from './components/SetupForm';
import DebateStage from './components/DebateStage';
import { createSession } from './services/api';

function App() {
  const [session, setSession] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleStartDebate = async (formData) => {
    setIsLoading(true);
    try {
      const response = await createSession(formData);
      // Ensure we have a session object. The API returns { session_id, state }.
      // We might want to merge the formData into it so we have the topic/model names available
      // if the API response doesn't repeat them.
      // Based on my API analysis, session_id and state are returned.
      // State has the conversation.
      // So I'll merge formData to keep track of names/topic.
      setSession({
        ...response,
        ...formData, // Fallback for metadata if not in response
      });
    } catch (error) {
      console.error("Failed to start debate:", error);
      alert("Failed to start debate. Please ensure the backend is running at http://localhost:8000");
    } finally {
      setIsLoading(false);
    }
  };

  const handleBack = () => {
    setSession(null);
  };

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900 text-gray-900 dark:text-gray-100 font-sans">
      {!session ? (
        <div className="flex flex-col min-h-screen">
          {/* Landing Header */}
          <header className="p-6 flex items-center justify-center">
            <div className="flex items-center gap-2 text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              <Sparkles className="w-8 h-8 text-blue-500" />
              AI Debate Stage
            </div>
          </header>

          <main className="flex-1 flex items-center justify-center p-4">
            <SetupForm onStartDebate={handleStartDebate} isLoading={isLoading} />
          </main>

          <footer className="p-6 text-center text-sm text-gray-500">
            Powered by FastAPI & React
          </footer>
        </div>
      ) : (
        <DebateStage session={session} onBack={handleBack} />
      )}
    </div>
  );
}

export default App;
