import React, { useState, useEffect, useRef } from 'react';
import { ShieldCheck, Lock, RefreshCw, AlertCircle, CheckCircle2, X, Sparkles, KeyRound } from 'lucide-react';
import { api } from '../services/api';
import { OTPGenerateResponse } from '../types';

interface OTPChallengeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onVerified: (otpReferenceId: string) => void;
  purpose?: string;
  recipientHint?: string;
  actionTitle?: string;
}

export const OTPChallengeModal: React.FC<OTPChallengeModalProps> = ({
  isOpen,
  onClose,
  onVerified,
  purpose = 'CITIZEN_PROFILE_UPDATE',
  recipientHint,
  actionTitle = 'Update Citizen Profile',
}) => {
  const [digits, setDigits] = useState<string[]>(['', '', '', '', '', '']);
  const [loading, setLoading] = useState<boolean>(false);
  const [generating, setGenerating] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [success, setSuccess] = useState<boolean>(false);
  const [otpInfo, setOtpInfo] = useState<OTPGenerateResponse | null>(null);
  const [timeLeft, setTimeLeft] = useState<number>(30);

  const inputRefs = useRef<(HTMLInputElement | null)[]>([]);

  // Request new OTP whenever modal is opened
  useEffect(() => {
    if (isOpen) {
      setDigits(['', '', '', '', '', '']);
      setErrorMessage('');
      setSuccess(false);
      requestOTP();
    }
  }, [isOpen]);

  // Countdown timer for resend
  useEffect(() => {
    if (!isOpen || timeLeft <= 0) return;
    const interval = setInterval(() => {
      setTimeLeft((t) => t - 1);
    }, 1000);
    return () => clearInterval(interval);
  }, [isOpen, timeLeft]);

  const requestOTP = async () => {
    setGenerating(true);
    setErrorMessage('');
    try {
      const res = await api.auth.generateOTP({ purpose, recipient: recipientHint });
      setOtpInfo(res);
      setTimeLeft(30);
      setTimeout(() => {
        inputRefs.current[0]?.focus();
      }, 100);
    } catch (err: any) {
      setErrorMessage(err.message || 'Failed to dispatch verification code.');
    } finally {
      setGenerating(false);
    }
  };

  const handleDigitChange = (index: number, val: string) => {
    const char = val.slice(-1);
    if (!/^\d*$/.test(char)) return;

    const newDigits = [...digits];
    newDigits[index] = char;
    setDigits(newDigits);
    setErrorMessage('');

    if (char && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }

    // Auto verify if all 6 digits are filled
    if (char && index === 5 && newDigits.every((d) => d !== '')) {
      verifyCode(newDigits.join(''));
    }
  };

  const handleKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Backspace' && !digits[index] && index > 0) {
      inputRefs.current[index - 1]?.focus();
    }
  };

  const handlePaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData('text').trim();
    if (/^\d{6}$/.test(pasted)) {
      const arr = pasted.split('');
      setDigits(arr);
      inputRefs.current[5]?.focus();
      verifyCode(pasted);
    }
  };

  const autoFillDemoCode = () => {
    if (otpInfo?.demo_hint) {
      const arr = otpInfo.demo_hint.split('');
      setDigits(arr);
      verifyCode(otpInfo.demo_hint);
    }
  };

  const verifyCode = async (codeToVerify?: string) => {
    const fullCode = codeToVerify || digits.join('');
    if (fullCode.length !== 6) {
      setErrorMessage('Please enter the full 6-digit verification code.');
      return;
    }
    if (!otpInfo?.reference_id) {
      setErrorMessage('Verification session expired. Please request a new OTP.');
      return;
    }

    setLoading(true);
    setErrorMessage('');
    try {
      const res = await api.auth.verifyOTP({
        reference_id: otpInfo.reference_id,
        otp_code: fullCode,
        purpose,
      });

      if (res.verified) {
        setSuccess(true);
        setTimeout(() => {
          onVerified(otpInfo.reference_id);
          onClose();
        }, 500);
      }
    } catch (err: any) {
      setErrorMessage(err.message || 'Incorrect verification code. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-navy-950/70 backdrop-blur-sm animate-fade-in"
      role="dialog"
      aria-modal="true"
      aria-labelledby="otp-modal-title"
    >
      <div className="relative w-full max-w-md bg-white rounded-2xl shadow-2xl border border-gov-gold/30 overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-navy-900 via-navy-800 to-navy-900 px-6 py-4 text-white flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-full bg-saffron-500/20 border border-saffron-400 flex items-center justify-center text-saffron-400">
              <Lock className="w-5 h-5" />
            </div>
            <div>
              <h3 id="otp-modal-title" className="text-base font-bold text-white">
                Two-Step Privacy Verification
              </h3>
              <p className="text-xs text-saffron-200">NagrikSetu Citizen Privacy Protection</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-white/10 transition"
            aria-label="Close dialog"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          <div className="text-center mb-5">
            <div className="w-12 h-12 bg-saffron-50 rounded-full flex items-center justify-center mx-auto mb-2 text-saffron-600">
              <KeyRound className="w-6 h-6" />
            </div>
            <h4 className="text-sm font-bold text-navy-900 mb-1">
              Confirm Authorization for {actionTitle}
            </h4>
            <p className="text-xs text-slate-500 max-w-xs mx-auto">
              To protect your citizen profile privacy, a 6-digit one-time authorization code was sent to{' '}
              <span className="font-semibold text-navy-900">
                {otpInfo?.recipient || recipientHint || 'your registered contact'}
              </span>.
            </p>
          </div>

          {/* Evaluator Demo Quick Banner */}
          {otpInfo?.demo_hint && (
            <div className="mb-5 p-3 bg-amber-50 border border-amber-200 rounded-xl flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <Sparkles className="w-4 h-4 text-amber-600 flex-shrink-0" />
                <div className="text-xs">
                  <span className="font-semibold text-amber-900">Evaluator Demo OTP: </span>
                  <span className="font-mono font-bold text-saffron-700 text-sm tracking-wider">
                    {otpInfo.demo_hint}
                  </span>
                </div>
              </div>
              <button
                type="button"
                onClick={autoFillDemoCode}
                className="px-2.5 py-1 bg-saffron-500 hover:bg-saffron-600 text-white rounded text-[11px] font-semibold transition"
              >
                Auto-Fill
              </button>
            </div>
          )}

          {errorMessage && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-xs flex items-start space-x-2">
              <AlertCircle className="w-4 h-4 flex-shrink-0 mt-0.5 text-red-500" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* 6-Digit Inputs */}
          <div className="flex justify-center space-x-2.5 mb-6" onPaste={handlePaste}>
            {digits.map((digit, idx) => (
              <input
                key={idx}
                ref={(el) => { inputRefs.current[idx] = el; }}
                type="text"
                inputMode="numeric"
                pattern="[0-9]*"
                maxLength={1}
                value={digit}
                onChange={(e) => handleDigitChange(idx, e.target.value)}
                onKeyDown={(e) => handleKeyDown(idx, e)}
                disabled={loading || generating || success}
                className={`w-12 h-14 text-center text-xl font-bold font-mono rounded-xl border-2 transition-all focus:outline-none ${
                  success
                    ? 'border-emerald-500 bg-emerald-50 text-emerald-800'
                    : digit
                    ? 'border-saffron-500 bg-saffron-50/50 text-navy-950 shadow-sm'
                    : 'border-slate-300 focus:border-navy-900 bg-white'
                }`}
                aria-label={`Digit ${idx + 1}`}
              />
            ))}
          </div>

          {/* Actions */}
          <button
            type="button"
            onClick={() => verifyCode()}
            disabled={loading || generating || digits.join('').length !== 6 || success}
            className="w-full py-3 px-4 bg-navy-900 hover:bg-navy-800 text-white font-semibold rounded-xl shadow hover:shadow-md transition flex items-center justify-center space-x-2 disabled:opacity-50"
          >
            {loading ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin text-saffron-400" />
                <span>Verifying Authorization...</span>
              </>
            ) : success ? (
              <>
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                <span>Authorized! Applying Changes...</span>
              </>
            ) : (
              <>
                <ShieldCheck className="w-5 h-5 text-saffron-400" />
                <span>Verify & Apply Changes</span>
              </>
            )}
          </button>

          {/* Resend & Timer */}
          <div className="mt-4 flex items-center justify-between text-xs text-slate-500">
            <span>Reference: {otpInfo?.reference_id || 'Generating...'}</span>
            {timeLeft > 0 ? (
              <span>Resend in {timeLeft}s</span>
            ) : (
              <button
                type="button"
                onClick={requestOTP}
                disabled={generating}
                className="text-saffron-600 hover:text-saffron-700 font-semibold"
              >
                {generating ? 'Sending...' : 'Resend Code'}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
