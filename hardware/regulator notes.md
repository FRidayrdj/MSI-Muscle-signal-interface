# Regulator notes

Part: UTC LM2950G-33 (LP2950-3.3 equivalent), TO-92. The marking reads "33 519": 33 is the 3.3 V version, 519 is the date code.

Pinout: flat face toward you, legs down, left to right: Output, GND, Input.

## Capacitors

- Input: 1 µF electrolytic (+ to the input pin, stripe leg to ground). It smooths the 5 V coming from the power bank.
- Output: 10 µF electrolytic, same polarity. The regulator needs an output capacitor to stay stable, and the extra capacitance also helps filter noise on the 3.3 V rail.
