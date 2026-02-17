import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Gavel, Star, X } from 'lucide-react';

const JudgeModal = ({ isOpen, onClose, winner, reasoning, scores }) => {
    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
                <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    className="relative w-full max-w-2xl bg-white dark:bg-gray-800 rounded-2xl shadow-2xl overflow-hidden"
                >
                    {/* Header */}
                    <div className="p-6 bg-gradient-to-r from-amber-500 to-orange-500 text-white flex justify-between items-start">
                        <div>
                            <h2 className="text-3xl font-bold flex items-center gap-2">
                                <Gavel className="w-8 h-8" />
                                The Verdict
                            </h2>
                            <p className="text-amber-100 mt-1">Judge AI has spoken.</p>
                        </div>
                        <button onClick={onClose} className="p-1 hover:bg-white/20 rounded-full transition-colors">
                            <X size={24} />
                        </button>
                    </div>

                    {/* Content */}
                    <div className="p-8 space-y-6">
                        <div className="text-center">
                            <span className="text-sm font-medium text-gray-500 uppercase tracking-widest">Winner</span>
                            <h3 className="text-4xl font-black text-gray-900 dark:text-white mt-2 mb-6">
                                {winner}
                            </h3>
                            <div className="inline-block px-4 py-1 bg-amber-100 text-amber-700 rounded-full text-sm font-semibold">
                                Decisive Victory
                            </div>
                        </div>

                        <div className="space-y-2">
                            <h4 className="font-semibold text-gray-700 dark:text-gray-200 flex items-center gap-2">
                                <Star className="w-4 h-4 text-amber-500" />
                                Reasoning
                            </h4>
                            <p className="text-gray-600 dark:text-gray-300 leading-relaxed bg-gray-50 dark:bg-gray-700/50 p-4 rounded-xl border border-gray-100 dark:border-gray-700">
                                {reasoning}
                            </p>
                        </div>
                    </div>

                    {/* Footer */}
                    <div className="p-6 bg-gray-50 dark:bg-gray-900 border-t border-gray-100 dark:border-gray-700 flex justify-end">
                        <button
                            onClick={onClose}
                            className="px-6 py-2 bg-gray-900 dark:bg-white text-white dark:text-gray-900 font-medium rounded-lg hover:opacity-90 transition-opacity"
                        >
                            Close Verdict
                        </button>
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
};

export default JudgeModal;
