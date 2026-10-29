import React, { useState, useEffect, useRef } from 'react';
import { api } from '../../services/api';
import {
  QrCode,
  Smartphone,
  ExternalLink,
  Send,
  CheckCircle2,
  Sparkles,
  RefreshCw,
  PhoneCall,
  MoreVertical,
  ArrowLeft,
  ShieldCheck,
  Zap,
} from 'lucide-react';

export const WhatsAppBotPage: React.FC = () => {
  const [botInfo, setBotInfo] = useState<{
    bot_name: string;
    phone_number: string;
    clean_number: string;
    wa_me_url: string;
    qr_code_svg: string;
    capabilities: string[];
  } | null>(null);

  const [loadingInfo, setLoadingInfo] = useState(true);

  // Phone Simulator State
  const [phoneNumber, setPhoneNumber] = useState('+91 98765 43210');
  const [messages, setMessages] = useState<Array<{
    id: string;
    sender: 'user' | 'bot';
    text: string;
    time: string;
    options?: string[];
  }>>([
    {
      id: 'welcome',
      sender: 'bot',
      text: "🏛️ *Welcome to CivicAdmin Municipal WhatsApp Services!*\n\nYou can register as a citizen or manage your municipal records directly here without visiting the website!\n\n👉 Reply *REGISTER* (or *1*) to start citizen registration.\n👉 Reply *HELP* to learn about available municipal services.",
      time: '10:00 AM',
      options: ['REGISTER', 'HELP'],
    },
  ]);

  const [inputMessage, setInputMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [registeredCitizenCode, setRegisteredCitizenCode] = useState<string | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const fetchInfo = async () => {
      try {
        const data = await api.whatsapp.getInfo();
        setBotInfo(data);
      } catch (err) {
        console.error('Failed to load WhatsApp info:', err);
      } finally {
        setLoadingInfo(false);
      }
    };
    fetchInfo();
  }, []);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isSending]);

  const handleSendMessage = async (textToSend?: string) => {
    const text = (textToSend || inputMessage).trim();
    if (!text || isSending) return;

    const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    // Append User Message
    const userMsg = {
      id: `u-${Date.now()}`,
      sender: 'user' as const,
      text,
      time: currentTime,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputMessage('');
    setIsSending(true);

    try {
      const res = await api.whatsapp.simulate(phoneNumber, text);
      const botMsg = {
        id: `b-${Date.now()}`,
        sender: 'bot' as const,
        text: res.reply,
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        options: res.options,
      };
      setMessages((prev) => [...prev, botMsg]);

      if (res.citizen_code) {
        setRegisteredCitizenCode(res.citizen_code);
      }
    } catch (err) {
      const errBotMsg = {
        id: `b-err-${Date.now()}`,
        sender: 'bot' as const,
        text: '⚠️ An error occurred processing your WhatsApp message. Please try again.',
        time: currentTime,
      };
      setMessages((prev) => [...prev, errBotMsg]);
    } finally {
      setIsSending(false);
    }
  };

  const resetSimulator = () => {
    setRegisteredCitizenCode(null);
    setMessages([
      {
        id: `welcome-${Date.now()}`,
        sender: 'bot',
        text: "🏛️ *Welcome to CivicAdmin Municipal WhatsApp Services!*\n\nYou can register as a citizen or manage your municipal records directly here without visiting the website!\n\n👉 Reply *REGISTER* (or *1*) to start citizen registration.\n👉 Reply *HELP* to learn about available municipal services.",
        time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        options: ['REGISTER', 'HELP'],
      },
    ]);
  };

  return (
    <div id="main-content" className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center max-w-3xl mx-auto">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold uppercase tracking-wider mb-3 border border-emerald-300">
          <Zap className="w-3.5 h-3.5" />
          <span>Interactive WhatsApp Citizen Bot</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">
          Scan & Register Directly on WhatsApp
        </h1>
        <p className="mt-2 text-sm sm:text-base text-slate-600 leading-relaxed">
          Citizens can complete their official municipal registration, check household residences, and track
          verification status directly through WhatsApp without visiting the website.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Side: Scannable QR Code & Instructions (5 cols) */}
        <div className="lg:col-span-5 bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-6">
          <div className="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-wider">
            <QrCode className="w-4 h-4 text-emerald-600" />
            <span>Scan to Chat on Phone</span>
          </div>

          {/* QR Code Container */}
          <div className="p-4 bg-slate-50 rounded-2xl border-2 border-dashed border-slate-300 flex flex-col items-center justify-center">
            {loadingInfo ? (
              <div className="w-48 h-48 flex items-center justify-center">
                <div className="w-8 h-8 border-4 border-emerald-300 border-t-emerald-700 rounded-full animate-spin" />
              </div>
            ) : botInfo?.qr_code_svg ? (
              <div
                className="w-48 h-48 sm:w-56 sm:h-56 [&>svg]:w-full [&>svg]:h-full rounded-xl overflow-hidden shadow-xs bg-white p-2"
                dangerouslySetInnerHTML={{ __html: botInfo.qr_code_svg }}
              />
            ) : (
              <div className="w-48 h-48 bg-slate-200 rounded-xl flex items-center justify-center text-xs text-slate-500">
                QR code unavailable
              </div>
            )}

            <p className="text-xs font-semibold text-slate-700 mt-3 text-center">
              Scan with your phone's camera to open WhatsApp
            </p>
            <span className="text-[11px] text-slate-500 font-mono">
              Bot Phone: {botInfo?.phone_number || '+1 555 019 2834'}
            </span>
          </div>

          {/* Direct WhatsApp Button */}
          {botInfo?.wa_me_url && (
            <a
              href={botInfo.wa_me_url}
              target="_blank"
              rel="noopener noreferrer"
              className="w-full inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-[#25D366] hover:bg-[#20bd5a] text-slate-950 font-bold text-sm shadow transition-all focus:outline-none focus:ring-2 focus:ring-[#25D366]"
            >
              <span>Launch WhatsApp Chat App</span>
              <ExternalLink className="w-4 h-4" />
            </a>
          )}

          {/* Capabilities List */}
          <div className="space-y-2.5 pt-2 border-t border-slate-100">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
              What Citizens Can Do on WhatsApp:
            </h3>
            <ul className="text-xs text-slate-600 space-y-2">
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                <span>
                  <strong>Full Citizen Self-Registration:</strong> Submit legal name, email, and language preferences directly in chat to create an official database record.
                </span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                <span>
                  <strong>Live Profile Inquiries:</strong> Query your official citizen code, verification standing, and contact details.
                </span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                <span>
                  <strong>Household Association:</strong> Retrieve registered residential address and family co-resident listings.
                </span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                <span>
                  <strong>Automated Audit Trails:</strong> Every citizen registered via WhatsApp generates an administrative audit event in PostgreSQL.
                </span>
              </li>
            </ul>
          </div>
        </div>

        {/* Right Side: Interactive Mobile WhatsApp Device Simulator (7 cols) */}
        <div className="lg:col-span-7 flex flex-col items-center">
          <div className="w-full max-w-md bg-slate-900 rounded-[2.5rem] p-3 shadow-2xl border-4 border-slate-700">
            {/* Phone Screen Frame */}
            <div className="bg-[#ECE5DD] rounded-[2rem] overflow-hidden flex flex-col h-[640px] relative border border-slate-800">
              {/* WhatsApp App Top Bar */}
              <div className="bg-[#075E54] text-white px-3.5 py-3 flex items-center justify-between shadow-sm z-10">
                <div className="flex items-center gap-2">
                  <ArrowLeft className="w-4 h-4 text-white" />
                  <div className="w-8 h-8 rounded-full bg-emerald-200 text-slate-900 flex items-center justify-center font-bold text-xs border border-white">
                    CA
                  </div>
                  <div>
                    <h2 className="font-bold text-xs leading-tight flex items-center gap-1">
                      <span>CivicAdmin Bot</span>
                      <CheckCircle2 className="w-3 h-3 text-emerald-300" />
                    </h2>
                    <span className="text-[10px] text-emerald-100">Official Municipal Channel</span>
                  </div>
                </div>
                <div className="flex items-center gap-3 text-white/80">
                  <PhoneCall className="w-3.5 h-3.5" />
                  <MoreVertical className="w-3.5 h-3.5" />
                </div>
              </div>

              {/* Simulated Phone Number Toolbar */}
              <div className="bg-slate-100 border-b border-slate-300 px-3 py-1.5 flex items-center justify-between text-xs">
                <div className="flex items-center gap-1 text-slate-600">
                  <Smartphone className="w-3.5 h-3.5 text-slate-400" />
                  <span className="text-[11px] font-semibold">Simulated Phone:</span>
                  <input
                    type="text"
                    value={phoneNumber}
                    onChange={(e) => setPhoneNumber(e.target.value)}
                    className="w-32 bg-white px-1.5 py-0.5 rounded border border-slate-300 font-mono text-[11px] text-slate-800"
                    title="Change phone number to test new citizen registrations"
                  />
                </div>
                <button
                  onClick={resetSimulator}
                  type="button"
                  title="Reset conversation"
                  className="p-1 text-slate-500 hover:text-slate-800 rounded"
                >
                  <RefreshCw className="w-3.5 h-3.5" />
                </button>
              </div>

              {/* Notification Banner when registration completes */}
              {registeredCitizenCode && (
                <div className="bg-emerald-600 text-white text-[11px] font-semibold px-3 py-1.5 flex items-center justify-between shadow-xs">
                  <span>✅ Citizen saved to database: {registeredCitizenCode}</span>
                  <ShieldCheck className="w-3.5 h-3.5" />
                </div>
              )}

              {/* Chat Messages Thread */}
              <div className="flex-1 overflow-y-auto p-3 space-y-2.5">
                <div className="text-center my-1">
                  <span className="bg-white/80 text-slate-600 text-[10px] font-semibold px-2.5 py-0.5 rounded-full shadow-xs">
                    MESSAGES ARE END-TO-END ENCRYPTED
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
                        className={`max-w-[85%] rounded-2xl px-3 py-2 text-xs shadow-xs leading-relaxed ${
                          isUser
                            ? 'bg-[#DCF8C6] text-slate-900 rounded-br-xs'
                            : 'bg-white text-slate-900 rounded-bl-xs'
                        }`}
                      >
                        <p className="whitespace-pre-line">{msg.text}</p>
                        <div className={`mt-1 flex items-center gap-1 text-[9px] text-slate-400 ${isUser ? 'justify-end' : 'justify-start'}`}>
                          <span>{msg.time}</span>
                          {isUser && <CheckCircle2 className="w-2.5 h-2.5 text-emerald-600" />}
                        </div>
                      </div>

                      {/* Quick Option Action Chips */}
                      {!isUser && msg.options && msg.options.length > 0 && (
                        <div className="mt-1.5 flex flex-wrap gap-1 max-w-[85%]">
                          {msg.options.map((opt, i) => (
                            <button
                              key={i}
                              onClick={() => handleSendMessage(opt.split('.')[0].trim())}
                              disabled={isSending}
                              className="text-[10px] bg-white text-emerald-800 font-semibold px-2.5 py-1 rounded-full border border-emerald-300 hover:bg-emerald-50 focus:outline-none shadow-2xs flex items-center gap-1"
                            >
                              <Sparkles className="w-2.5 h-2.5 text-emerald-600" />
                              <span>{opt}</span>
                            </button>
                          ))}
                        </div>
                      )}
                    </div>
                  );
                })}

                {isSending && (
                  <div className="flex items-start">
                    <div className="bg-white text-slate-500 text-[11px] rounded-xl px-3 py-1.5 shadow-xs flex items-center gap-1.5">
                      <div className="w-1.5 h-1.5 bg-emerald-600 rounded-full animate-bounce" />
                      <div className="w-1.5 h-1.5 bg-emerald-600 rounded-full animate-bounce [animation-delay:0.2s]" />
                      <div className="w-1.5 h-1.5 bg-emerald-600 rounded-full animate-bounce [animation-delay:0.4s]" />
                      <span className="text-[10px]">Processing via WhatsApp API...</span>
                    </div>
                  </div>
                )}

                <div ref={chatEndRef} />
              </div>

              {/* Input Area */}
              <div className="p-2 bg-[#F0F2F5] border-t border-slate-300">
                <form
                  onSubmit={(e) => {
                    e.preventDefault();
                    handleSendMessage();
                  }}
                  className="flex items-center gap-1.5"
                >
                  <input
                    type="text"
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder="Type a message or command..."
                    className="flex-1 bg-white rounded-full px-3.5 py-2 text-xs text-slate-900 border border-slate-300 focus:outline-none focus:ring-1 focus:ring-[#075E54]"
                  />
                  <button
                    type="submit"
                    disabled={isSending || !inputMessage.trim()}
                    className="w-8 h-8 rounded-full bg-[#075E54] hover:bg-[#128C7E] text-white flex items-center justify-center shadow focus:outline-none disabled:opacity-50"
                  >
                    <Send className="w-3.5 h-3.5 ml-0.5" />
                  </button>
                </form>
              </div>
            </div>
          </div>
          <p className="mt-3 text-xs text-slate-500 text-center max-w-sm">
            💡 <strong>Teacher Demo Tip:</strong> Change the phone number in the top bar to test registering a brand new citizen live into the database!
          </p>
        </div>
      </div>
    </div>
  );
};
