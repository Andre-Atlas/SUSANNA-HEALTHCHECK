'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { 
  ArrowRight, 
  MessageSquare, 
  ShieldCheck, 
  Sparkles, 
  Clock, 
  ChevronRight 
} from 'lucide-react';
import { MascotDisplay, SuzannaAvatar } from '@/components/Landing/MascotDisplay';

interface LandingPageProps {
  onEnterApp: () => void;
  onOpenChatDirectly: () => void;
}

export function LandingPage({ onEnterApp, onOpenChatDirectly }: LandingPageProps) {
  return (
    <div className="min-h-screen bg-[#F5F9FF] text-[#0A1B3D] flex flex-col selection:bg-blue-100">
      {/* Top Floating Header */}
      <header className="sticky top-0 z-40 glass-panel border-b border-slate-200/70 py-3.5 px-6">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <SuzannaAvatar size={38} />
            <div>
              <span className="font-extrabold text-base tracking-tight text-[#0A1B3D] flex items-center gap-1.5">
                SUS Digital
                <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-blue-100 text-[#2563EB] uppercase">
                  DF
                </span>
              </span>
              <p className="text-[11px] text-[#5B6B8C] hidden sm:block">
                Saúde pública · Distrito Federal
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={onOpenChatDirectly}
              className="text-xs sm:text-sm font-semibold text-[#2563EB] hover:text-[#1D4ED8] flex items-center gap-1.5 py-2 px-3 rounded-full hover:bg-blue-50/70 transition"
            >
              <MessageSquare size={16} />
              <span>Falar com a SUSANNA</span>
            </button>
            <button
              onClick={onEnterApp}
              className="bg-[#2563EB] hover:bg-[#1D4ED8] text-white text-xs sm:text-sm font-semibold py-2.5 px-5 rounded-full shadow-sm hover:shadow active:scale-[0.98] transition flex items-center gap-1.5"
            >
              <span>Acessar Plataforma</span>
              <ArrowRight size={15} />
            </button>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1">
        <section className="py-12 md:py-20 px-6 max-w-6xl mx-auto">
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 items-center">
            {/* Left Copy */}
            <motion.div 
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="lg:col-span-7 space-y-6 text-left"
            >
              <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-blue-50 border border-blue-100 text-xs font-semibold text-[#2563EB]">
                <Sparkles size={14} />
                <span>Assistente Oficial do SUS-DF</span>
              </div>

              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-[#0A1B3D] leading-[1.08]">
                Saúde pública, <br />
                <span className="text-[#2563EB] italic font-serif">clara</span> como água.
              </h1>

              <p className="text-base sm:text-lg text-[#5B6B8C] max-w-[54ch] leading-relaxed">
                Agende consultas, acompanhe exames e tire dúvidas com a SUSANNA, assistente de IA que consulta dados atualizados da rede pública da Secretaria de Saúde do DF.
              </p>

              {/* CTAs */}
              <div className="flex flex-wrap items-center gap-4 pt-2">
                <button
                  onClick={onEnterApp}
                  className="bg-[#2563EB] hover:bg-[#1D4ED8] text-white font-semibold text-base py-3.5 px-7 rounded-full shadow-md hover:shadow-lg active:scale-[0.98] transition flex items-center gap-2"
                >
                  <span>Acessar Plataforma</span>
                  <ArrowRight size={17} />
                </button>
                <button
                  onClick={onOpenChatDirectly}
                  className="bg-white hover:bg-slate-50 text-[#0A1B3D] border border-slate-200/90 font-medium text-sm py-3 px-6 rounded-full transition flex items-center gap-2 shadow-2xs"
                >
                  <span>Tirar uma dúvida</span>
                  <ChevronRight size={16} className="text-slate-400" />
                </button>
              </div>

              {/* Scope Guarantee */}
              <div className="pt-4 flex items-center gap-2 text-xs text-[#5B6B8C]">
                <ShieldCheck size={16} className="text-[#16A34A] flex-shrink-0" />
                <span>Respostas fundamentadas exclusivamente em dados abertos oficiais da SES-DF.</span>
              </div>
            </motion.div>

            {/* Right Mascot Hero Card */}
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="lg:col-span-5 flex justify-center"
            >
              <MascotDisplay size="lg" interactive={true} />
            </motion.div>
          </div>
        </section>

        {/* 3 Pillars Section */}
        <section className="py-16 px-6 bg-white/70 border-y border-slate-200/60">
          <div className="max-w-6xl mx-auto">
            <div className="text-center max-w-xl mx-auto mb-12">
              <span className="text-xs font-bold uppercase tracking-wider text-[#2563EB] block mb-1">
                Pilares do Sistema
              </span>
              <h2 className="text-2xl sm:text-3xl font-bold text-[#0A1B3D]">
                Informação segura em uma só experiência
              </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Pillar 01 */}
              <div className="glass-card rounded-3xl p-7 text-left transition hover:-translate-y-1 duration-200">
                <span className="text-3xl font-bold font-mono text-[#2563EB]/40 block mb-4">
                  01
                </span>
                <h3 className="text-lg font-bold text-[#0A1B3D] mb-2">
                  Atendimento por IA
                </h3>
                <p className="text-sm text-[#5B6B8C] leading-relaxed">
                  Respostas fundamentadas em dados públicos, horários de UBS, estoques de vacinas e farmácias, a qualquer hora.
                </p>
              </div>

              {/* Pillar 02 */}
              <div className="glass-card rounded-3xl p-7 text-left transition hover:-translate-y-1 duration-200">
                <span className="text-3xl font-bold font-mono text-[#2563EB]/40 block mb-4">
                  02
                </span>
                <h3 className="text-lg font-bold text-[#0A1B3D] mb-2">
                  Histórico Clínico
                </h3>
                <p className="text-sm text-[#5B6B8C] leading-relaxed">
                  Consultas, vacinas aplicadas e resultados de exames organizados em uma linha do tempo intuitiva e clara.
                </p>
              </div>

              {/* Pillar 03 */}
              <div className="glass-card rounded-3xl p-7 text-left transition hover:-translate-y-1 duration-200">
                <span className="text-3xl font-bold font-mono text-[#2563EB]/40 block mb-4">
                  03
                </span>
                <h3 className="text-lg font-bold text-[#0A1B3D] mb-2">
                  Dados Regionais
                </h3>
                <p className="text-sm text-[#5B6B8C] leading-relaxed">
                  Campanhas ativas, vigilância da dengue e alertas sanitários específicos da sua Região Administrativa no DF.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Ready to start CTA Banner */}
        <section className="py-16 px-6 max-w-4xl mx-auto text-center">
          <div className="rounded-3xl p-8 sm:p-12 bg-gradient-to-br from-[#1E40AF] to-[#2563EB] text-white shadow-xl relative overflow-hidden">
            <div className="relative z-10 space-y-4">
              <h2 className="text-2xl sm:text-3xl font-bold tracking-tight">
                Pronto para <span className="underline decoration-white/40">começar</span>?
              </h2>
              <p className="text-sm sm:text-base text-blue-100 max-w-lg mx-auto">
                Entre na plataforma digital do SUS-DF e converse com a SUSANNA para tirar suas dúvidas agora mesmo.
              </p>
              <div className="pt-2">
                <button
                  onClick={onEnterApp}
                  className="bg-white hover:bg-slate-50 text-[#1E40AF] font-bold text-sm sm:text-base py-3.5 px-8 rounded-full shadow-md active:scale-[0.98] transition inline-flex items-center gap-2"
                >
                  <span>Acessar Plataforma</span>
                  <ArrowRight size={17} />
                </button>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="py-8 px-6 border-t border-slate-200/70 text-xs text-[#5B6B8C] text-center">
        <div className="max-w-6xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <p>
            SUS Digital · Protótipo conceitual integrado com Inteligência Artificial SES-DF.
          </p>
          <div className="flex items-center gap-4 text-[11px]">
            <span>Privacidade & LGPD</span>
            <span>·</span>
            <span>Termos de Uso</span>
            <span>·</span>
            <span>Ouvidoria 160</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
