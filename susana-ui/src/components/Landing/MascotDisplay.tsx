'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Syringe, Calendar, CheckCircle2 } from 'lucide-react';

interface MascotDisplayProps {
  size?: 'sm' | 'md' | 'lg';
  interactive?: boolean;
}

export function SuzannaAvatar({ size = 40 }: { size?: number }) {
  return (
    <div 
      className="relative flex items-center justify-center rounded-full bg-gradient-to-tr from-[#1A5699] to-[#2563EB] shadow-sm select-none"
      style={{ width: size, height: size }}
      aria-label="Avatar da SUSANNA"
    >
      {/* SUSANNA drop silhouette */}
      <svg 
        viewBox="0 0 64 64" 
        className="w-4/5 h-4/5" 
        fill="none" 
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* White Drop Body */}
        <path 
          d="M32 6C32 6 12 30 12 43C12 54.0457 20.9543 60 32 60C43.0457 60 52 54.0457 52 43C52 30 32 6 32 6Z" 
          fill="#FFFFFF" 
        />
        {/* Blue Medical Cross */}
        <path 
          d="M32 24V34M27 29H37" 
          stroke="#1A5699" 
          strokeWidth="3.5" 
          strokeLinecap="round" 
        />
        {/* Friendly Eyes */}
        <circle cx="26" cy="41" r="2.5" fill="#1A5699" />
        <circle cx="38" cy="41" r="2.5" fill="#1A5699" />
        {/* Smile */}
        <path 
          d="M28 47C29.5 49 34.5 49 36 47" 
          stroke="#1A5699" 
          strokeWidth="2.2" 
          strokeLinecap="round" 
        />
      </svg>
    </div>
  );
}

export function MascotDisplay({ size = 'lg', interactive = true }: MascotDisplayProps) {
  return (
    <div className="relative flex items-center justify-center w-full max-w-md mx-auto py-4 select-none">
      {/* Background radial glow */}
      <div className="absolute w-72 h-72 md:w-80 md:h-80 rounded-full bg-gradient-to-br from-[#2563EB]/15 to-[#60A5FA]/10 blur-2xl -z-10" />

      {/* Main Mascot Circle */}
      <motion.div 
        animate={interactive ? { y: [0, -8, 0] } : {}}
        transition={{ duration: 4.5, repeat: Infinity, ease: 'easeInOut' }}
        className="relative w-64 h-64 md:w-72 md:h-72 rounded-full bg-gradient-to-b from-[#2563EB] to-[#1E40AF] p-3 shadow-xl flex items-center justify-center border-4 border-white/80"
      >
        <svg 
          viewBox="0 0 200 200" 
          className="w-52 h-52 filter drop-shadow-md"
          fill="none" 
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Main Drop Body */}
          <path 
            d="M100 20C100 20 40 92 40 135C40 168.137 66.8629 188 100 188C133.137 188 160 168.137 160 135C160 92 100 20 100 20Z" 
            fill="#FFFFFF" 
          />
          {/* Blue Medical Cross */}
          <path 
            d="M100 70V100M85 85H115" 
            stroke="#1A5699" 
            strokeWidth="8" 
            strokeLinecap="round" 
          />
          {/* Expressive Eyes with shine */}
          <ellipse cx="80" cy="122" rx="6.5" ry="8" fill="#1A5699" />
          <circle cx="82" cy="119" r="2.5" fill="#FFFFFF" />

          <ellipse cx="120" cy="122" rx="6.5" ry="8" fill="#1A5699" />
          <circle cx="122" cy="119" r="2.5" fill="#FFFFFF" />

          {/* Rosy Cheeks */}
          <circle cx="71" cy="132" r="5" fill="#60A5FA" opacity="0.4" />
          <circle cx="129" cy="132" r="5" fill="#60A5FA" opacity="0.4" />

          {/* Happy Smile */}
          <path 
            d="M88 138C93 145 107 145 112 138" 
            stroke="#1A5699" 
            strokeWidth="5" 
            strokeLinecap="round" 
          />

          {/* Friendly wave arm */}
          <motion.path 
            animate={interactive ? { rotate: [0, 10, 0] } : {}}
            transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
            d="M145 130C158 122 172 120 178 126C182 130 176 142 160 144"
            stroke="#FFFFFF"
            strokeWidth="10"
            strokeLinecap="round"
          />
        </svg>

        {/* Small verified badge on mascot */}
        <div className="absolute bottom-2 right-6 bg-white text-[#16A34A] rounded-full p-1.5 shadow-md flex items-center justify-center border border-emerald-100">
          <CheckCircle2 size={20} className="stroke-[2.5]" />
        </div>
      </motion.div>

      {/* Floating Badge 1: Vacinação */}
      <motion.div 
        animate={interactive ? { y: [0, 6, 0] } : {}}
        transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut', delay: 0.5 }}
        className="absolute -top-2 -left-4 md:-left-8 glass-card rounded-2xl p-3 shadow-lg flex items-center gap-3 border border-white/90 text-left max-w-[200px]"
      >
        <div className="w-10 h-10 rounded-xl bg-blue-50 text-[#2563EB] flex items-center justify-center flex-shrink-0">
          <Syringe size={20} className="stroke-[2.2]" />
        </div>
        <div>
          <span className="inline-block text-[11px] font-semibold text-emerald-600 uppercase tracking-wider">Ativa</span>
          <p className="text-xs font-bold text-[#0A1B3D] leading-snug">Vacinação no DF</p>
          <p className="text-[11px] text-slate-500">Asa Norte · UBS 1</p>
        </div>
      </motion.div>

      {/* Floating Badge 2: Próxima consulta */}
      <motion.div 
        animate={interactive ? { y: [0, -6, 0] } : {}}
        transition={{ duration: 4.2, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
        className="absolute -bottom-3 -right-4 md:-right-8 glass-card rounded-2xl p-3 shadow-lg flex items-center gap-3 border border-white/90 text-left max-w-[210px]"
      >
        <div className="w-10 h-10 rounded-xl bg-indigo-50 text-[#1E40AF] flex items-center justify-center flex-shrink-0">
          <Calendar size={20} className="stroke-[2.2]" />
        </div>
        <div>
          <span className="inline-block text-[11px] font-semibold text-blue-600 uppercase tracking-wider">Agendamento</span>
          <p className="text-xs font-bold text-[#0A1B3D] leading-snug">Clínico Geral</p>
          <p className="text-[11px] text-slate-500">Qui, 15 out · 14h</p>
        </div>
      </motion.div>
    </div>
  );
}
