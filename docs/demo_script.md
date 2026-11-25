# Demo script

A step-by-step guide to running and showing the circuit live to someone else.

## Before you start

- Board powered **only** from the USB power bank (no laptop cable to the board while electrodes are on anyone).
- `msi_live.py` running on the laptop, connected to the board's Wi-Fi stream.
- Multimeter on hand for the live checks below.

## 1. Show the supply is healthy

- Probe the 3.3 V rail → should read ~3.29 V.
- Probe the Vmid test point → should read ~1.65 V.
- Say: *this is the "virtual ground" the whole circuit is biased around, since there's no negative supply.*

## 2. Show the gain, live

- Feed in the 100 Hz test tone through the resistor divider.
- Point at the live plot: input is about 1 mV, output is about 0.85 V → gain ≈ 850.
- Use the measure panel in `msi_live.py` to read the exact RMS value.

## 3. Show the noise floor

- Turn the test tone off.
- Point at the quiet baseline on the plot; read the RMS noise value from the measure panel.
- Say: *this sets the smallest signal the circuit can reliably tell apart from its own noise.*

## 4. Show real EMG

- Attach electrodes (forearm flexors + reference on the elbow).
- Rest, then clench a fist — point at the live burst on the plot (15–25× bigger than resting).

## 5. Open the board up

- Walk through the signal path on the breadboard, stage by stage: electrodes → in-amp → gain stage → ESP32 → Wi-Fi.
- Be ready to re-wire a stage and show the plot change in response, rather than only describing it.

## Troubleshooting on the spot

| Symptom | Likely cause |
|---|---|
| Output stuck at 0 V or the supply rail | An input upstream is floating — check continuity before suspecting the signal |
| Flat line, no noise at all | Wi-Fi link down, or a wire in the wrong row |
| Noisy/spiky trace | A loose connection, or a nearby mains-powered device picking up through the test leads |
