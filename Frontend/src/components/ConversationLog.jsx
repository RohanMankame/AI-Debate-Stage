import React, { useRef, useEffect } from 'react';
import DebateBubble from './DebateBubble';

const ConversationLog = ({ conversation, modelA }) => {
    const bottomRef = useRef(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [conversation]);

    return (
        <div className="flex-1 p-6 space-y-6 bg-white/80 dark:bg-gray-900/60 rounded-md shadow-inner no-scrollbar">
            <div className="max-w-3xl mx-auto">
                {conversation.map((msg, index) => (
                    <DebateBubble
                        key={index}
                        speaker={msg.speaker}
                        text={msg.text}
                        round={msg.round}
                        isModelA={msg.speaker === modelA}
                    />
                ))}
                <div ref={bottomRef} />
            </div>
        </div>
    );
};

export default ConversationLog;