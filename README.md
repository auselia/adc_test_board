# ADS7057 test board (low-cost version)

The middle step between the perfboard and the AFE PCB. It takes the perfboard charge-amplifier output on an SMA connector, filters it, digitizes it with the ADS7057, and gives the SPI bus and a wake-up line to a ZedBoard PMOD port.

The topology is the one in the AFE v0.1 design description, rebuilt around JLCPCB **Basic** parts. Only the ADS7057, the OPA2365 and the THS4531 pay the $3.07 extended-part fee.

## Circuit

| Block | Parts | Values |
|---|---|---|
| High-pass filter | Sallen-Key, U1A | 100 pF C0G ×2, 10k, 20k: f0 = 113 kHz, Q = 0.71 (AFE: 119 kHz) |
| Gain | U1B | 1 + 3.9k/1k = 4.9 (AFE ×5 for Cf = 47 pF) |
| Low-pass filter | Sallen-Key, U2A | 2.2k ×2, C1 = 2 × 100 pF, C2 = 100 pF: f0 = 512 kHz, Q = 0.71 (AFE: 495 kHz) |
| VMID5 (2.5 V signal ground) | 10k/10k divider, U2B buffer | 10 Ω, 10 µF (same as AFE) |
| Driver | THS4531, gain 1 | 1k in and feedback; VOCM = 1k/1k divider on AVDD |
| ADC input filter | | 10 Ω per leg, 4 × 100 pF C0G = 400 pF (25 × the 16 pF sampling C) |
| AVDD (reference) | AMS1117-3.3 from 5 V | 22 µF + 4.7 µF + 100 nF |
| 5 V | 9 V → SS14 → AMS1117-5.0 | |
| Wake comparator | LM393 window | Half window = 2.5 V × (1k + Rp)/(67k + Rp) = 37–603 mV with the 20k RV1, about 7–120 mV at the perfboard output |

The two LM393 open-collector outputs are tied together and pulled up to 3.3 V. **nWAKE goes low** when the signal leaves the window.

Board: 50 × 32 mm, 2 layers, all SMD parts on top, GND pour on both layers.

## Hand-soldered parts

These are not in the JLC BOM, which keeps them out of the fees.

| Ref | Part | LCSC |
|---|---|---|
| J1 | SMA jack, vertical, 5 pins | C496549 |
| RV1 | 20k Bourns 3296W trimmer | C34845 |
| J2 | 1×2 pin header, 2.54 mm | — |
| J3 | 2×6 right-angle pin header, 2.54 mm | — |

All four are common parts at local shops.

## Connectors

- **J2:** +9 V (square pad), GND.
- **J3 PMOD:** 1 CS, 3 SDO, 4 SCLK, 5/11 GND, 6/12 3V3, 10 nWAKE.

Before you plug the board into JA–JD, check that pins 5/6 and 11/12 line up with GND/VCC on the ZedBoard silkscreen.

## SPI

- CS falling edge starts a conversion.
- Read 18 SCLK cycles on SDO. The frame is a leading 0, then D13..D0, then zeros (datasheet Fig. 1).
- SCLK can go up to 60 MHz. Start at 10–20 MHz.

## Cost (Economic PCBA, 5 bare PCBs, before shipping)

Run `python3 hw/tools/cost.py N` for N assembled boards.

| Block | Per board (2 assembled) | Per board (5 assembled) |
|---|---|---|
| Input + HPF + gain | $2.23 | $1.77 |
| LPF + VMID | $2.31 | $1.85 |
| Driver + VOCM | $4.64 | $3.72 |
| ADC + input filter + SPI resistors | $11.32 | $10.40 |
| Wake comparator (incl. trimmer) | $1.01 | $1.01 |
| Power | $1.05 | $1.05 |
| Connectors (hand-soldered) | $0.70 | $0.70 |
| Shared (PCB, setup, stencil, placement check) | $7.08 | $2.83 |
| **Total order** | **$60.68** | **$116.65** |

Shipping to Chile:
- Global Standard Direct Line: $9–12, 13–22 business days, orders up to $150.
- DHL: $42.51, 3–7 business days.
- Expect about 19% IVA on arrival.

## Files (`hw/`)

- `ADC_Test.kicad_pro/.kicad_sch/.kicad_pcb`: the KiCad 10 project.
- `ADC_Test_schematic.pdf`: the schematic.
- `fab/ADC_Test_gerbers.zip`: Gerbers and drill files.
- `fab/ADC_Test_BOM_JLC.csv` and `fab/ADC_Test_CPL_JLC.csv`: BOM and pick-and-place.
- DRC: 0 errors, 0 unconnected, 0 parity issues. The only warnings are the PMOD silkscreen clipped at the board edge, which is expected.

## Rebuild

```
python3 hw/tools/design.py hw          # schematic (then export netlist with kicad-cli)
FREEROUTING=/path/to/freerouting hw/tools/route.sh 60   # place, route, finish
hw/tools/drc.sh && hw/tools/fab.sh && python3 hw/tools/jlc_files.py
```

## At JLCPCB checkout

- Check the rotations in the parts-placement preview, and keep "Confirm Parts Placement" ($0.45). The CPL uses KiCad rotations with no JLC offsets.
- Check pin 1 of U4 (ADS7057) in particular.
- SOIC, SOT-223 and SMA-diode parts usually need a 90° or 180° offset.
