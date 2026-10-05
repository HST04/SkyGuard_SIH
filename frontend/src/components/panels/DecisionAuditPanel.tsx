'use client';

import React, { useState, useMemo } from 'react';
import { useTelemetryStore } from '@/stores/telemetryStore';
import { DecisionRecord, ConfluenceClassification } from '@/lib/types';
import {
  History,
  Search,
  Filter,
  CheckCircle2,
  AlertTriangle,
  CloudLightning,
  Activity,
  ShieldCheck,
  Clock,
  ArrowRight,
  ChevronDown,
  ChevronUp,
  Copy,
  Check,
  Sparkles,
  Radio,
  FileText,
} from 'lucide-react';

export function DecisionAuditPanel() {
  const { decisions } = useTelemetryStore();
  const [filterClass, setFilterClass] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [expandedDecisionId, setExpandedDecisionId] = useState<string | null>(null);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [decViewModes, setDecViewModes] = useState<Record<string, 'summary' | 'actual_readings'>>({});

  const filteredDecisions = useMemo(() => {
    return decisions.filter((d) => {
      // Filter by classification
      if (filterClass !== 'all' && d.classification !== filterClass) {
        return false;
      }
      // Search by query (culprits, trigger reason, action, classification)
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase();
        const matchesClass = d.classification.toLowerCase().includes(q);
        const matchesReason = d.trigger_reason.toLowerCase().includes(q);
        const matchesAction = d.action_recommended.toLowerCase().includes(q);
        const matchesSensor = d.culprit_sensors.some((s) => s.toLowerCase().includes(q));
        if (!matchesClass && !matchesReason && !matchesAction && !matchesSensor) {
          return false;
        }
      }
      return true;
    });
  }, [decisions, filterClass, searchQuery]);

  const handleCopy = (decision: DecisionRecord) => {
    navigator.clipboard.writeText(JSON.stringify(decision, null, 2));
    setCopiedId(decision.decision_id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const getBadgeConfig = (classification: ConfluenceClassification | string) => {
    switch (classification) {
      case 'Natural Weather Event':
        return {
          pill: 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40',
          icon: CloudLightning,
          accent: 'text-emerald-400',
        };
      case 'Sensor Defect':
        return {
          pill: 'bg-rose-500/20 text-rose-300 border-rose-500/40',
          icon: AlertTriangle,
          accent: 'text-rose-400',
        };
      case 'Compound Event':
        return {
          pill: 'bg-amber-500/20 text-amber-300 border-amber-500/40',
          icon: Activity,
          accent: 'text-amber-400',
        };
      default:
        return {
          pill: 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40',
          icon: ShieldCheck,
          accent: 'text-cyan-400',
        };
    }
  };

  return (
    <div className="space-y-4 animate-in fade-in duration-200">
      {/* Header Panel */}
      <div className="glass-panel rounded-2xl p-4 border border-white/10 space-y-3 bg-gradient-to-br from-slate-900/90 via-[#0b1329]/80 to-slate-900/90 shadow-glass">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <div className="flex items-center gap-2.5">
            <div className="p-2 rounded-xl bg-purple-500/10 border border-purple-500/30 text-purple-400 shadow-glow-indigo/20">
              <History className="w-5 h-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-sm font-mono font-bold uppercase tracking-wider text-white">
                  Decision Audit Trail
                </h2>
                <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 border border-purple-500/30">
                  {decisions.length} Logged
                </span>
              </div>
              <p className="text-[11px] font-mono text-slate-400">
                Timestamped AI confluence decisions, verdicts & recommended operational actions
              </p>
            </div>
          </div>
        </div>

        {/* Search Bar & Filter Strip */}
        <div className="space-y-2 pt-2 border-t border-white/10">
          <div className="relative">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search by sensor (temp, humidity), event type, or keywords..."
              className="w-full bg-black/40 border border-white/10 rounded-xl pl-9 pr-3 py-2 text-xs font-mono text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/60"
            />
          </div>

          <div className="flex items-center gap-1.5 flex-wrap text-[10px] font-mono">
            {[
              { id: 'all', label: 'All Events' },
              { id: 'Sensor Defect', label: 'Sensor Defects' },
              { id: 'Natural Weather Event', label: 'Weather Events' },
              { id: 'Compound Event', label: 'Compound' },
              { id: 'Nominal Baseline', label: 'Nominal Baseline' },
            ].map((f) => (
              <button
                key={f.id}
                onClick={() => setFilterClass(f.id)}
                className={`px-2.5 py-1 rounded-lg border transition-all ${
                  filterClass === f.id
                    ? 'bg-cyan-500/20 text-cyan-200 border-cyan-500/50 shadow-glow-cyan/20'
                    : 'bg-white/5 text-slate-400 border-white/5 hover:bg-white/10'
                }`}
              >
                {f.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Decisions List */}
      <div className="space-y-2.5">
        {filteredDecisions.length === 0 ? (
          <div className="glass-panel rounded-2xl p-8 border border-white/10 text-center space-y-2 bg-slate-900/40">
            <div className="w-10 h-10 mx-auto rounded-full bg-white/5 flex items-center justify-center text-slate-400">
              <History className="w-5 h-5" />
            </div>
            <div className="text-xs font-mono text-slate-300 font-bold">
              No Decision Records Found
            </div>
            <p className="text-[11px] font-mono text-slate-500 max-w-sm mx-auto">
              Decisions are permanently logged upon every state transition, anomaly detection, or dual-agent debate conclusion.
            </p>
          </div>
        ) : (
          filteredDecisions.map((dec) => {
            const isExpanded = expandedDecisionId === dec.decision_id;
            const badge = getBadgeConfig(dec.classification);
            const Icon = badge.icon;
            const formattedTime = new Date(dec.timestamp).toLocaleTimeString();
            const formattedDate = new Date(dec.timestamp).toLocaleDateString();

            return (
              <div
                key={dec.decision_id}
                className="glass-panel rounded-xl border border-white/10 bg-slate-900/60 transition-all duration-200 hover:border-white/20"
              >
                {/* Decision Summary Header Row */}
                <div
                  onClick={() => setExpandedDecisionId(isExpanded ? null : dec.decision_id)}
                  className="p-3.5 cursor-pointer flex items-start justify-between gap-3"
                >
                  <div className="flex items-start gap-3 min-w-0">
                    <div className={`p-2 rounded-xl border shrink-0 ${badge.pill}`}>
                      <Icon className="w-4 h-4" />
                    </div>

                    <div className="min-w-0 space-y-1">
                      <div className="flex items-center gap-2 flex-wrap">
                        <span className={`text-[11px] font-mono font-bold uppercase tracking-wider ${badge.accent}`}>
                          {dec.classification}
                        </span>
                        <span className="text-[10px] font-mono px-2 py-0.2 rounded-full bg-black/40 text-slate-300 border border-white/5">
                          {dec.confidence_score.toFixed(1)}% Confidence
                        </span>
                        <span className="text-[10px] font-mono text-slate-500 flex items-center gap-1">
                          <Clock className="w-3 h-3" />
                          {formattedTime} • {formattedDate}
                        </span>
                      </div>

                      <p className="text-xs font-sans text-slate-200 line-clamp-2 leading-relaxed">
                        {dec.trigger_reason}
                      </p>

                      {/* Culprit Sensors & Recommended Action */}
                      <div className="flex items-center gap-1.5 flex-wrap pt-1 text-[9px] font-mono">
                        {dec.culprit_sensors.map((s, idx) => (
                          <span
                            key={idx}
                            className="px-1.5 py-0.5 rounded bg-rose-500/10 text-rose-300 border border-rose-500/20"
                          >
                            Sensor: {s}
                          </span>
                        ))}
                        {dec.action_recommended && (
                          <span className="text-slate-400 flex items-center gap-1">
                            <ArrowRight className="w-2.5 h-2.5 text-cyan-400" />
                            {dec.action_recommended}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>

                  <div className="flex items-center gap-1 shrink-0 text-slate-400">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleCopy(dec);
                      }}
                      className="p-1.5 rounded-lg hover:bg-white/10 hover:text-white transition-colors"
                      title="Copy JSON"
                    >
                      {copiedId === dec.decision_id ? (
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                      ) : (
                        <Copy className="w-3.5 h-3.5" />
                      )}
                    </button>
                    {isExpanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
                  </div>
                </div>

                {/* Expanded Detail View */}
                {isExpanded && (
                  <div className="p-3.5 pt-0 border-t border-white/5 space-y-3 bg-black/30 rounded-b-xl animate-in fade-in duration-200">
                    {/* View Mode Toggle: Summary vs Actual Readings */}
                    <div className="flex items-center gap-1 pt-3 bg-black/40 p-1 rounded-lg border border-white/10 text-[10px] font-mono">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setDecViewModes((prev) => ({ ...prev, [dec.decision_id]: 'summary' }));
                        }}
                        className={`flex-1 py-1 px-2 rounded flex items-center justify-center gap-1 transition-all ${
                          (decViewModes[dec.decision_id] || 'summary') === 'summary'
                            ? 'bg-cyan-500/20 text-cyan-200 border border-cyan-500/40 font-semibold shadow-glow-cyan/20'
                            : 'text-slate-400 hover:text-slate-200'
                        }`}
                      >
                        <FileText className="w-3 h-3" />
                        <span>Decision Summary</span>
                      </button>

                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setDecViewModes((prev) => ({ ...prev, [dec.decision_id]: 'actual_readings' }));
                        }}
                        className={`flex-1 py-1 px-2 rounded flex items-center justify-center gap-1 transition-all ${
                          decViewModes[dec.decision_id] === 'actual_readings'
                            ? 'bg-purple-500/20 text-purple-200 border border-purple-500/40 font-semibold shadow-glow-indigo/20'
                            : 'text-slate-400 hover:text-slate-200'
                        }`}
                      >
                        <Radio className="w-3 h-3" />
                        <span>Actual Readings & Evidence</span>
                      </button>
                    </div>

                    {/* Content for Actual Readings vs Summary */}
                    {decViewModes[dec.decision_id] === 'actual_readings' ? (
                      <div className="space-y-2.5">
                        {/* Transmitted Telemetry Grid */}
                        {dec.transmitted_data?.sensor_readings ? (
                          <div className="p-2.5 rounded-xl bg-purple-950/20 border border-purple-500/20 space-y-1.5">
                            <div className="text-[10px] font-mono uppercase font-bold text-purple-300 flex items-center justify-between">
                              <span className="flex items-center gap-1">
                                <Radio className="w-3 h-3 text-purple-400" />
                                <span>Actual Transmitted Telemetry Snapshot</span>
                              </span>
                              {dec.transmitted_data.sequence && (
                                <span className="text-[9px] text-slate-500">Seq #{dec.transmitted_data.sequence}</span>
                              )}
                            </div>

                            <div className="grid grid-cols-2 sm:grid-cols-3 gap-1.5 text-[11px] font-mono pt-1">
                              <div className="p-1.5 rounded bg-white/5 border border-white/5">
                                <span className="text-[9px] text-slate-400 block">Temperature:</span>
                                <span className="text-slate-200 font-bold">{dec.transmitted_data.sensor_readings.temperature_c}°C</span>
                              </div>
                              <div className="p-1.5 rounded bg-white/5 border border-white/5">
                                <span className="text-[9px] text-slate-400 block">Humidity:</span>
                                <span className="text-slate-200 font-bold">{dec.transmitted_data.sensor_readings.humidity_pct}%</span>
                              </div>
                              <div className="p-1.5 rounded bg-white/5 border border-white/5">
                                <span className="text-[9px] text-slate-400 block">Pressure:</span>
                                <span className="text-slate-200 font-bold">{dec.transmitted_data.sensor_readings.pressure_hpa} hPa</span>
                              </div>
                              <div className="p-1.5 rounded bg-white/5 border border-white/5">
                                <span className="text-[9px] text-slate-400 block">Dew Point:</span>
                                <span className="text-slate-200 font-bold">{dec.transmitted_data.sensor_readings.dew_point_c}°C</span>
                              </div>
                              <div className="p-1.5 rounded bg-white/5 border border-white/5">
                                <span className="text-[9px] text-slate-400 block">Wind Speed:</span>
                                <span className="text-slate-200 font-bold">{dec.transmitted_data.sensor_readings.wind_speed_ms} m/s</span>
                              </div>
                              <div className="p-1.5 rounded bg-white/5 border border-white/5">
                                <span className="text-[9px] text-slate-400 block">Solar Radiation:</span>
                                <span className="text-slate-200 font-bold">{dec.transmitted_data.sensor_readings.solar_radiation_wm2} W/m²</span>
                              </div>
                            </div>
                          </div>
                        ) : (
                          <div className="p-2 rounded bg-black/20 text-[10px] font-mono text-slate-500 italic">
                            Operational state log (no abnormal sensor telemetry attached).
                          </div>
                        )}

                        {/* Why Decision Was Taken */}
                        {dec.decision_reasoning && (
                          <div className="p-2.5 rounded-xl bg-black/40 border border-white/10 space-y-1 text-xs">
                            <span className="text-[10px] uppercase font-bold text-amber-300 font-mono">
                              Why Decision Was Taken
                            </span>
                            <p className="text-[11px] font-sans text-slate-200 leading-relaxed">
                              {dec.decision_reasoning.why_decision || dec.decision_reasoning.physics_inconsistency || dec.trigger_reason}
                            </p>
                          </div>
                        )}
                      </div>
                    ) : (
                      /* Summary View */
                      <>
                        {/* Action Recommended Box */}
                        {dec.action_recommended && (
                          <div className="p-2.5 rounded-xl bg-cyan-950/20 border border-cyan-500/20 text-xs font-mono text-cyan-200 space-y-1">
                            <div className="text-[10px] uppercase font-bold text-cyan-400 flex items-center gap-1">
                              <Sparkles className="w-3 h-3" />
                              Recommended Protocol
                            </div>
                            <p className="text-[11px] text-slate-300 font-sans">{dec.action_recommended}</p>
                          </div>
                        )}
                      </>
                    )}

                    {/* Dialogue Transcript of this Decision */}
                    <div className="space-y-2">
                      <div className="text-[10px] font-mono font-bold uppercase tracking-wider text-slate-400">
                        Multi-Agent Deliberation Transcript ({dec.dialogue.length} Turns)
                      </div>

                      {dec.dialogue.length > 0 ? (
                        dec.dialogue.map((turn, tIdx) => {
                          const isA = turn.role === 'model_a';
                          const isB = turn.role === 'model_b';
                          return (
                            <div
                              key={tIdx}
                              className={`p-2.5 rounded-xl border text-xs ${
                                isA
                                  ? 'bg-sky-950/20 border-sky-500/30 text-sky-100'
                                  : isB
                                  ? 'bg-rose-950/20 border-rose-500/30 text-rose-100'
                                  : 'bg-purple-950/20 border-purple-500/30 text-purple-100'
                              }`}
                            >
                              <div className="flex items-center justify-between text-[10px] font-mono font-bold mb-1">
                                <span>{turn.sender}</span>
                                <span className="text-slate-500 font-normal">Turn #{tIdx + 1}</span>
                              </div>
                              <p className="text-[11px] font-sans leading-relaxed text-slate-200">
                                {turn.message}
                              </p>
                            </div>
                          );
                        })
                      ) : (
                        <div className="text-[11px] font-mono text-slate-500 italic p-2 rounded bg-black/20">
                          Automated deterministic state transition. No adversarial debate rounds required.
                        </div>
                      )}
                    </div>

                    {/* Technical Metadata Footer */}
                    <div className="flex items-center justify-between text-[9px] font-mono text-slate-500 pt-2 border-t border-white/5">
                      <span>ID: {dec.decision_id}</span>
                      <span>MSE Error: {dec.reconstruction_error.toFixed(4)}</span>
                      <span>Station: {dec.station_id}</span>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
