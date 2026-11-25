# Deep dive: the regulator and the gain stage

These are two small pieces that are easy to skim past, but each one is solving a specific problem.

## Why a separate voltage regulator

The whole board could, in principle, run straight off the 5 V power bank. Two things argue against that:

1. **The op-amps are rated for a lower supply.** MCP6004 is happy up to 6 V, but running right at the edge of a part's rating isn't where you want your signal chain's noise floor to be.
2. **A clean, stable rail matters more here than it looks.** Every bias point in this circuit — Vmid, every op-amp's reference — hangs off the 3.3 V rail. Any ripple or noise on that rail shows up directly as noise on the output. An LM2950-3.3 linear regulator, with a small input and output capacitor, gives a quiet, steady 3.3 V instead of whatever the power bank's 5 V output is doing.

**How to check it's working:** measure across the regulator's OUT and GND pins — should read close to 3.3 V (measured 3.294 V here) regardless of what's happening elsewhere on the board.

## Why the gain is split into two stages instead of one

The in-amp's output is only a few millivolts — not enough for the ADC to resolve well — so a second stage amplifies it further, by about 100×. But it can't be *just* a plain amplifier:

- Electrodes produce a slow DC offset from the skin contact, usually much bigger than the EMG signal.
- If you amplified that offset by 100× along with the real signal, the op-amp would simply saturate (slam against a supply rail) and you'd see nothing useful.

So this stage includes a capacitor in series with its gain resistor. A capacitor blocks DC (zero frequency) and passes AC — so the slow offset is blocked, while EMG frequencies (above ~16 Hz) sail through and get amplified.

```
G = 1 + Rf/Rg          (above the cutoff)
fc = 1 / (2π · Rg · C)
```

With Rf = 100 kΩ, Rg = 1 kΩ, C = 10 µF: gain ≈ 101, cutoff ≈ 16 Hz.

**How to check it's working:** with no input signal, the stage's output should sit at Vmid (1.65 V) — if it's pinned at 0 V or the supply rail instead, something upstream is floating or shorted.

**A question worth being ready for:** *why not put all the gain in one stage, right after the in-amp?* Because the high-pass filter needs to come before the bulk of the gain. Put the big gain first, and you amplify the DC drift right along with the signal — by the time the high-pass filter sees it, the op-amp is already saturated.
