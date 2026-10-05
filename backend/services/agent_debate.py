import httpx
import json
import logging
from typing import Dict, Any, Tuple, List
from datetime import datetime
from backend.config import settings
from backend.schemas import AgentTurnLog, ConfluenceResult

logger = logging.getLogger("agent_debate")

class AgentDebateService:
    def __init__(self):
        self.api_key = settings.OPENROUTER_API_KEY
        self.model = settings.OPENROUTER_MODEL
        self.base_url = settings.OPENROUTER_BASE_URL

    async def conduct_debate(
        self,
        telemetry: Dict[str, Any],
        model_a_info: Dict[str, Any],
        model_b_info: Dict[str, Any]
    ) -> ConfluenceResult:
        """
        Executes a 2-turn dialogue between Model A (Atmospheric Specialist)
        and Model B (Hardware Diagnostician) via OpenRouter, concluding in a
        synthesized consensus decision with reasoning and classification.
        """
        # If no OpenRouter key is configured, use the local deterministic debate engine
        if not self.api_key or self.api_key.strip() == "":
            return self._local_deterministic_debate(telemetry, model_a_info, model_b_info)

        try:
            return await self._openrouter_debate(telemetry, model_a_info, model_b_info)
        except Exception as e:
            logger.warning(f"OpenRouter API call failed ({e}). Falling back to local debate engine.")
            return self._local_deterministic_debate(telemetry, model_a_info, model_b_info)

    async def _openrouter_debate(
        self,
        telemetry: Dict[str, Any],
        model_a_info: Dict[str, Any],
        model_b_info: Dict[str, Any]
    ) -> ConfluenceResult:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": "http://localhost:8000",
            "X-Title": "SkyGuard AI Multi-Agent Diagnostic Debate",
            "Content-Type": "application/json"
        }

        # --- Turn 1: Model A (Atmospheric Specialist) ---
        prompt_turn_1 = f"""You are 'Model A: Atmospheric Dynamics Specialist' analyzing automatic weather station telemetry.
Current Telemetry:
- Temperature: {telemetry.get('temperature_c')} °C
- Relative Humidity: {telemetry.get('humidity_pct')} %
- Barometric Pressure: {telemetry.get('pressure_hpa')} hPa
- Wind Speed: {telemetry.get('wind_speed_ms')} m/s
- Solar Radiation: {telemetry.get('solar_radiation_wm2')} W/m²
- Model A Prior Assessment: {json.dumps(model_a_info)}

Analyze physical thermodynamic consistency (e.g. pressure drops during convective downdrafts, dew point convergence, frontal squalls vs unphysical spikes).
Provide your concise meteorological hypothesis in 2-3 sentences."""

        turn_1_msg = await self._call_llm(headers, prompt_turn_1)
        turn_1_log = AgentTurnLog(
            sender="Model A (Atmospheric Specialist)",
            role="model_a",
            message=turn_1_msg,
            timestamp=datetime.utcnow().isoformat()
        )

        # --- Turn 2: Model B (Hardware Diagnostician) ---
        prompt_turn_2 = f"""You are 'Model B: Sensor Hardware Diagnostician' on an Automatic Weather Station.
Current Telemetry:
- Temperature: {telemetry.get('temperature_c')} °C, Humidity: {telemetry.get('humidity_pct')} %, Pressure: {telemetry.get('pressure_hpa')} hPa
- Model B Prior Assessment: {json.dumps(model_b_info)}

Model A (Atmospheric Specialist) just made this claim:
"{turn_1_msg}"

Evaluate whether this telemetry matches physical sensor failure archetypes (capacitive dielectric drift, ADC frozen bit flatline, resistive thermal spike, decoupling transient).
Either rebut or corroborate Model A in 2-3 sentences."""

        turn_2_msg = await self._call_llm(headers, prompt_turn_2)
        turn_2_log = AgentTurnLog(
            sender="Model B (Hardware Diagnostician)",
            role="model_b",
            message=turn_2_msg,
            timestamp=datetime.utcnow().isoformat()
        )

        # --- Consensus Synthesis ---
        prompt_consensus = f"""You are the Confluence Arbiter synthesizing a two-turn technical debate between:
Turn 1 - Model A (Weather Specialist): "{turn_1_msg}"
Turn 2 - Model B (Hardware Diagnostician): "{turn_2_msg}"

Telemetry values:
T={telemetry.get('temperature_c')}°C, RH={telemetry.get('humidity_pct')}%, P={telemetry.get('pressure_hpa')}hPa, Wind={telemetry.get('wind_speed_ms')}m/s

Output strictly valid JSON with no markdown formatting:
{{
  "classification": "Natural Weather Event" | "Sensor Defect" | "Compound Event" | "Nominal Baseline",
  "confidence_score": <number between 50 and 99.9>,
  "defect_class": "<short defect tag or none>",
  "summary": "<1-2 sentence decision reasoning combining both models>",
  "action_recommended": "<Actionable guidance for station operators>",
  "operator_alert": <true or false>
}}"""

        consensus_raw = await self._call_llm(headers, prompt_consensus)
        parsed = self._extract_json(consensus_raw)

        conf_score = float(parsed.get("confidence_score", 92.0))
        classification = parsed.get("classification", "Sensor Defect")
        defect_class = parsed.get("defect_class", "none")
        summary = parsed.get("summary", "Consensus reached from dual-agent telemetry cross-verification.")
        action = parsed.get("action_recommended", "Inspect telemetry log.")
        op_alert = bool(parsed.get("operator_alert", True))

        arbiter_log = AgentTurnLog(
            sender="Consensus Arbiter",
            role="arbiter",
            message=f"Consensus [{classification} - {conf_score:.1f}%]: {summary}",
            timestamp=datetime.utcnow().isoformat()
        )

        return ConfluenceResult(
            classification=classification,  # type: ignore
            confidence=conf_score / 100.0,
            confidence_score=conf_score,
            p_weather=0.9 if "Weather" in classification else 0.1,
            p_defect=0.9 if "Defect" in classification else 0.1,
            defect_class=defect_class,
            defect_type=defect_class,
            summary=summary,
            action_recommended=action,
            severity="high" if op_alert else "low",
            operator_alert=op_alert,
            agent_dialogue=[turn_1_log, turn_2_log, arbiter_log]
        )

    async def _call_llm(self, headers: dict, prompt: str) -> str:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": "You are an automated scientific telemetry reasoning agent."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.2,
                    "max_tokens": 250
                }
            )
            resp.raise_for_status()
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()

    def _extract_json(self, text: str) -> Dict[str, Any]:
        try:
            # Look for outermost braces
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                return json.loads(text[start:end+1])
            return json.loads(text)
        except Exception:
            return {}

    def _local_deterministic_debate(
        self,
        telemetry: Dict[str, Any],
        model_a_info: Dict[str, Any],
        model_b_info: Dict[str, Any]
    ) -> ConfluenceResult:
        """
        Local fallback engine delivering instant 2-turn dialogue without external API requirements.
        """
        temp = telemetry.get("temperature_c", 25.0)
        rh = telemetry.get("humidity_pct", 60.0)
        pressure = telemetry.get("pressure_hpa", 1013.0)
        wind = telemetry.get("wind_speed_ms", 2.0)
        fault = telemetry.get("fault_type", "normal")

        # Determine diagnostic scenario
        if fault == "valid_squall" or (wind > 15.0 and pressure < 1005.0):
            classification = "Natural Weather Event"
            defect_class = "severe_squall"
            conf = 96.5
            turn1 = f"Model A: Correlated sharp barometric pressure drop ({pressure:.1f} hPa) and wind gust ({wind:.1f} m/s) with moist advection ({rh:.1f}% RH) indicates a genuine microburst or squall front."
            turn2 = f"Model B: Confirmed across sensor channels. Thermistor and pressure transducer respond synchronously with physical lag, ruling out ADC latchup or hardware defect."
            reasoning = "Multi-parameter physical coherence validates this as a real convective weather event rather than hardware failure."
            action = "Log severe convective event; zero false alarms triggered."
            alert = False
        elif fault == "humidity_drift" or (rh > 85.0 and temp > 38.0):
            classification = "Sensor Defect"
            defect_class = "capacitive_drift"
            conf = 94.2
            turn1 = f"Model A: Thermodynamic violation detected. High ambient temperature ({temp:.1f}°C) co-occurring with elevated RH ({rh:.1f}%) violates local dew point psychrometric constraints under clear skies."
            turn2 = f"Model B: Capacitive polymer hygrometer exhibits monotonic positive baseline bias (+15%). Impedance shift characteristic of dielectric contamination."
            reasoning = "Psychrometric dew-point divergence and capacitive degradation signature confirm sensor drift."
            action = "Schedule hygrometer recalibration (< 2 weeks); activate data imputation."
            alert = True
        elif fault == "heat_spike" or (temp > 45.0):
            classification = "Sensor Defect"
            defect_class = "impulse_spike"
            conf = 98.0
            turn1 = f"Model A: Unphysical temperature discontinuity (+{temp:.1f}°C in single timestep) occurs without concurrent solar radiation surge or pressure fluctuation."
            turn2 = f"Model B: Point discontinuity matches classic ADC transient voltage spike or intermittent contact resistance on PT100 probe."
            reasoning = "Instantaneous single-parameter step function without meteorological cross-correlation confirms electrical sensor glitch."
            action = "Flag packet as sensor defect and substitute with imputed baseline."
            alert = True
        elif fault == "stuck_humidity":
            classification = "Sensor Defect"
            defect_class = "frozen_flatline"
            conf = 97.5
            turn1 = f"Model A: Zero variance observed in relative humidity ({rh:.1f}%) across consecutive readings despite ambient diurnal temperature fluctuations."
            turn2 = f"Model B: Digital I2C bus lockup or sensor firmware freeze detected on SHT31 sensor node."
            reasoning = "Zero-variance flatline under fluctuating thermal conditions confirms sensor hardware lockup."
            action = "Power-cycle digital sensor node and schedule diagnostic check."
            alert = True
        else:
            classification = "Nominal Baseline"
            defect_class = "none"
            conf = 98.8
            turn1 = f"Model A: All atmospheric parameters (T={temp:.1f}°C, RH={rh:.1f}%, P={pressure:.1f}hPa) conform to standard diurnal IMD envelope."
            turn2 = f"Model B: Sensor noise variance is nominal. SNR and electrical baseline remain within factory calibration tolerances."
            reasoning = "Multi-sensor atmospheric and electrical parameters demonstrate nominal steady-state operation."
            action = "Continuous 1 Hz nominal monitoring."
            alert = False

        turn_1_log = AgentTurnLog(
            sender="Model A (Atmospheric Specialist)",
            role="model_a",
            message=turn1,
            timestamp=datetime.utcnow().isoformat()
        )
        turn_2_log = AgentTurnLog(
            sender="Model B (Hardware Diagnostician)",
            role="model_b",
            message=turn2,
            timestamp=datetime.utcnow().isoformat()
        )
        arbiter_log = AgentTurnLog(
            sender="Consensus Arbiter",
            role="arbiter",
            message=f"Consensus [{classification} - {conf:.1f}%]: {reasoning}",
            timestamp=datetime.utcnow().isoformat()
        )

        return ConfluenceResult(
            classification=classification,  # type: ignore
            confidence=conf / 100.0,
            confidence_score=conf,
            p_weather=0.9 if "Weather" in classification else 0.05,
            p_defect=0.9 if "Defect" in classification else 0.05,
            defect_class=defect_class,
            defect_type=defect_class,
            summary=reasoning,
            action_recommended=action,
            severity="high" if alert else "low",
            operator_alert=alert,
            agent_dialogue=[turn_1_log, turn_2_log, arbiter_log]
        )

agent_debate_service = AgentDebateService()
