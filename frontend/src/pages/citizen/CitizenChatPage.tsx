import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '../../context/AuthContext';
import { api } from '../../services/api';
import { ChatMessage } from '../../types';
import {
  Send,
  Bot,
  Sparkles,
  CheckCircle2,
} from 'lucide-react';

export const CitizenChatPage: React.FC = () => {
  const { citizenProfile } = useAuth();

  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: 'welcome',
      sender: 'assistant',
      text: `Hello ${citizenProfile?.full_name || 'Citizen'}! 👋\n\nI am your CivicAdmin Assistant. How can I assist you today? You can ask about your profile information, check your registered household details, or inquire about municipal services.`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      suggested_prompts: [
        'View My Profile',
        'Check Household Details',
        'Review Application Status',
        'What services are available?',
      ],
    },
  ]);

  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (textToSend?: string) => {
    const message = (textToSend || inputMessage).trim();
    if (!message || isLoading) return;

    const userMsg: ChatMessage = {
      id: `user-${Date.now()}`,
      sender: 'user',
      text: message,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await api.chat.sendMessage(message);
      const assistantMsg: ChatMessage = {
        id: `assistant-${Date.now()}`,
        sender: 'assistant',
        text: response.reply,
        timestamp: response.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        suggested_prompts: response.suggested_prompts,
        context_data: response.context_data,
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: `err-${Date.now()}`,
        sender: 'assistant',
        text: 'Sorry, I encountered an issue processing your request. Please ensure you are connected and try again.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div id="main-content" className="py-6 px-4 sm:px-6 lg:px-8 max-w-4xl mx-auto h-[calc(100vh-8rem)] flex flex-col">
      {/* Chat Container Card */}
      <div className="flex-1 bg-white border border-slate-300 rounded-2xl shadow-xl overflow-hidden flex flex-col">
        {/* Chat Header (WhatsApp Inspired Green Top Bar) */}
        <div className="bg-[#075E54] text-white px-5 py-3.5 flex items-center justify-between shadow-sm">
          <div className="flex items-center gap-3">
            <div className="relative">
              <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center font-bold text-white border border-white/30">
                <Bot className="w-6 h-6 text-emerald-200" />
              </div>
              <span className="absolute bottom-0 right-0 w-3 h-3 bg-emerald-400 border-2 border-[#075E54] rounded-full" />
            </div>
            <div>
              <h1 className="font-bold text-base leading-tight">CivicAdmin Assistant</h1>
              <span className="text-xs text-emerald-100 flex items-center gap-1">
                <span>Online</span>
                <span>•</span>
                <span className="text-[11px]">Authorized Citizen Assistance</span>
              </span>
            </div>
          </div>
          <div className="text-xs bg-[#128C7E] px-2.5 py-1 rounded-full text-emerald-50 border border-white/10 hidden sm:block">
            Direct Municipal Channel
          </div>
        </div>

        {/* Message Thread Area */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 bg-[#ECE5DD] space-y-4">
          <div className="text-center my-2">
            <span className="bg-white/80 text-slate-600 text-[11px] font-semibold px-3 py-1 rounded-full shadow-sm">
              Today • End-to-End Encrypted Session
            </span>
          </div>

          {messages.map((msg) => {
            const isUser = msg.sender === 'user';
            return (
              <div
                key={msg.id}
                className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}
              >
                <div
                  className={`max-w-[85%] sm:max-w-[75%] rounded-2xl px-4 py-3 shadow-sm ${
                    isUser
                      ? 'bg-[#DCF8C6] text-slate-900 rounded-br-xs'
                      : 'bg-white text-slate-900 rounded-bl-xs'
                  }`}
                >
                  <p className="text-sm whitespace-pre-line leading-relaxed font-normal">
                    {msg.text}
                  </p>
                  <div className={`mt-1.5 flex items-center gap-1 text-[10px] text-slate-500 ${isUser ? 'justify-end' : 'justify-start'}`}>
                    <span>{msg.timestamp}</span>
                    {isUser && <CheckCircle2 className="w-3 h-3 text-emerald-600" />}
                  </div>
                </div>

                {/* Suggested Prompt Chips */}
                {!isUser && msg.suggested_prompts && msg.suggested_prompts.length > 0 && (
                  <div className="mt-2.5 flex flex-wrap gap-1.5 max-w-[85%]">
                    {msg.suggested_prompts.map((prompt, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSend(prompt)}
                        disabled={isLoading}
                        className="text-xs bg-white text-emerald-800 font-semibold px-3 py-1.5 rounded-full border border-emerald-300 hover:bg-emerald-50 hover:border-emerald-400 focus:outline-none focus:ring-2 focus:ring-emerald-500 shadow-xs transition-colors flex items-center gap-1"
                      >
                        <Sparkles className="w-3 h-3 text-emerald-600" />
                        <span>{prompt}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            );
          })}

          {isLoading && (
            <div className="flex items-start">
              <div className="bg-white text-slate-500 text-xs rounded-2xl px-4 py-2.5 shadow-sm flex items-center gap-2">
                <div className="w-2 h-2 bg-emerald-600 rounded-full animate-bounce" />
                <div className="w-2 h-2 bg-emerald-600 rounded-full animate-bounce [animation-delay:0.2s]" />
                <div className="w-2 h-2 bg-emerald-600 rounded-full animate-bounce [animation-delay:0.4s]" />
                <span className="ml-1 text-[11px]">Assistant is consulting official records...</span>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar Area */}
        <div className="p-3 bg-[#F0F2F5] border-t border-slate-300">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSend();
            }}
            className="flex items-center gap-2"
          >
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={isLoading}
              placeholder="Ask about your profile, household, or services..."
              aria-label="Type your message to the assistant"
              className="flex-1 bg-white rounded-full px-4 py-2.5 text-sm text-slate-900 border border-slate-300 focus:outline-none focus:ring-2 focus:ring-[#075E54] shadow-xs"
            />
            <button
              type="submit"
              disabled={isLoading || !inputMessage.trim()}
              aria-label="Send message"
              className="w-10 h-10 rounded-full bg-[#075E54] hover:bg-[#128C7E] text-white flex items-center justify-center shadow-md focus:outline-none focus:ring-2 focus:ring-offset-1 focus:ring-[#075E54] disabled:opacity-50 transition-all flex-shrink-0"
            >
              <Send className="w-4 h-4 ml-0.5" />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};
