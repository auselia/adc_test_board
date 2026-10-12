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

## Hand-soldered parts

These are not in the JLC BOM, which keeps them out of the fees.

| Ref | Part | LCSC |
|---|---|---|
| J1, J4 | SMA jack, vertical, 5 pins (input, MON) | C496549 |
| RV1 | 20k Bourns 3296W trimmer | C34845 |
| J2 | 1×2 pin header, 2.54 mm | — |
| J3 | 2×6 right-angle pin header, 2.54 mm | — |

All four are common parts at local shops.

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

Always 5 bare PCBs. The figures below predate the MON output and regulator changes. Those add about $3.30 per order (tantalum fee) plus a few cents per board. Run the script for current numbers. N = boards assembled. For the full line-item list, run `python3 hw/tools/cost.py 2 3 5`.

| | 2 boards | 3 boards | 5 boards |
|---|---|---|---|
| Components (JLC buys and places) | $30.43 | $45.65 | $76.08 |
| PCB fabrication (5 pcs) | $4.00 | $4.00 | $4.00 |
| Setup + stencil + placement check | $10.16 | $10.16 | $10.16 |
| Extended-part fee (ADS7057, OPA2365, THS4531) | $9.21 | $9.21 | $9.21 |
| X-ray inspection of the ADS7057 ($1.64 each) | $3.28 | $4.92 | $8.20 |
| SMT joints (150/board × $0.0016) | $0.48 | $0.72 | $1.20 |
| **JLCPCB order** | **$57.56** | **$74.66** | **$108.85** |
| Shipping, Global Standard (13–22 days) | $9.00 | $9.00 | $9.00 |
| IVA 19% | $12.65 | $15.90 | $22.39 |
| Hand-soldered parts (SMA, trimmer, headers) | $3.12 | $4.68 | $7.80 |
| **Total** | **$82.33** | **$104.24** | **$148.05** |
| Per board | $41.17 | $34.75 | $29.61 |

DHL instead of Global Standard: +$33.51 (3–7 days).

Prices were checked on 2026-10-12 in the JLCPCB parts library and on the PCBA fee page. Upload the files to get the official quote.

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
