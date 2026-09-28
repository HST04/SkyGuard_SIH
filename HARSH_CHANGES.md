# Harsh: maintenance + imputation, fitted into main

Unzip at the repo root on `feat/harsh`. Existing files are only extended, nothing removed.

New files
- backend/services/predictive_maintenance.py   drift tracker
- backend/services/imputation_engine.py        suggested values for a faulty sensor
- backend/services/sensor_health.py            runs both, once per packet
- backend/routers/sensor_health.py             GET /api/v1/maintenance, POST /api/v1/imputation/accept
- backend/tests/test_sensor_health.py

Changed files
- backend/services/telemetry_ingestion.py      calls sensor_health.process() before broadcasting
- backend/models/schemas.py                    TelemetryPayload gets maintenance, imputation, weather; new ImputationAcceptRequest
- backend/main.py                              registers the new router

Test: `cd backend && python -m pytest tests -q` (12 pass).

## For Shreyansh
The existing `telemetry` SSE event now carries three extra fields. Add them to `TelemetryPayload` in `src/lib/types.ts`:

    maintenance?: { humidity: { status: 'Learning'|'Healthy'|'Watch'|'At Risk'|'Recalibrate Now';
                                drift_sigma: number|null; progress: number;
                                days_to_recalibration: number|null; trend?: string; warmup?: string };
                    temperature: { status: 'Not Tracked'; note: string };
                    pressure:    { status: 'Not Tracked'; note: string } };
    imputation?: { active: boolean; sensor?: 'humidity'|'temperature'|'pressure';
                   reported?: number; suggested?: number|null; method?: string;
                   uncertainty?: number|null; reason?: 'anomaly'|'drift' };
    weather?: { event: boolean; cooldown: boolean; source: string };

When humidity drift reaches At Risk, an `anomaly` event with `anomaly_type: "sensor_health"` is sent once.
The Accept & Impute button: POST /api/v1/imputation/accept with
{ station_id, sensor, suggested, reported, timestamp, sequence, method }. The server then sends an `imputation_accepted` SSE event.

Note: `frontend/src/lib/` is missing from the repo. The root .gitignore has `lib/`
(from a Python template), so api.ts and types.ts were never committed. Add `!frontend/src/lib/` to .gitignore and push them.

## For Mudit
When the confluence engine exists, pass its answer in telemetry_ingestion.py:
`sensor_health.process(payload, detected_anomaly, weather_event=<True if natural weather>)`.
Until then a stand-in rule is used (pressure falls 5+ hPa and humidity rises 5+% within 2 minutes).

## Settings
- MAINT_WARMUP_SAMPLES (600): the tracker learns what's normal from the first 10 minutes of live data. Let the stream run 10 minutes before recording.
- WEATHER_COOLDOWN_S (1800): drift tracking pauses this long after a storm.
- MAINT_TIME_SCALE (1.0): only for a sped-up demo countdown. If used, say so in the video.
