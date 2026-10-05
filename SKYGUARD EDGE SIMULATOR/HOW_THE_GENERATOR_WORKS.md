# How `generate_dataset.py` Works (Layman's Guide for Judges)

> **Quick Summary for Presenters:**  
> Use this guide to understand and confidently explain to the judges why your dataset is **100% mathematically authentic**, **stochastically random**, and **not a pre-recorded or hardcoded script**.

---

## 1. The Core Idea: Why This Proves "Zero Cheating"

When judges evaluate IoT anomaly detection systems, their #1 skepticism is usually:
> *"Did you just record a pre-made CSV or write a script that sends fake hardcoded numbers?"*

**Your Answer:**  
> *"No. We built `generate_dataset.py` using first-principles atmospheric physics and stochastic differential equations calibrated to real Indian Meteorological Department (IMD) climate records. When I run this script in front of you, it calculates new random numbers in real-time. Every single test run produces a completely unique, non-repeating dataset."*

---

## 2. The 3 Golden Rules of Real Weather (Simple Analogies)

Real atmospheric weather is governed by physical laws. Our generator simulates 3 core rules:

### Rule 1: The Sun Rule (The Diurnal Cycle)
* **The Math:** Solar Zenith Angle & Radiative Transfer equation:  
  $$T_{\text{base}}(t) = T_{\text{mean}} + \Delta T \cdot \sin\left(\frac{2\pi (t - 9)}{24}\right)$$
* **The Simple Analogy:**  
  Think of the sun like an oven burner turning on and off. The sun rises at 6:00 AM, reaches its highest point at 12:00 PM (solar noon), and sets at 6:00 PM. Because the ground takes time to absorb and re-radiate heat (thermal inertia), peak daily temperature doesn't happen at noon—it happens around **3:00 PM (15:00)**, while the coolest hour is right before sunrise at **5:00 AM**.
* **What the Judges See:** A smooth, natural 24-hour wave of temperature and solar radiation that looks like real weather station data.

---

### Rule 2: The Sponge Rule (Heat vs. Relative Humidity)
* **The Math:** Magnus-Tetens Saturation Vapor Pressure Formula:  
  $$e_s(T) = 6.1078 \exp\left(\frac{17.27 \cdot T}{T + 237.3}\right)$$
* **The Simple Analogy:**  
  Warm air acts like a **giant sponge**, while cold air is a **small sponge**.  
  When afternoon heat expands the air (makes the sponge bigger), the air can hold much more water vapor. Because the actual amount of water in the air doesn't instantly change, the *Relative Humidity (%)* naturally drops during hot afternoons and rises at night when it cools down.
* **What the Judges See:** When temperature climbs at midday, humidity naturally slopes downward. When it rains, humidity surges to near 100%. This inverse correlation proves the data follows atmospheric thermodynamics rather than random guesswork.

---

### Rule 3: The Rubber Band Rule (Ornstein-Uhlenbeck Random Walk)
* **The Math:** Mean-Reverting Stochastic Diffusion:  
  $$dX_t = \theta (\mu_t - X_t) dt + \sigma \sqrt{dt} \mathcal{N}(0, 1)$$
* **The Simple Analogy:**  
  If you simulate random weather by just rolling dice, after a few minutes your simulated temperature might wander off to $+500^\circ\text{C}$ or $-200^\circ\text{C}$ because pure random walks drift infinitely.  
  The **Ornstein-Uhlenbeck** equation acts like a **gentle rubber band**:
  1. Every second, it rolls a true Gaussian random number (giving natural micro-turbulence and breeze fluctuations).
  2. The rubber band ($\theta$) gently pulls the numbers back toward the real physical climate mean for that city.
* **What the Judges See:** Every run is genuinely random and never repeats, but the temperature stays realistically within the real physical bounds of the chosen Indian city.

---

## 3. The 4 Indian Climate Zones (IMD Baselines)

The generator provides 4 distinct micro-climates based on real Indian data:

| Region | Climate Type | What Makes It Real |
| :--- | :--- | :--- |
| **Mumbai Monsoon** | Coastal Tropical Wet | High humidity (75–98%), coastal squalls, heavy episodic downpours (up to 75 mm/h), depressed barometric pressure (~1003 hPa). |
| **Delhi Summer** | Semi-Arid Heatwave | Scorching heat (35–46°C), dry desiccating air (15–30% RH), blazing solar radiation (>1000 W/m²), gusty Loo winds. |
| **Thar Desert** | Arid Desert (Rajasthan) | Huge day/night swing (hot days, cool nights), near-zero precipitation, intense solar radiation, very low humidity. |
| **Bengaluru** | Deccan Plateau Temperate | Mild, comfortable temperatures (20–30°C), gentle plateau breezes, balanced 50–70% humidity. |

---

## 4. The Critical Difference: Weather Anomaly vs. Sensor Defect

This is the exact reason your teammate's anomaly detector exists, and what you are proving:

```
+-----------------------------------------------------------------------------------------+
|                  HOW THE SYSTEM TELLS THE DIFFERENCE                                    |
+-----------------------------------------------------------------------------------------+
|  REAL WEATHER ANOMALY (e.g. Severe Storm)  |  HARDWARE SENSOR DEFECT (e.g. Stuck/Drift) |
+--------------------------------------------+--------------------------------------------+
| • MULTI-SENSOR CORRELATION                 | • SINGLE-SENSOR ISOLATION                  |
|   Pressure plunges (-12 hPa)               |   Temperature freezes at 28.50°C           |
|   Wind gusts surge (>20 m/s)               |   WHILE solar radiation and pressure           |
|   Rain gauge spikes (>50 mm/h)             |   continue fluctuating naturally!          |
|   Temperature drops (evaporative downdraft)|                                            |
| • Follows the Laws of Physics              | • Defies the Laws of Physics (Impossible)  |
+-----------------------------------------------------------------------------------------+
```

1. **Weather Anomaly = Correlated Physics**: In a real storm, **all sensors react together** because they share the same physical atmosphere.
2. **Sensor Defect = Broken Hardware**: If only the temperature sensor flatlines or drifts $+5^\circ\text{C}$ while wind, rain, and solar stay calm, it is **impossible in nature**. Your teammate's software detects this as a **hardware fault**, not weather!

---

## 5. The 60-Second Presentation Pitch to the Judges

*(Read or paraphrase this during your live demo):*

> *"Judges, to ensure our demonstration is completely transparent and free of any pre-canned or hardcoded bias, we built a standalone generator called `generate_dataset.py`.
> 
> When I launch it here on screen, you can see the exact governing equations: the diurnal solar cycle for daytime heating, the Magnus-Tetens formula for psychrometric relative humidity, and an Ornstein-Uhlenbeck stochastic diffusion model. 
> 
> Because this uses continuous random walks, every single execution generates a fresh, uniquely randomized dataset strictly calibrated to historical India Meteorological Department records—in this case, Mumbai's coastal monsoon.
> 
> Notice the SHA-256 integrity checksum generated here: `[read first few letters of hash]`.
> 
> Now, we start our AWS Edge Simulator pointing to this exact file. As you can see on the edge dashboard, the simulator verifies line-by-line that it is streaming only this generated file. During transmission, we can inject real multi-sensor storms versus isolated hardware defects using hotkeys, proving that our anomaly detection system can tell the difference between genuine extreme weather and sensor failure."*

---

## 6. How to Run It During the Demo

### Step 1: Generate the CSV live in front of the judges
```bash
python generate_dataset.py
```
*Select `[1]` for Mumbai Monsoon, choose `120` rows, and name it `demo_mumbai.csv`.*

### Step 2: Stream that exact file through the AWS Edge Device Simulator
```bash
python run_simulator.py --csv demo_mumbai.csv
```
*The terminal UI will clearly display: `Source: CSV File: demo_mumbai.csv (Row 1/120)`.*

### Step 3: Test live hotkeys during playback
* Press **`[1]`** to trigger a **Severe Storm** (Weather Anomaly).
* Press **`[4]`** to inject a **Stuck Temperature Sensor** (Hardware Defect).
* Press **`[5]`** to inject **Calibration Drift** (Hardware Defect).
* Press **`[0]`** to reset to normal conditions.
* Press **`[Q]`** to quit.
