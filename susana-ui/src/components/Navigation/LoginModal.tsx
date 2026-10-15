'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Lock, CheckCircle, ArrowRight } from 'lucide-react';
import { SuzannaAvatar } from '@/components/Landing/MascotDisplay';

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

export function LoginModal({ isOpen, onClose, onSuccess }: LoginModalProps) {
  if (!isOpen) return null;

  return (
    <AnimatePresence>
      <div 
        className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm"
        role="dialog"
        aria-modal="true"
        aria-labelledby="login-title"
      >
        <motion.div
          initial={{ opacity: 0, scale: 0.95, y: 10 }}
          animate={{ opacity: 1, scale: 1, y: 0 }}
          exit={{ opacity: 0, scale: 0.95, y: 10 }}
          transition={{ duration: 0.2 }}
          className="relative w-full max-w-md p-6 bg-white rounded-3xl shadow-2xl border border-slate-100 text-center"
        >
          {/* Close button */}
          <button
            onClick={onClose}
            className="absolute top-4 right-4 p-2 text-slate-400 hover:text-slate-600 rounded-full hover:bg-slate-100 transition"
            aria-label="Fechar janela de login"
          >
            <X size={20} />
          </button>

          {/* Header */}
          <div className="flex flex-col items-center mb-6">
            <div className="mb-3">
              <SuzannaAvatar size={56} />
            </div>
            <span className="text-xs font-bold uppercase tracking-wider text-[#2563EB] bg-blue-50 px-3 py-1 rounded-full mb-2">
              Autenticação SUS Digital
            </span>
            <h2 id="login-title" className="text-xl font-bold text-[#0A1B3D]">
              Entrar na Plataforma
            </h2>
            <p className="text-sm text-slate-500 mt-1">
              Acesso seguro com a sua conta unificada do cidadão.
            </p>
          </div>

          {/* Simulated Login Card */}
          <div className="p-4 rounded-2xl bg-[#F8FAFC] border border-slate-200 text-left mb-6 space-y-3">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-sm">
                gov
              </div>
              <div>
                <p className="text-xs text-slate-500">Acessando como</p>
                <p className="text-sm font-semibold text-[#0A1B3D]">Maria Silva de Oliveira</p>
                <p className="text-[11px] text-slate-400">CPF: ***.842.101-**</p>
              </div>
            </div>
            <div className="flex items-center gap-2 pt-2 border-t border-slate-200/80 text-xs text-emerald-700">
              <CheckCircle size={15} />
              <span>Nível Prata · Dados de saúde validados SES-DF</span>
            </div>
          </div>

          {/* Terms notice */}
          <p className="text-xs text-slate-500 mb-6 flex items-center justify-center gap-1.5">
            <Lock size={14} className="text-slate-400" />
            Em conformidade com a LGPD e privacidade do SUS.
          </p>

          {/* Action buttons */}
          <div className="space-y-3">
            <button
              onClick={onSuccess}
              className="w-full py-3.5 px-6 rounded-full bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-medium text-sm flex items-center justify-center gap-2 shadow-md hover:shadow-lg active:scale-[0.98] transition"
            >
              <span>Confirmar e Acessar</span>
              <ArrowRight size={16} />
            </button>
            <button
              onClick={onClose}
              className="w-full py-2.5 px-6 rounded-full text-slate-600 hover:text-slate-800 text-sm font-medium transition"
            >
              Voltar à página inicial
            </button>
          </div>
        </motion.div>
      </div>
    </AnimatePresence>
  );
}
