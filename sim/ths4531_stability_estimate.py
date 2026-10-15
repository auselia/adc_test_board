"""THS4531 loop phase margin into the ADC input filter, assumption-based (not the TI model).
The TI PSPICE model gives wrong results in ngspice (the output rolls off at 97 kHz with a 400 pF load, flat with no load),
and LTspice batch mode does not run here. So this uses a one-pole amplifier (GBW 27 MHz, datasheet) with an assumed second
pole and an assumed open-loop output impedance Zo, and the real load (Ro, 400 pF across = 800 pF per leg, 2k feedback).
Run: python3 sim/ths4531_stability_estimate.py
"""
import numpy as np
f = np.logspace(5, 9, 6000); s = 2j * np.pi * f


def pm(f2, Zo, Ro=10, C=800e-12, gbw=27e6):
    A = gbw / (1j * f) / (1 + 1j * f / f2)
    Zl = 1 / (1 / 2000.0 + 1 / (Ro + 1 / (s * C)))
    T = A * 0.5 * Zl / (Zo + Zl)
    i = np.argmin(abs(abs(T) - 1))
    return f[i] / 1e6, (180 + np.degrees(np.angle(T[i]))) % 360


print('phase margin in degrees (crossover MHz). Rows: assumed open-loop Zo. Columns: assumed second pole 50/100/200 MHz')
for Zo in (2.5, 10, 25, 50):
    print(f'Zo {Zo:5.1f}', ['%.0f (%.1f)' % (pm(f2 * 1e6, Zo)[1], pm(f2 * 1e6, Zo)[0]) for f2 in (50, 100, 200)])
for Ro in (5, 10, 20, 30):
    print(f'Ro {Ro:2d} ohm, Zo 25, f2 100 MHz: {pm(100e6, 25, Ro=Ro)[1]:.0f} deg')
