# FAQ

**What does this circuit actually do, in one sentence?**
Picks a tiny muscle signal out of a sea of electrical noise, makes it about 850× bigger, and sends it to a laptop over Wi-Fi.

**What's CMRR and why does it matter?**
Common-Mode Rejection Ratio — how well the amplifier ignores signals that are the same on both inputs (like mains hum) while still amplifying the signal that's different between them. Measured in decibels; higher is better. This one measures about 91 dB.

**Why build your own instrumentation amplifier instead of buying one?**
Mainly to understand it properly, end to end — and it turned out to be a useful decision, since it meant everything could be measured and verified rather than trusted from a datasheet. (See [the clone-chip investigation](clone_chip_investigation.md) — a bought part turned out to behave like a different chip.)

**What's input impedance and why does it matter here?**
How much current the amplifier draws from the source. Electrode-skin contact is a relatively poor, high-resistance connection — a low-input-impedance amplifier would load it down and distort the signal. The buffer stage gives very high input impedance.

**Why 1% resistors in the subtractor stage but 5% elsewhere?**
The subtractor's resistor matching directly sets CMRR — any mismatch there leaks common-mode signal straight through. Elsewhere, resistor tolerance only causes a small gain error.

**What happens if Rg changes?**
Gain is inversely related to it (`G₁ = 1 + 2R/Rg`): a bigger Rg means less gain, a smaller Rg means more.

**Why does a capacitor "block DC"?**
A capacitor's impedance is `1/(2πfC)` — infinite at f = 0 (DC), small at higher frequencies. DC can't pass; AC can.

**Why sample at 2000 Hz when the signal tops out around 450 Hz?**
Nyquist: you need to sample at more than twice the highest frequency of interest or the signal distorts (aliasing). 2000 Hz gives a comfortable margin above 450 Hz.

**Biggest source of error?**
5% resistor tolerance on the gain-setting resistors (~±4.5% gain error), plus electrode-skin contact variability session to session.

**Biggest safety consideration?**
Never connect the person wearing electrodes to anything mains-powered — power the board only from an isolated USB power bank, no laptop cable while electrodes are attached.

**What's left to build?**
A second channel, a trained gesture-recognition model, and a 3D hand that mirrors the gesture — see `ROADMAP.md`.
