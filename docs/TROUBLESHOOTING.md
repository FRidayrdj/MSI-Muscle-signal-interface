# Troubleshooting & lessons learned

Real mistakes made while building this, kept here so they don't get repeated.

- **A "100 kΩ" resistor was actually 100 Ω.** Always measure resistors off the board with a multimeter before trusting a color code or a bag label.
- **A cheap multimeter's "smart mode" drops to continuity/resistance below about 0.4–0.5 V AC** — the beep it gives there is the meter switching modes, not a short circuit. Use manual AC-volts mode, or read small AC signals straight off the ADC instead.
- **Two amplifier outputs were once both wired into the same input row.** The result looked like valid data but was actually dominated by whichever amplifier had the lower output impedance. Rule now: only one amplifier's output feeds a given input row at a time.
- **A miswired common-mode test left an input floating and shorted the test signal to the bias point.** Symptom: the output got stuck at a supply rail, and every logged reading came back as exactly 0.00 (a high-pass filter zeroes out a constant/rail-stuck input). Lesson: if a gain stage's output is stuck at a rail, some input upstream is floating — check continuity before suspecting the signal itself.
- **A CSV logging file locked by Excel throws a permission error on write.** Fixed by always printing the reading to the console as well, and falling back to a differently-named file if the primary one is locked.
- **A bought "AD623" chip didn't match its own datasheet's gain formula.** Its measured gain fit a different formula (consistent with a different, pinout-compatible chip family) — a supply-invariance test and an input-swap test both pointed to a re-marked part rather than a damaged one. Full write-up: [clone_chip_investigation.md](clone_chip_investigation.md).

## Precautions

- Power the board only from an isolated USB power bank whenever electrodes are on skin — never from a laptop or wall-powered USB port.
- Clean skin with alcohol before placing electrodes; remove them immediately if any irritation is felt.
- Measure every resistor before using it.
- Check every supply and bias voltage with a multimeter before connecting any live test signal, to catch wiring errors early.
