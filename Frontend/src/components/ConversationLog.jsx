import React, { useRef, useEffect } from 'react';
import DebateBubble from './DebateBubble';

const ConversationLog = ({ conversation, modelA }) => {
    const bottomRef = useRef(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [conversation]);

    return (
        <div className="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth bg-gray-50/50 dark:bg-gray-900/50">
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
    );
};

export default ConversationLog;
