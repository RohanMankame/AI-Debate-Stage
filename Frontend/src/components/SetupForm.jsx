import React, { useState } from 'react';
import { Settings, Play, MessageSquare, Bot } from 'lucide-react';

const AVAILABLE_MODELS = [
    { value: 'gpt-3.5-turbo', label: 'GPT-3.5 Turbo' },
    { value: 'gpt-4', label: 'GPT-4' },
    { value: 'claude-3-opus', label: 'Claude 3 Opus' },
    { value: 'claude-3-sonnet', label: 'Claude 3 Sonnet' },
];

const SetupForm = ({ onStartDebate, isLoading }) => {
    const [formData, setFormData] = useState({
        topic: '',
        model_a: 'Debater A',
        model_b: 'Debater B',
        model_a_stance: 'In favor',
        model_b_stance: 'Against',
        model_a_model: 'gpt-3.5-turbo',
        model_b_model: 'gpt-3.5-turbo',
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        onStartDebate({
            original_debate_topic: formData.topic,
            model_a: formData.model_a,
            model_b: formData.model_b,
            model_a_stance: formData.model_a_stance,
            model_b_stance: formData.model_b_stance,
            model_a_model: formData.model_a_model,
            model_b_model: formData.model_b_model,
            starting_turn: formData.model_a, // Model A starts by default
            max_rounds: 3,
        });
    };

    return (
        <div className="w-full max-w-2xl mx-auto p-6 bg-white dark:bg-gray-800 rounded-2xl shadow-xl">
            <div className="mb-8 text-center">
                <h2 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                    Configure Debate
                </h2>
                <p className="text-gray-500 dark:text-gray-400 mt-2">
                    Set the stage for an AI-powered battle of wits.
                </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-6">
                {/* Topic Section */}
                <div className="space-y-2">
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-200">
                        Debate Topic
                    </label>
                    <div className="relative">
                        <MessageSquare className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                        <textarea
                            required
                            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent dark:bg-gray-700 dark:text-white transition-all h-24 resize-none"
                            placeholder="e.g., Is AI sentient?"
                            value={formData.topic}
                            onChange={(e) => setFormData({ ...formData, topic: e.target.value })}
                        />
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    {/* Debater A */}
                    <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-xl border border-blue-100 dark:border-blue-800 space-y-4">
                        <h3 className="text-lg font-semibold text-blue-800 dark:text-blue-300 flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                            Debater A
                        </h3>

                        <div>
                            <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
                                Name
                            </label>
                            <input
                                type="text"
                                required
                                className="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
                                value={formData.model_a}
                                onChange={(e) => setFormData({ ...formData, model_a: e.target.value })}
                            />
                        </div>

                        <div>
                            <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
                                Model
                            </label>
                            <div className="relative">
                                <Bot className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
                                <select
                                    className="w-full pl-9 pr-3 py-2 border border-gray-200 dark:border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white appearance-none"
                                    value={formData.model_a_model}
                                    onChange={(e) => setFormData({ ...formData, model_a_model: e.target.value })}
                                >
                                    {AVAILABLE_MODELS.map(model => (
                                        <option key={model.value} value={model.value}>{model.label}</option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        <div>
                            <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
                                Stance
                            </label>
                            <input
                                type="text"
                                required
                                className="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:text-white"
                                value={formData.model_a_stance}
                                onChange={(e) => setFormData({ ...formData, model_a_stance: e.target.value })}
                            />
                        </div>
                    </div>

                    {/* Debater B */}
                    <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-xl border border-purple-100 dark:border-purple-800 space-y-4">
                        <h3 className="text-lg font-semibold text-purple-800 dark:text-purple-300 flex items-center gap-2">
                            <span className="w-2 h-2 rounded-full bg-purple-500"></span>
                            Debater B
                        </h3>

                        <div>
                            <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
                                Name
                            </label>
                            <input
                                type="text"
                                required
                                className="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 dark:bg-gray-800 dark:text-white"
                                value={formData.model_b}
                                onChange={(e) => setFormData({ ...formData, model_b: e.target.value })}
                            />
                        </div>

                        <div>
                            <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
                                Model
                            </label>
                            <div className="relative">
                                <Bot className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
                                <select
                                    className="w-full pl-9 pr-3 py-2 border border-gray-200 dark:border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 dark:bg-gray-800 dark:text-white appearance-none"
                                    value={formData.model_b_model}
                                    onChange={(e) => setFormData({ ...formData, model_b_model: e.target.value })}
                                >
                                    {AVAILABLE_MODELS.map(model => (
                                        <option key={model.value} value={model.value}>{model.label}</option>
                                    ))}
                                </select>
                            </div>
                        </div>

                        <div>
                            <label className="block text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide mb-1">
                                Stance
                            </label>
                            <input
                                type="text"
                                required
                                className="w-full px-3 py-2 border border-gray-200 dark:border-gray-700 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 dark:bg-gray-800 dark:text-white"
                                value={formData.model_b_stance}
                                onChange={(e) => setFormData({ ...formData, model_b_stance: e.target.value })}
                            />
                        </div>
                    </div>
                </div>

                <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full py-4 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold rounded-xl shadow-lg transform transition-all hover:scale-[1.02] active:scale-[0.98] disabled:opacity-70 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                    {isLoading ? (
                        'Initializing Debate...'
                    ) : (
                        <>
                            <Play className="w-5 h-5" />
                            Start Debate
                        </>
                    )}
                </button>
            </form>
        </div>
    );
};

export default SetupForm;
