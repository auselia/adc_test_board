# ADS7057 test board (low-cost version)

The middle step between the perfboard and the AFE PCB. It takes the perfboard charge-amplifier output on an SMA connector, filters it, digitizes it with the ADS7057, and gives the SPI bus and a wake-up line to a ZedBoard PMOD port.

The topology is the one in the AFE v0.1 design description, rebuilt around JLCPCB **Basic** parts. Only the ADS7057, the OPA2365 and the THS4531 pay the $3.07 extended-part fee.

## Uses

The board serves two purposes. In the plant experiments, four boards sit on ZedBoard PMODs JA to JD: two control plants, one drying plant and one reference sensor. Each board is one channel, and an FPGA capture design reads all four. For Croc validation, one board checks the ADC and the wake path. Order 5 assembled boards: 4 channels plus a spare.

## Circuit

| Block | Parts | Values |
|---|---|---|
| High-pass filter | Sallen-Key, U1A | 100 pF C0G ×2, 10k, 20k: f0 = 113 kHz, Q = 0.71 (AFE: 119 kHz) |
| Gain | U1B | 1 + 3.9k/1k = 4.9 (AFE ×5 for Cf = 47 pF) |
| Low-pass filter | Sallen-Key, U2A | 2.2k ×2, C1 = 2 × 100 pF, C2 = 100 pF: f0 = 512 kHz, Q = 0.71 (AFE: 495 kHz) |
| VMID5 (2.5 V signal ground) | 10k/10k divider, U2B buffer | 10 Ω, 10 µF (same as AFE) |
| Driver | THS4531, gain 1 | 1k in and feedback; VOCM = 1k/1k divider on AVDD |
| ADC input filter | | 10 Ω per leg, 4 × 100 pF C0G = 400 pF (25 × the 16 pF sampling C) |
| AVDD (reference) | XC6206P332 from 5 V | 1 µF at the LDO, 4.7 µF + 100 nF at the ADS7057 AVDD pin |
| 5 V | 9 V → SS14 → AMS1117-5.0 | 22 µF tantalum output (C29) |
| MON output | 51 Ω from LPF_OUT to SMA J4 | The scope sees the same signal the ADC samples |
| nWAKE filter | C31, 0603 to GND near J3 | Not fitted (DNP). No hysteresis, since the outputs are wired together |
| Wake comparator | LM393 window | Half window = 2.5 V × (1k + Rp)/(67k + Rp) = 37–603 mV with the 20k RV1, about 7–120 mV at the perfboard output |

The two LM393 open-collector outputs are tied together and pulled up to 3.3 V. **nWAKE goes low** when the signal leaves the window.

Board: 50 × 32 mm, 2 layers, all SMD parts on top, GND pour on both layers.

## Regulators

The AMS1117 datasheet (LCSC C6186, C6187) says the output capacitor is part of the frequency compensation. It asks for 22 µF solid tantalum and gives no ESR range. So the board uses option (b) for AVDD: the XC6206P332 (C5446, Basic) is stable with ceramic capacitors. It has no noise spec. Reference noise scales with the signal, and events reach 17 % of full scale, so 500 µV rms on AVDD adds about 0.2 LSB. The 5 V AMS1117 keeps option (a): a 22 µF tantalum (C11366) on its output. That part is Extended and adds one $3.07 fee.

## Through-hole parts

JLCPCB solders these. They are in the BOM and the pick-and-place file.

| Ref | Part | LCSC |
|---|---|---|
| J1, J4 | SMA jack, vertical, 5 pins (input, MON) | C496549 |
| RV1 | 20k Bourns 3296W trimmer | C34845 |
| J2 | 1×2 pin header, 2.54 mm | C492401 |
| J3 | 2×6 right-angle pin header, 2.54 mm | C60565 |

If JLCPCB declines a through-hole part, delete its line from the BOM and solder it yourself. The board has the same footprints either way.

## Connectors

- **J1:** SMA input from the perfboard.
- **J4 MON:** SMA monitor output, LPF_OUT through 51 Ω.
- **J2:** +9 V (square pad), GND.
- **H1, H2:** M3 mounting holes.
- **CH box:** silkscreen field at the top edge. Write the channel number by hand.
- **J3 PMOD:** 1 CS, 3 SDO, 4 SCLK, 5/11 GND, 6/12 3V3, 10 nWAKE.

Before you plug the board into JA–JD, check that pins 5/6 and 11/12 line up with GND/VCC on the ZedBoard silkscreen.

## SPI

- CS falling edge starts a conversion.
- Read 18 SCLK cycles on SDO. The frame is a leading 0, then D13..D0, then zeros (datasheet Fig. 1).
- SCLK can go up to 60 MHz. Start at 10–20 MHz.

## Cost (JLCPCB Economic PCBA, shipped to Chile)

Always 5 bare PCBs. N = boards assembled. Run `python3 hw/tools/cost.py 2 3 5` for the figures below. It reads the BOM in `hw/fab`.

JLCPCB assembles the through-hole parts too (two SMAs, the trimmer and two headers). Economic assembly allows through-hole parts on the top side, which is the only side used. The cost depends on one detail I could not confirm without an order: whether the four through-hole part types also pay the $3.07 extended-part fee. The table gives both cases.

| | 2 boards | 3 boards | 5 boards |
|---|---|---|---|
| Components (JLC buys and places) | $33.33 | $49.99 | $83.32 |
| JLC fees (PCB, setup, stencil, 4 extended parts, X-ray, joints, through-hole labor) | $34.68 | $37.01 | $41.67 |
| Shipping, Global Standard (13–22 days) | $9.00 | $9.00 | $9.00 |
| IVA 19% | $14.63 | $18.24 | $25.46 |
| **Total, JLC solders through-hole (low)** | **$91.64** | **$114.24** | **$159.45** |
| **Total, JLC solders through-hole (high)** | **$106.25** | **$128.86** | **$174.07** |
| Total if you solder the through-hole parts yourself | $85.66 | $107.40 | $150.88 |

The difference between letting JLC solder and doing it yourself is about $6 to $9 for 2 to 5 boards in the low case. The high case adds $14.63.

DHL instead of Global Standard: +$33.51 (3–7 days). Prices were checked on 2026-10-12. Upload the files to get the official quote.

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

- Check the rotations in the parts-placement preview, and keep "Confirm Parts Placement" ($0.45). The CPL applies the JLC offsets for SOIC (+270), SOT-23 (−90), SOT-223 (+180) and tantalum (+180).
- Not covered by the offset table, so check them by eye: ADS7057 U4 (pin 1), SS14 D1 (cathode band), and the through-hole J1 to J4 and RV1.
- Check pin 1 of U4 (ADS7057) in particular.
