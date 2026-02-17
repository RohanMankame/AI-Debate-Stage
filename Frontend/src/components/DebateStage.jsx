import React, { useState, useEffect } from 'react';
import { ArrowLeft, MessageCircle, Gavel, RefreshCw, Loader2 } from 'lucide-react';
import ConversationLog from './ConversationLog';
import JudgeModal from './JudgeModal';
import { advanceSession, judgeSession, getSessionState } from '../services/api';

const DebateStage = ({ session, onBack }) => {
    const [sessionState, setSessionState] = useState(session);
    const [conversation, setConversation] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [judgeData, setJudgeData] = useState(null);
    const [isJudgeModalOpen, setIsJudgeModalOpen] = useState(false);

    // Sync state on mount
    useEffect(() => {
        if (session) {
            setSessionState(session);
            // If the session object from createSession/response has a 'state' property, use it.
            // The create_session response returns { session_id, state: DebateTurnResponse }
            // But get_session returns SessionStateResponse which has transcript directly.
            // We need to handle both structures or normalize them.
            // Let's rely on getSessionState to normalize if needed, but for now assume initial sync.
            if (session.state && session.state.updated_conversation) {
                setConversation(session.state.updated_conversation);
            } else if (session.transcript) {
                setConversation(session.transcript);
            }
        }
    }, [session]);

    const handleNextTurn = async () => {
        setIsLoading(true);
        try {
            const result = await advanceSession(sessionState.session_id);
            setSessionState(prev => ({ ...prev, ...result })); // Merge state
            setConversation(result.updated_conversation);
        } catch (error) {
            console.error("Failed to advance turn:", error);
            alert("Failed to advance turn. See console for details.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleJudge = async () => {
        setIsLoading(true);
        try {
            const result = await judgeSession(sessionState.session_id);
            setJudgeData(result);
            setIsJudgeModalOpen(true);
        } catch (error) {
            console.error("Failed to judge debate:", error);
            alert("Failed to judge debate. See console for details.");
        } finally {
            setIsLoading(false);
        }
    };

    const isDebateDone = sessionState.done || (sessionState.state && sessionState.state.done);

    // Helper to get model names from session create response or state response
    // session response structure: { session_id, state: {...} } - doesn't have model names directly if purely from create reponse
    // We might need to pass the initial config props or fetch full state.
    // For simplicity, let's assume we can fetch full state on mount if names are missing.

    // Actually, the createSession response in `api.py` returns `SessionCreateResponse`:
    // contains `session_id` and `state` (DebateTurnResponse).
    // `DebateTurnResponse` has `updated_conversation`.
    // It does NOT have the model names in `SessionCreateResponse`.
    // So we should fetch the full session state immediately to get metadata.

    useEffect(() => {
        const fetchFullState = async () => {
            try {
                const data = await getSessionState(session.session_id);
                setSessionState(data);
                setConversation(data.transcript);
            } catch (e) {
                console.error("Failed to fetch session state", e);
            }
        };
        if (session.session_id) {
            fetchFullState();
        }
    }, [session.session_id]);

    return (
        <div className="h-screen flex flex-col bg-gray-50 dark:bg-gray-900">
            {/* Header */}
            <header className="h-16 px-6 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between shadow-sm z-10">
                <div className="flex items-center gap-4">
                    <button
                        onClick={onBack}
                        className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
                    >
                        <ArrowLeft className="w-5 h-5 text-gray-500 dark:text-gray-400" />
                    </button>
                    <div>
                        <h1 className="text-lg font-semibold text-gray-900 dark:text-white truncate max-w-md">
                            {sessionState.original_debate_topic || "Debate Session"}
                        </h1>
                        <div className="flex items-center gap-2 text-xs text-gray-500">
                            <span className="flex items-center gap-1">
                                <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>
                                Round {sessionState.current_round} / {sessionState.max_rounds}
                            </span>
                        </div>
                    </div>
                </div>

                <div className="flex items-center gap-3">
                    {!isDebateDone && (
                        <button
                            onClick={handleNextTurn}
                            disabled={isLoading}
                            className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-all disabled:opacity-50"
                        >
                            {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <MessageCircle className="w-4 h-4" />}
                            Next Turn
                        </button>
                    )}

                    {/* Show Judge button if done or manually if user wants early verdict (maybe only if done) */}
                    <button
                        onClick={handleJudge}
                        disabled={isLoading}
                        className="flex items-center gap-2 px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white text-sm font-medium rounded-lg transition-all disabled:opacity-50"
                    >
                        {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Gavel className="w-4 h-4" />}
                        Judge Verdict
                    </button>
                </div>
            </header>

            {/* Main Content */}
            <div className="flex-1 flex overflow-hidden">
                {/* Model A Profile */}
                <div className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 p-6 hidden md:block">
                    <div className="text-center">
                        <div className="w-16 h-16 mx-auto bg-blue-100 text-blue-600 rounded-full flex items-center justify-center mb-4">
                            <span className="text-xl font-bold">A</span>
                        </div>
                        <h3 className="font-bold text-gray-900 dark:text-white mb-1">{sessionState.model_a}</h3>
                        <p className="text-xs text-blue-500 font-medium bg-blue-50 dark:bg-blue-900/20 py-1 px-2 rounded-full inline-block mb-4">
                            {sessionState.model_a_model}
                        </p>
                        <div className="text-left bg-gray-50 dark:bg-gray-700/50 p-3 rounded-lg border border-gray-100 dark:border-gray-700">
                            <p className="text-xs font-semibold text-gray-500 mb-1">STANCE</p>
                            <p className="text-sm text-gray-700 dark:text-gray-300 italic">"{sessionState.model_a_stance}"</p>
                        </div>
                    </div>
                </div>

                {/* Conversation */}
                <div className="flex-1 flex flex-col relative bg-gray-50 dark:bg-gray-900">
                    <ConversationLog conversation={conversation} modelA={sessionState.model_a} />
                </div>

                {/* Model B Profile */}
                <div className="w-64 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 p-6 hidden md:block">
                    <div className="text-center">
                        <div className="w-16 h-16 mx-auto bg-purple-100 text-purple-600 rounded-full flex items-center justify-center mb-4">
                            <span className="text-xl font-bold">B</span>
                        </div>
                        <h3 className="font-bold text-gray-900 dark:text-white mb-1">{sessionState.model_b}</h3>
                        <p className="text-xs text-purple-500 font-medium bg-purple-50 dark:bg-purple-900/20 py-1 px-2 rounded-full inline-block mb-4">
                            {sessionState.model_b_model}
                        </p>
                        <div className="text-left bg-gray-50 dark:bg-gray-700/50 p-3 rounded-lg border border-gray-100 dark:border-gray-700">
                            <p className="text-xs font-semibold text-gray-500 mb-1">STANCE</p>
                            <p className="text-sm text-gray-700 dark:text-gray-300 italic">"{sessionState.model_b_stance}"</p>
                        </div>
                    </div>
                </div>
            </div>

            <JudgeModal
                isOpen={isJudgeModalOpen}
                onClose={() => setIsJudgeModalOpen(false)}
                winner={judgeData?.winner}
                reasoning={judgeData?.reasoning}
                scores={judgeData?.scores}
            />
        </div>
    );
};

export default DebateStage;
