import React, { useState, useEffect } from 'react';
import { api } from '../../services/api';
import {
  QrCode,
  ExternalLink,
  CheckCircle2,
  RefreshCw,
  PhoneCall,
  MoreVertical,
  ArrowLeft,
  ShieldCheck,
  Zap,
  Maximize2,
  MessageSquare,
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
  const [iframeKey, setIframeKey] = useState<number>(Date.now());

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

  const reloadBot = () => {
    setIframeKey(Date.now());
  };

  const openLivechatWidget = () => {
    if ((window as any).myLandbot?.open) {
      (window as any).myLandbot.open();
    }
  };

  return (
    <div id="main-content" className="py-8 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto space-y-8">
      {/* Header */}
      <div className="text-center max-w-3xl mx-auto">
        <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold uppercase tracking-wider mb-3 border border-emerald-300">
          <Zap className="w-3.5 h-3.5" />
          <span>Landbot Automated WhatsApp & Citizen Services</span>
        </div>
        <h1 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">
          Scan & Chat with Municipal Bot
        </h1>
        <p className="mt-2 text-sm sm:text-base text-slate-600 leading-relaxed">
          Citizens can complete their official municipal registration, check household residences, and track
          verification status directly through our automated Landbot WhatsApp bot without visiting the website.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Side: Scannable QR Code & Instructions (5 cols) */}
        <div className="lg:col-span-5 bg-white rounded-3xl border border-slate-200 p-6 sm:p-8 shadow-sm space-y-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-xs font-bold text-slate-500 uppercase tracking-wider">
              <QrCode className="w-4 h-4 text-emerald-600" />
              <span>Scan to Chat on Phone</span>
            </div>
            <button
              onClick={openLivechatWidget}
              type="button"
              className="text-xs font-semibold text-emerald-700 hover:text-emerald-800 flex items-center gap-1 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200"
            >
              <MessageSquare className="w-3.5 h-3.5" />
              <span>Open Livechat Widget</span>
            </button>
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
              Scan with your smartphone camera to connect to the bot
            </p>
            <span className="text-[11px] text-slate-500 font-mono">
              Official Helpline: {botInfo?.phone_number || '+1 555 019 2834'}
            </span>
          </div>

          {/* Direct Action Buttons */}
          <div className="space-y-2">
            {botInfo?.wa_me_url && (
              <a
                href={botInfo.wa_me_url}
                target="_blank"
                rel="noopener noreferrer"
                className="w-full inline-flex items-center justify-center gap-2 px-5 py-3 rounded-xl bg-[#25D366] hover:bg-[#20bd5a] text-slate-950 font-bold text-sm shadow transition-all focus:outline-none focus:ring-2 focus:ring-[#25D366]"
              >
                <span>Launch WhatsApp Directly</span>
                <ExternalLink className="w-4 h-4" />
              </a>
            )}

            <a
              href="/landbot.html"
              target="_blank"
              rel="noopener noreferrer"
              className="w-full inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-800 font-semibold text-xs transition-colors"
            >
              <span>Open Landbot in Full Window</span>
              <Maximize2 className="w-3.5 h-3.5 text-slate-500" />
            </a>
          </div>

          {/* Capabilities List */}
          <div className="space-y-2.5 pt-2 border-t border-slate-100">
            <h3 className="text-xs font-bold text-slate-800 uppercase tracking-wider">
              Landbot Municipal Capabilities:
            </h3>
            <ul className="text-xs text-slate-600 space-y-2">
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                <span>
                  <strong>Full Citizen Self-Registration:</strong> Real-time input validation for full name, email address, and language preferences.
                </span>
              </li>
              <li className="flex items-start gap-2">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0 mt-0.5" />
                <span>
                  <strong>Live Profile Inquiries:</strong> Query official citizen code, verification standing, and contact details.
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
                  <strong>Privacy Safeguards:</strong> Co-resident phone numbers and administrative internal notes are securely withheld.
                </span>
              </li>
            </ul>
          </div>
        </div>

        {/* Right Side: Embedded Real Landbot in Mobile Device Frame (7 cols) */}
        <div className="lg:col-span-7 flex flex-col items-center">
          <div className="w-full max-w-md bg-slate-900 rounded-[2.5rem] p-3 shadow-2xl border-4 border-slate-700">
            {/* Phone Screen Frame */}
            <div className="bg-[#ECE5DD] rounded-[2rem] overflow-hidden flex flex-col h-[650px] relative border border-slate-800">
              {/* WhatsApp App Top Bar */}
              <div className="bg-[#075E54] text-white px-3.5 py-3 flex items-center justify-between shadow-sm z-10">
                <div className="flex items-center gap-2">
                  <ArrowLeft className="w-4 h-4 text-white" />
                  <div className="w-8 h-8 rounded-full bg-emerald-200 text-slate-900 flex items-center justify-center font-bold text-xs border border-white">
                    LB
                  </div>
                  <div>
                    <h2 className="font-bold text-xs leading-tight flex items-center gap-1">
                      <span>NagrikSetu Bot</span>
                      <CheckCircle2 className="w-3 h-3 text-emerald-300" />
                    </h2>
                    <span className="text-[10px] text-emerald-100">नागरिक सेतु Official Channel</span>
                  </div>
                </div>
                <div className="flex items-center gap-2 text-white/80">
                  <button
                    onClick={reloadBot}
                    type="button"
                    title="Reload Landbot"
                    className="p-1 hover:text-white rounded hover:bg-white/10 transition-colors"
                  >
                    <RefreshCw className="w-3.5 h-3.5" />
                  </button>
                  <PhoneCall className="w-3.5 h-3.5" />
                  <MoreVertical className="w-3.5 h-3.5" />
                </div>
              </div>

              {/* Status Banner */}
              <div className="bg-emerald-700 text-white text-[11px] font-medium px-3 py-1 flex items-center justify-between">
                <span>🟢 Live NagrikSetu Citizen Bot Connected</span>
                <ShieldCheck className="w-3.5 h-3.5 text-emerald-200" />
              </div>

              {/* Real Landbot Embed */}
              <div className="flex-1 w-full h-full bg-white relative">
                <iframe
                  key={iframeKey}
                  src="/landbot.html"
                  title="NagrikSetu Landbot Assistant"
                  className="w-full h-full border-0 absolute inset-0"
                  allow="microphone; camera"
                />
              </div>
            </div>
          </div>
          <p className="mt-3 text-xs text-slate-500 text-center max-w-sm">
            💡 <strong>Live Interactive Demo:</strong> Chat directly inside the phone screen above or click the floating chat bubble in the bottom right corner!
          </p>
        </div>
      </div>
    </div>
  );
};

export default WhatsAppBotPage;
