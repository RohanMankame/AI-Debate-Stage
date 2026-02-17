import React from 'react';
import { motion } from 'framer-motion';
import clsx from 'clsx';
import { Bot, User } from 'lucide-react';

const DebateBubble = ({ speaker, text, round, isModelA }) => {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className={clsx(
                "flex w-full mb-6",
                isModelA ? "justify-start" : "justify-end"
            )}
        >
            <div className={clsx(
                "max-w-[80%] flex gap-4",
                isModelA ? "flex-row" : "flex-row-reverse"
            )}>
                <div className={clsx(
                    "w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 shadow-md",
                    isModelA ? "bg-blue-100 text-blue-600" : "bg-purple-100 text-purple-600"
                )}>
                    {isModelA ? <Bot size={20} /> : <User size={20} />}
                </div>

                <div className="flex flex-col gap-1">
                    <span className={clsx(
                        "text-xs font-semibold text-gray-500",
                        isModelA ? "text-left" : "text-right"
                    )}>
                        {speaker} • Round {round}
                    </span>
                    <div className={clsx(
                        "p-4 rounded-2xl shadow-sm text-sm leading-relaxed",
                        isModelA
                            ? "bg-white text-gray-800 rounded-tl-none border border-gray-100"
                            : "bg-gradient-to-br from-purple-600 to-purple-700 text-white rounded-tr-none"
                    )}>
                        {text}
                    </div>
                </div>
            </div>
        </motion.div>
    );
};

export default DebateBubble;
