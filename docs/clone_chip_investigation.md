# A bought "AD623" that didn't match its datasheet

To have a reference to compare the homemade amplifier against, I built a second in-amp around a chip marked AD623AN (DIP-8). It worked, but not like an AD623.

## What was measured

Gain-setting resistor: 11.88 kΩ + 0.99 kΩ = 12.87 kΩ (each part measured off the board). 100 Hz test tone, about 1 mV at the input, same gain stage and ADC as the homemade amp.

| | Gain |
|---|---|
| AD623 datasheet formula, G = 1 + 100 kΩ / RG | 8.77 |
| Measured in-amp gain (475 total ÷ 101) | ≈ 4.7 |
| Formula G = 1 + 50 kΩ / RG (INA128 / AD620 family) | 4.88 |

The measured gain follows the 50 kΩ formula much more closely than the AD623's.

## What was ruled out

- **Supply headroom.** Same gain with the chip on 3.3 V and on 5 V.
- **A damaged input.** Swapping the two inputs gave the same output, so the chip behaves symmetrically.

## Conclusion

Most likely a different, pinout-compatible chip carrying an AD623 marking. That can't be proven without a datasheet for the actual part, so it is a best explanation, not a certainty.

## Other observations

- Common-mode rejection was good: about 100 dB (0.42 mV residual after subtracting the 0.22 mV detection floor, for a 90.9 mV common-mode input).
- Noise was higher than the homemade amp (7.4 µV vs 2.8 µV input-referred) and spikier: peak-to-peak was 14–20× the RMS, against 7–9× for the homemade amp.
- It runs from 5 V in this build, and its output reaches the 3.3 V parts only through a 10 kΩ series resistor to protect the op-amp input.

## Takeaway

Building the amplifier myself meant every number could be checked on the bench, and that is what exposed this. A genuine AD623 from an authorised distributor would make a cleaner comparison; that is on the roadmap.

Raw data: `data/measurements.csv` and `data/measurements_v3.csv` (see `data/README.md`).
