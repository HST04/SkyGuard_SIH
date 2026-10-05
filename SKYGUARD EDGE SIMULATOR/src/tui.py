import sys
import os
import time
from typing import Dict, Any, List, Optional
from collections import deque

# Ensure Windows terminal supports UTF-8 characters without cp1252 crash
if sys.platform.startswith("win"):
    import io
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except AttributeError:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.live import Live

from src.models.fault_injector import FaultInjector, AnomalyType
from src.transmitter import TransmissionResult

# Windows-specific non-blocking keyboard input
try:
    import msvcrt
    WINDOWS_KEYBOARD = True
except ImportError:
    WINDOWS_KEYBOARD = False

class EdgeSimulatorTUI:
    """Terminal dashboard providing real-time telemetry inspection and live fault injection."""

    def __init__(
        self,
        device_id: str,
        region_display: str,
        endpoint_url: str,
        source_desc: str,
        fault_injector: FaultInjector,
        initial_interval_sec: float = 1.0,
        auto_chaos: Optional[Any] = None,
    ):
        self.device_id = device_id
        self.region_display = region_display
        self.endpoint_url = endpoint_url
        self.source_desc = source_desc
        self.fault_injector = fault_injector
        self.interval_sec = initial_interval_sec
        self.auto_chaos = auto_chaos
        self.is_paused = False
        self.should_exit = False

        self.console = Console()
        self.transmission_logs = deque(maxlen=6)
        self.last_result: Optional[TransmissionResult] = None
        self.current_reading_data: Dict[str, Any] = {}
        self.baseline_reading_data: Dict[str, Any] = {}
        self.source_metadata: Dict[str, Any] = {}

    def log_transmission(self, result: TransmissionResult):
        """Appends a transmission event to the recent log window."""
        self.last_result = result
        timestamp = time.strftime("%H:%M:%S")
        status_color = "green" if result.success else "red"
        self.transmission_logs.append((timestamp, status_color, result.message))

    def update_telemetry(
        self,
        baseline_data: Dict[str, Any],
        processed_data: Dict[str, Any],
        source_metadata: Optional[Dict[str, Any]] = None,
    ):
        """Updates internal state with latest tick data."""
        self.baseline_reading_data = baseline_data
        self.current_reading_data = processed_data
        if source_metadata:
            self.source_metadata = source_metadata

    def build_header(self) -> Panel:
        """Constructs top header bar with system info and active source verification."""
        header_table = Table.grid(expand=True)
        header_table.add_column(justify="left", ratio=2)
        header_table.add_column(justify="right", ratio=1)

        pause_badge = "[bold yellow on dark_goldenrod] PAUSED [/]" if self.is_paused else "[bold green on dark_green] STREAMING [/]"
        chaos_badge = ""
        if self.auto_chaos and self.auto_chaos.enabled:
            chaos_badge = f"  |  [bold black on bright_magenta] AUTO-CHAOS ({self.auto_chaos.state_countdown:.0f}s) [/]"
        left_text = (
            f"[bold cyan]SKYGUARD AWS EDGE SIMULATOR[/]{chaos_badge}  |  "
            f"[bold white]Device:[/] [green]{self.device_id}[/]  |  "
            f"[bold white]Region:[/] {self.region_display}\n"
            f"[bold yellow]Source:[/] [bold magenta]{self.source_desc}[/]  |  "
            f"[bold white]Target:[/] {self.endpoint_url}"
        )
        right_text = f"{pause_badge}\n[dim]Interval: {self.interval_sec:.1f}s/tick[/]"

        header_table.add_row(left_text, right_text)
        return Panel(header_table, style="bold white on grey15", border_style="cyan")

    def build_telemetry_table(self) -> Panel:
        """Constructs telemetry gauge table comparing baseline vs processed reading."""
        table = Table(expand=True, box=None)
        table.add_column("Sensor Metric", style="cyan", width=22)
        table.add_column("Transmitted Value", justify="right", style="bold white", width=18)
        table.add_column("Baseline Value", justify="right", style="dim", width=16)
        table.add_column("Status / Physical Signature", justify="left")

        cur = self.current_reading_data
        base = self.baseline_reading_data

        def fmt_row(label, unit, cur_val, base_val, format_str="{:.2f}"):
            if cur_val is None:
                cur_str = "[bold red]NULL (PACKET DROP)[/]"
                status_str = "[red]I2C Bus Error / Sensor Missing[/]"
            else:
                cur_str = f"{format_str.format(cur_val)} {unit}"
                diff = cur_val - base_val if (base_val is not None) else 0.0
                if abs(diff) < 0.01:
                    status_str = "[green]Normal Physical Reading[/]"
                else:
                    sign = "+" if diff > 0 else ""
                    status_str = f"[bold yellow]Delta {sign}{diff:.2f} {unit}[/]"
            base_str = f"{format_str.format(base_val)} {unit}" if base_val is not None else "--"
            table.add_row(label, cur_str, base_str, status_str)

        fmt_row("Temp Ambient", "C", cur.get("temperature_c"), base.get("temperature_c"))
        fmt_row("Relative Humidity", "%", cur.get("humidity_pct"), base.get("humidity_pct"))
        fmt_row("Barometric Pressure", "hPa", cur.get("pressure_hpa"), base.get("pressure_hpa"))
        fmt_row("Wind Speed", "m/s", cur.get("wind_speed_mps"), base.get("wind_speed_mps"))
        fmt_row("Solar Irradiance", "W/m2", cur.get("solar_radiation_wm2"), base.get("solar_radiation_wm2"), "{:.1f}")
        fmt_row("Precipitation Rate", "mm/h", cur.get("precipitation_mmh"), base.get("precipitation_mmh"))
        fmt_row("Battery Level", "%", cur.get("battery_pct"), base.get("battery_pct"), "{:.1f}")

        return Panel(table, title="[bold white]Live Edge Sensor Telemetry[/]", border_style="blue")

    def build_status_panel(self) -> Panel:
        """Constructs banner showcasing active weather anomalies vs hardware defects."""
        gt = self.fault_injector.get_ground_truth()
        status = gt["status"]
        labels = gt["active_labels"]

        text = Text()
        if status == "NORMAL":
            text.append("\n  [STATE: NORMAL METEOROLOGICAL OPERATION]\n", style="bold green")
            text.append("  Atmospheric parameters governed by natural thermodynamic laws and stochastic drift.\n", style="dim")
        elif status == "WEATHER_ANOMALY":
            text.append(f"\n  [EVENT: GENUINE WEATHER ANOMALY]\n", style="bold black on bright_yellow")
            text.append(f"  Active Events: {', '.join(labels)}\n", style="bold yellow")
            text.append("  Physics Signature: Multi-sensor correlated response across pressure, wind, rain & temp.\n", style="italic")
        else:  # SENSOR_DEFECT
            text.append(f"\n  [ALERT: SENSOR HARDWARE DEFECT]\n", style="bold white on red")
            text.append(f"  Active Defects: {', '.join(labels)}\n", style="bold red")
            text.append("  Defect Signature: Isolated unphysical breakdown, defying atmospheric correlations.\n", style="italic yellow")

        # Add Auto-Chaos stats if active
        if self.auto_chaos and self.auto_chaos.enabled:
            phase_type = "Nominal" if self.auto_chaos.is_nominal_phase else "Anomaly Injection"
            text.append(
                f"\n  [AUTO-CHAOS ENGINE]: Phase: {phase_type} -> {self.auto_chaos.current_state_name} "
                f"(Next transition in {self.auto_chaos.state_countdown:.0f}s)\n",
                style="bold magenta",
            )

        # Add Source verification stats if available
        if self.source_metadata:
            text.append(
                f"\n  [Verifiable File Stream]: {self.source_metadata.get('source_file')} "
                f"(Row {self.source_metadata.get('source_row')} of {self.source_metadata.get('total_rows')})",
                style="dim cyan",
            )

        return Panel(text, title="[bold white]Ground Truth & Anomaly State[/]", border_style="yellow")

    def build_logs_panel(self) -> Panel:
        """Constructs recent transmission event log."""
        table = Table(expand=True, box=None)
        table.add_column("Time", style="dim", width=10)
        table.add_column("Status / Response", style="bold")

        for timestamp, color, msg in self.transmission_logs:
            table.add_row(timestamp, f"[{color}]{msg}[/]")

        if not self.transmission_logs:
            table.add_row("--:--:--", "[dim]Awaiting initial transmission tick...[/]")

        return Panel(table, title="[bold white]HTTP Dispatch Log[/]", border_style="green", height=7)

    def build_footer(self) -> Panel:
        """Constructs interactive hotkey instruction legend."""
        chaos_label = "[bold magenta][C][/] Auto-Chaos (ON)" if (self.auto_chaos and self.auto_chaos.enabled) else "[dim][C][/] Auto-Chaos (OFF)"
        legend = (
            f"{chaos_label}  |  "
            "[bold cyan][1][/] Storm  "
            "[bold cyan][2][/] Heatwave  "
            "[bold cyan][3][/] Cold Snap  |  "
            "[bold red][4][/] Stuck  "
            "[bold red][5][/] Drift  "
            "[bold red][6][/] Noise  "
            "[bold red][7][/] Drop\n"
            "[bold green][0][/] Reset Normal  |  "
            "[bold white][+][/]/[bold white][-][/] Speed  |  "
            "[bold white][Space][/] Pause/Resume  |  "
            "[bold white][Q][/] Quit"
        )
        return Panel(legend, style="dim white", border_style="grey50")

    def render(self) -> Layout:
        """Assembles full terminal layout."""
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=4),
            Layout(name="main", ratio=1),
            Layout(name="logs", size=7),
            Layout(name="footer", size=3),
        )

        layout["main"].split_row(
            Layout(name="telemetry", ratio=3),
            Layout(name="status", ratio=2),
        )

        layout["header"].update(self.build_header())
        layout["telemetry"].update(self.build_telemetry_table())
        layout["status"].update(self.build_status_panel())
        layout["logs"].update(self.build_logs_panel())
        layout["footer"].update(self.build_footer())
        return layout

    def check_hotkeys(self):
        """Polls keyboard input non-blockingly and executes corresponding hotkey command."""
        if not WINDOWS_KEYBOARD:
            return

        while msvcrt.kbhit():
            ch = msvcrt.getch()
            try:
                char = ch.decode("utf-8").lower()
            except UnicodeDecodeError:
                continue

            if char == "c" and self.auto_chaos:
                self.auto_chaos.toggle()
            elif char == "1":
                self.fault_injector.set_weather_anomaly(AnomalyType.WEATHER_SEVERE_STORM)
            elif char == "2":
                self.fault_injector.set_weather_anomaly(AnomalyType.WEATHER_HEATWAVE)
            elif char == "3":
                self.fault_injector.set_weather_anomaly(AnomalyType.WEATHER_COLD_SNAP)
            elif char == "4":
                self.fault_injector.toggle_defect(AnomalyType.DEFECT_STUCK_SENSOR)
            elif char == "5":
                self.fault_injector.toggle_defect(AnomalyType.DEFECT_CALIBRATION_DRIFT)
            elif char == "6":
                self.fault_injector.toggle_defect(AnomalyType.DEFECT_ERRATIC_NOISE)
            elif char == "7":
                self.fault_injector.toggle_defect(AnomalyType.DEFECT_PACKET_DROP_NULL)
            elif char == "0":
                if self.auto_chaos and self.auto_chaos.enabled:
                    self.auto_chaos.toggle()
                self.fault_injector.clear_all()
            elif char == "+":
                self.interval_sec = max(0.1, round(self.interval_sec - 0.2, 1))
            elif char == "-":
                self.interval_sec = min(5.0, round(self.interval_sec + 0.2, 1))
            elif char == " ":
                self.is_paused = not self.is_paused
            elif char == "q":
                self.should_exit = True
