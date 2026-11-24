# Bill of materials

| Component | Value / part | Purpose |
|---|---|---|
| Quad op-amp IC | MCP6004 (×2) | Builds the in-amp and the gain stage |
| Voltage regulator | LM2950-3.3 (TO-92) | Clean 3.3 V supply for the analog circuit |
| Gain-setting resistor Rg (in-amp) | 2.7 kΩ, 5% | Sets in-amp gain G₁ ≈ 8.4 |
| Matched resistors (×4) | 10 kΩ, 1% | Difference-amplifier stage; sets CMRR |
| Vmid divider resistors | 10 kΩ (×2), 5% | Generates the 1.65 V bias point |
| Gain-stage resistors | Rf = 100 kΩ, Rg = 1 kΩ | Sets gain-stage gain G₂ ≈ 101 |
| DC-blocking capacitor | 10 µF electrolytic | Blocks electrode DC offset (fc ≈ 16 Hz) |
| Regulator capacitors | 1 µF (in), 10 µF (out) | Supply stability / noise filtering |
| Microcontroller | ESP32 DevKit (ESP-WROOM-32) | 2 kHz ADC sampling, digital filtering, Wi-Fi |
| Electrodes | Ag/AgCl snap electrodes (×2 per channel + reference) | Pick up the EMG signal from the forearm |
| Power source | 5 V USB power bank | Isolated supply — no mains connection to the body |
| Breadboards, jumper wires, multimeter | — | Prototyping and measurement |
