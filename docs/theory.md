# How it works

## Why a muscle signal needs an instrumentation amplifier

A contracting muscle produces a tiny electrical signal at the skin, typically 0.1–5 mV, in the 20–450 Hz range. Two electrodes placed along the muscle pick this up as a *difference* in voltage between them.

The problem: the body also picks up a much larger signal that is common to *both* electrodes — mostly 50 Hz mains hum from the wiring around you. A plain amplifier would amplify the hum right along with the signal and swamp it.

An **instrumentation amplifier (in-amp)** solves this by amplifying only the difference between its two inputs, while rejecting whatever both inputs share. How well it does this is its **Common-Mode Rejection Ratio (CMRR)**, in decibels — higher is better.

## The in-amp, built from ordinary op-amps

Rather than buying a ready-made in-amp chip, this one is built from a quad op-amp IC (MCP6004 — four op-amps in one package), in the classic 3-op-amp topology:

- **Stage 1** — two op-amps, one per electrode, wired as buffers that share a single resistor, `Rg`. Sharing that resistor is what makes this stage amplify the *difference* between the electrodes while barely touching whatever is common to both. It also gives very high input impedance, so the circuit doesn't load down the (relatively poor) electrode-skin contact.

  `G₁ = 1 + 2R/Rg` — with R = 10 kΩ and Rg = 2.7 kΩ, G₁ ≈ 8.4

- **Stage 2** — a third op-amp wired as a classic difference amplifier with four precisely matched resistors (1%, 10 kΩ), subtracting the two stage-1 outputs. Whatever was common to both inputs cancels out here; whatever was different survives and continues on. The better these four resistors are matched, the higher the CMRR.

## Why a second gain stage — and why it blocks DC

The in-amp's output is still only a few millivolts — too small for a microcontroller's ADC to resolve well. A second op-amp stage amplifies it roughly another 100×.

Electrodes also produce a slow, drifting DC offset (a chemical effect at the skin contact) that's much bigger than the EMG signal itself. Amplifying that too would saturate the stage. So a capacitor sits in series with this stage's gain resistor, blocking DC while letting EMG frequencies (above ~16 Hz) through.

`G₂ = 1 + Rf/Rg` above cutoff `fc = 1/(2π·Rg·C)` — with Rf = 100 kΩ, Rg = 1 kΩ, C = 10 µF: G₂ ≈ 101, fc ≈ 16 Hz.

Splitting the gain this way matters: the high-pass filter has to come *before* most of the gain, or the big DC drift gets amplified first and saturates the amplifier before the signal ever gets there.

## Vmid — a virtual ground for a single supply

The circuit runs off one 3.3 V rail, no negative supply — but EMG is an AC-like signal that swings both above and below its resting value. The fix is a virtual "zero" at the midpoint, **1.65 V**, made from a resistor divider and a buffer op-amp. Every stage is biased around this point, so the signal swings above and below 1.65 V instead of above and below 0 V.

## A clean supply for the analog side

The ESP32 runs off a 5 V USB power bank. The op-amps are more sensitive to supply noise, so they're not powered directly from that 5 V line — an **LM2950-3.3 linear regulator** steps it down to a clean, stable 3.3 V, with a small capacitor on its input and output to keep it stable and filter high-frequency noise.

## Digitising and sending it out

The ESP32 samples the amplified signal at **2000 Hz** — comfortably above the EMG bandwidth (Nyquist). Digital filters clean it up further: a 20 Hz high-pass (removes remaining drift), a 50 Hz notch (a second layer of hum rejection beyond the in-amp's own CMRR), and a 450 Hz low-pass. The result streams over Wi-Fi (UDP) to a laptop, which plots it live and can log it.
