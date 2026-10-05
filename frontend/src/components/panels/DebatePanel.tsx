'use client';

import React from 'react';
import { useTelemetryStore } from '@/stores/telemetryStore';
import {
  MessageSquare,
  Sparkles,
  ShieldCheck,
  CloudLightning,
  AlertTriangle,
  Scale,
  Cpu,
  Layers,
  ArrowRight,
  Clock,
  CheckCircle2,
} from 'lucide-react';

export function DebatePanel() {
  const { confluence, latestTelemetry, stationStatus } = useTelemetryStore();

  const conf = confluence || {
    classification: 'Nominal Baseline',
    confidence: 0.99,
    confidence_score: 99.0,
    p_weather: 0.04,
    p_defect: 0.03,
    defect_class: 'none',
    summary: 'Atmospheric parameters within nominal IMD physical boundaries.',
    action_recommended: 'Continuous 1 Hz nominal monitoring.',
    agent_dialogue: [],
  };

  const dialogue = conf.agent_dialogue || [];
  const isNominal = conf.classification === 'Nominal Baseline';
  const isDefect = conf.classification === 'Sensor Defect';
  const isNatural = conf.classification === 'Natural Weather Event';

  const rawConf = conf.confidence_score !== undefined
    ? conf.confidence_score
    : (conf.confidence <= 1.0 ? conf.confidence * 100 : conf.confidence);
  const confidencePct = Math.round(Number(rawConf) * 10) / 10;

  return (
    <div className="space-y-4 animate-in fade-in duration-200">
      {/* Top Banner: Arena Status */}
      <div className="glass-panel rounded-2xl p-4 border border-white/10 space-y-3 bg-gradient-to-br from-slate-900/90 via-[#0b1329]/80 to-slate-900/90 shadow-glass">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400 shadow-glow-cyan/20">
              <MessageSquare className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-sm font-mono font-bold uppercase tracking-wider text-white">
                  Dual-Agent Neuro-Symbolic Arena
                </h2>
                <span className="flex items-center gap-1 text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-300 border border-cyan-500/30">
                  <span className="w-1.5 h-1.5 rounded-full bg-cyan-400 animate-ping" />
                  Live Sync
                </span>
              </div>
              <p className="text-[11px] font-mono text-slate-400">
                Layer 3 Adversarial Debate & Confluence Synthesis Engine
              </p>
            </div>
          </div>

          {/* Verdict Pill */}
          <div className="flex items-center gap-2">
            <div
              className={`px-3 py-1 rounded-xl text-xs font-mono font-bold border flex items-center gap-1.5 ${
                isDefect
                  ? 'bg-rose-500/20 text-rose-300 border-rose-500/40 shadow-glow-rose/20'
                  : isNatural
                  ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40 shadow-glow-emerald/20'
                  : 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40'
              }`}
            >
              {isDefect && <AlertTriangle className="w-3.5 h-3.5" />}
              {isNatural && <CloudLightning className="w-3.5 h-3.5" />}
              {isNominal && <ShieldCheck className="w-3.5 h-3.5" />}
              <span>{conf.classification}</span>
            </div>
          </div>
        </div>

        {/* Participating Agent Persona Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 pt-2 border-t border-white/10 text-xs font-mono">
          {/* Agent A */}
          <div className="p-2.5 rounded-xl bg-sky-950/30 border border-sky-500/30 flex items-start gap-2">
            <div className="p-1.5 rounded-lg bg-sky-500/20 text-sky-400 shrink-0">
              <CloudLightning className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <div className="text-[11px] font-bold text-sky-200 truncate">Model A (Atmospheric)</div>
              <div className="text-[10px] text-slate-400">Synoptic LSTM • Physics</div>
              <div className="text-[10px] text-sky-400 font-semibold mt-0.5">
                P(Weather): {Math.round((conf.p_weather ?? 0.04) * 100)}%
              </div>
            </div>
          </div>

          {/* Agent B */}
          <div className="p-2.5 rounded-xl bg-rose-950/30 border border-rose-500/30 flex items-start gap-2">
            <div className="p-1.5 rounded-lg bg-rose-500/20 text-rose-400 shrink-0">
              <Cpu className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <div className="text-[11px] font-bold text-rose-200 truncate">Model B (Hardware)</div>
              <div className="text-[10px] text-slate-400">CNN-LSTM • Sensor Failures</div>
              <div className="text-[10px] text-rose-400 font-semibold mt-0.5">
                P(Defect): {Math.round((conf.p_defect ?? 0.03) * 100)}%
              </div>
            </div>
          </div>

          {/* Arbiter */}
          <div className="p-2.5 rounded-xl bg-purple-950/30 border border-purple-500/30 flex items-start gap-2">
            <div className="p-1.5 rounded-lg bg-purple-500/20 text-purple-400 shrink-0">
              <Scale className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <div className="text-[11px] font-bold text-purple-200 truncate">Confluence Arbiter</div>
              <div className="text-[10px] text-slate-400">Thermodynamic Judge</div>
              <div className="text-[10px] text-purple-300 font-semibold mt-0.5">
                Confidence: {confidencePct}%
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Synthesis Verdict Card */}
      <div className="glass-panel rounded-2xl p-4 border border-white/10 space-y-2 bg-slate-900/60">
        <div className="flex items-center justify-between text-xs font-mono">
          <span className="text-slate-400 uppercase tracking-wider font-semibold flex items-center gap-1.5">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            Consensus Scientific Rationale
          </span>
          <span className="text-[10px] text-slate-500">
            {dialogue.length > 0 ? `${dialogue.length} Round(s) Evaluated` : 'Pass-through'}
          </span>
        </div>
        <div className="text-xs text-slate-200 leading-relaxed font-sans bg-black/40 p-3 rounded-xl border border-white/5">
          {conf.summary || conf.action_recommended || 'Atmospheric parameters within nominal physical boundaries.'}
        </div>
        {conf.action_recommended && (
          <div className="flex items-start gap-2 text-xs font-mono text-cyan-300 bg-cyan-950/30 p-2.5 rounded-xl border border-cyan-500/20">
            <ArrowRight className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
            <div>
              <span className="font-bold text-cyan-200 uppercase text-[10px] block">Recommended Action</span>
              <span className="text-[11px] text-slate-300">{conf.action_recommended}</span>
            </div>
          </div>
        )}
      </div>

      {/* Conversation Stream */}
      <div className="glass-panel rounded-2xl p-4 border border-white/10 space-y-3 bg-slate-900/50">
        <div className="flex items-center justify-between">
          <div className="text-xs font-mono font-bold uppercase tracking-wider text-slate-300 flex items-center gap-2">
            <span>Debate Dialogue Transcript</span>
            <span className="text-[10px] font-normal px-2 py-0.5 rounded-full bg-slate-800 text-slate-400 border border-white/5">
              Turn-by-turn verification
            </span>
          </div>
        </div>

        <div className="space-y-3">
          {dialogue.length > 0 ? (
            dialogue.map((turn, idx) => {
              const isModelA = turn.role === 'model_a';
              const isModelB = turn.role === 'model_b';
              const isArbiter = turn.role === 'arbiter';

              const cardTheme = isModelA
                ? 'bg-sky-950/30 border-sky-500/40 text-sky-100 shadow-glow-cyan/5'
                : isModelB
                ? 'bg-rose-950/30 border-rose-500/40 text-rose-100 shadow-glow-rose/5'
                : 'bg-purple-950/30 border-purple-500/40 text-purple-100 shadow-glow-indigo/5';

              const avatarBg = isModelA
                ? 'bg-sky-500/20 text-sky-300 border-sky-500/40'
                : isModelB
                ? 'bg-rose-500/20 text-rose-300 border-rose-500/40'
                : 'bg-purple-500/20 text-purple-300 border-purple-500/40';

              const roleLabel = isModelA
                ? 'Model A • Atmospheric Specialist'
                : isModelB
                ? 'Model B • Hardware Diagnostician'
                : 'Arbiter • Thermodynamic Judge';

              return (
                <div
                  key={idx}
                  className={`p-3.5 rounded-xl border transition-all duration-200 ${cardTheme}`}
                >
                  {/* Speaker Header */}
                  <div className="flex items-center justify-between mb-2 pb-1.5 border-b border-white/10">
                    <div className="flex items-center gap-2">
                      <div className={`px-2 py-0.5 rounded-lg border text-[10px] font-mono font-bold ${avatarBg}`}>
                        {turn.sender}
                      </div>
                      <span className="text-[10px] font-mono text-slate-400">
                        {roleLabel}
                      </span>
                    </div>
                    <span className="text-[9px] font-mono text-slate-500 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      Turn #{idx + 1}
                    </span>
                  </div>

                  {/* Statement Body */}
                  <p className="text-xs font-sans text-slate-100 leading-relaxed">
                    {turn.message}
                  </p>

                  {/* Turn Badges & Rationale */}
                  <div className="flex flex-wrap items-center gap-1.5 mt-2.5 pt-2 border-t border-white/5 text-[9px] font-mono">
                    {isModelA && (
                      <>
                        <span className="px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-500/30">
                          ΔP / Δt Barometric Drop Evaluated
                        </span>
                        <span className="px-2 py-0.5 rounded bg-white/5 text-slate-300">
                          P(Storm): {Math.round((conf.p_weather ?? 0.04) * 100)}%
                        </span>
                      </>
                    )}
                    {isModelB && (
                      <>
                        <span className="px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30">
                          Sensor Covariance Decoupling Test
                        </span>
                        <span className="px-2 py-0.5 rounded bg-white/5 text-slate-300">
                          P(Defect): {Math.round((conf.p_defect ?? 0.03) * 100)}%
                        </span>
                      </>
                    )}
                    {isArbiter && (
                      <>
                        <span className="px-2 py-0.5 rounded bg-purple-500/20 text-purple-300 border border-purple-500/30 font-bold">
                          Final Consensus Verdict
                        </span>
                        <span className="px-2 py-0.5 rounded bg-white/5 text-slate-300">
                          Confidence: {confidencePct}%
                        </span>
                      </>
                    )}
                  </div>
                </div>
              );
            })
          ) : (
            <div className="p-6 rounded-xl bg-black/30 border border-white/5 text-center space-y-2">
              <div className="w-10 h-10 mx-auto rounded-full bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <div className="text-xs font-mono text-slate-300 font-bold">
                Gatekeeper CNN-1D Monitoring Pass
              </div>
              <p className="text-[11px] font-mono text-slate-500 max-w-sm mx-auto">
                Current observations adhere to nominal IMD thermodynamic boundaries. The dual-agent debate will engage automatically when an outlier pattern is triggered.
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
