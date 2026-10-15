# ADS7057 test board (low-cost version)

The middle step between the perfboard and the AFE PCB. It takes the signal from the sensor, filters it, digitizes it with the ADS7057, and gives the SPI bus and a wake-up line to a ZedBoard PMOD port.

There are **two boards**, ordered separately:

| Board | What it is | Size |
|---|---|---|
| ADC test board (`ADC_Test`) | HPF, gain, LPF, driver, ADS7057, wake-up comparator, PMOD, 9 V supply, bias-T for the head | 57 × 32 mm |
| Sensor head (`ADC_Head`) | The perfboard charge amplifier on a PCB. The piezo wires solder to it. It is powered through the coax | 10 × 22 mm |

The head connects to **SENSOR IN (J1)** with one coax cable. The coax carries 5 V to the head (a bias-T) and the signal back. The perfboard is replaced by the head. To use a function generator instead, remove R26 so the centre pin carries no DC.

The topology is the one in the AFE v0.1 design description, rebuilt around JLCPCB **Basic** parts. The extended-part fee ($3.09 per type) is paid for the ADS7057, OPA2365, THS4531, the tantalum C29 and the 470 µH inductor (both boards), plus the OPA365 on the head.

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
| Bias-T on SENSOR IN (J1) | R26 47R + C32 10 µF, L2 470 µH, C33 100 nF, R27 1M | 5 V reaches the coax centre through 47 Ω and 470 µH. C33 passes the head signal to SIG_IN. R27 sets the DC level of SIG_IN to VMID5 |
| Wake comparator | LM393 window | Half window = 2.5 V × (1k + Rp)/(67k + Rp) = 37–603 mV with the 20k RV1, about 7–120 mV at the perfboard output |

The two LM393 open-collector outputs are tied together and pulled up to 3.3 V. **nWAKE goes low** when the signal leaves the window.

Main board: 57 × 32 mm, 2 layers, all SMD parts on top, GND pour on both layers.

### Sensor head

The perfboard circuit (TRL3 schematic), on its own board:

| Block | Parts | Values |
|---|---|---|
| Charge amplifier | U8 OPA365 (SOT-23-5) | Same silicon as the OPA2365 on the main board, 50 MHz. Perfboard used an OPA1642 on 9 V |
| Feedback | R28 1 MΩ, C34 47 pF C0G | Same as the perfboard. Corner 3.4 kHz, gain 1/Cf |
| Reference | R29, R30 10k, C35 10 µF | VREF = V+/2 = 2.5 V (perfboard: 4.5 V on 9 V) |
| Output | R31 49.9 Ω, C38 100 nF | Same 50 Ω, AC-coupled onto the coax |
| Power from the coax | L1 470 µH, C36 100 nF, C37 10 µF | 5 V comes in on the coax centre. About 4.7 mA |
| Piezo | TP1 (+, to the summing node), TP2 (−, to ground) | Two 1 mm holes, 4.8 mm apart. The piezo sits on the other face |
| Output connector | J6 SMA, vertical | To SENSOR IN (J1) on the main board |

Differences from the perfboard that you should know about:

- Supply 5 V instead of 9 V, so the output rests at 2.5 V, not 4.8 V. The coupling capacitors make this invisible downstream.
- The OPA365 has 4.5× the gain-bandwidth of the OPA1642, so the charge amplifier loses 0.2 dB at 250 kHz instead of 2.2 dB. Events read about 25 % higher than on the perfboard for the same charge.
- The bias-T costs 0.16 dB at 250 kHz and 19 dB at 10 kHz (`python3 sim/head_bias_t.py`).
- The board is 22 mm long, not the 20 mm of the capsule drawing v3. The extra 2 mm sticks out of the capsule with the SMA.

## Silkscreen

| Label | What it is |
|---|---|
| SENSOR IN, +5V on centre (J1) | SMA input for the sensor head. The centre pin carries 5 V while R26 is fitted. Remove R26 before you connect a function generator. |
| SCOPE OUT (J4) | SMA monitor output. It carries the same signal the ADC samples, through 51 Ω. Use a 1 MΩ scope input. A 50 Ω input halves the signal. |
| +9V / GND (J2) | 9 V battery input. The square pad is +9V. |
| WAKE LEVEL (RV1) | Trimmer that sets how large a signal must be to pull nWAKE low. Clockwise should widen the window. Check with a multimeter on the 33k resistors. |
| CH and box | Write the channel number in the box with a marker. Four boards go on JA to JD. |
| 1 (next to J3) | PMOD pin 1. The pin list is on the back of the board. |
| Leaf and waves | Auselia mark. |

Reference designators (R1, C4 and so on) are on the F.Fab layer, not on the silkscreen. Open the KiCad file to see them.

## Regulators

The AMS1117 datasheet (LCSC C6186, C6187) says the output capacitor is part of the frequency compensation. It asks for 22 µF solid tantalum and gives no ESR range. So the board uses option (b) for AVDD: the XC6206P332 (C5446, Basic) is stable with ceramic capacitors. It has no noise spec. Reference noise scales with the signal, and events reach 17 % of full scale, so 500 µV rms on AVDD adds about 0.2 LSB. The 5 V AMS1117 keeps option (a): a 22 µF tantalum (C11366) on its output. That part is Extended and adds one $3.07 fee.

## Through-hole parts

JLCPCB solders these. They are in the BOM and the pick-and-place file.

| Ref | Part | LCSC |
|---|---|---|
| J1, J4 (and J6 on the head) | SMA jack, vertical, 5 pins (sensor in, MON, head out) | C496549 |
| RV1 | 20k Bourns 3296W trimmer | C34845 |
| J2 | 1×2 pin header, 2.54 mm | C492401 |
| J3 | 2×6 right-angle pin header, 2.54 mm | C60565 |

If JLCPCB declines a through-hole part, delete its line from the BOM and solder it yourself. The board has the same footprints either way.

## Connectors

- **J1 SENSOR IN:** SMA for the sensor head, carries +5 V on the centre pin (R26 fitted).
- **J4 MON:** SMA monitor output, LPF_OUT through 51 Ω.
- **J2:** +9 V (square pad), GND.
- **H1, H2:** M3 mounting holes.
- **CH box:** silkscreen field at the top edge. Write the channel number by hand.
- **J3 PMOD:** 1 CS, 3 SDO, 4 SCLK, 5/11 GND, 6/12 3V3, 10 nWAKE.

Before you plug the board into JA–JD, check that pins 5/6 and 11/12 line up with GND/VCC on the ZedBoard silkscreen.

## SPI

- CS falling edge starts a conversion.
- Read 18 SCLK cycles on SDO. The frame is a leading 0, then D13..D0, then zeros (datasheet Fig. 1).
- Each frame returns the result of the **previous** conversion. The first frame after power-up returns all zeros.
- After power-up, send **24 SCLKs** in the first frame. That starts the offset calibration (datasheet 8.4.3.1), and SDO stays at zero. Then wait at least 95 ns before the next CS fall.
- Repeat the calibration when AVDD or the temperature changes a lot.
- SCLK can go up to 60 MHz. Start at 10–20 MHz.

## Cost (JLCPCB Economic PCBA, shipped to Chile)

The two boards are two JLCPCB orders (or one checkout with two designs). `python3 hw/tools/cost.py` prints the model. It is calibrated on the real quote of the first revision (2026-10-12, 5 boards, $114.36, no bias-T). The new parts have list prices from the JLCPCB library of 2026-10-15. The v2 numbers are estimates until you upload the files.

| Order | Goods (parts + PCB + fees) | Parts | Fees |
|---|---|---|---|
| ADC board × 2 | $66.99 | $32.32 | $30.67 |
| ADC board × 3 | $84.06 | $48.48 | $31.58 |
| ADC board × 5 | $118.20 | $80.80 | $33.40 |
| Sensor head × 5 | $40.76 | $15.64 | $21.12 |
| Sensor head × 10 | $57.94 | $31.29 | $22.65 |

Both orders together, with shipping (Global Standard $10.75 per parcel) and 19 % IVA:

| | One parcel | Two parcels |
|---|---|---|
| 2 ADC boards + 5 heads | $141.01 | $153.81 |
| 2 ADC boards + 10 heads | $161.46 | $174.25 |

- The head's fixed fees (setup $8.24, stencil $1.55, hand-solder labor $3.61, PCB $4.00, one more extended type) are about $20 per order. A single panel would save them, but it forces equal quantities and mouse-bite tabs. Two orders let you buy 2 ADC boards and 10 heads.
- The OPA365 ($2.67) is the most expensive part of a head. The OPA2365 (SOIC-8) would be $1.38 and needs no new extended fee, but it does not fit in 10 mm × 22 mm with the SMA.
- DHL Express costs about $32 more per parcel (3–7 days).
- "Confirm Parts Placement" adds $0.45 per order.

First revision, real quote for 5 boards (no head, no bias-T):

| Item | Price |
|---|---|
| PCB, 5 pcs, 2 layers, HASL with lead, 24 h build | $4.00 |
| Components, 27 part types | $80.14 |
| Setup fee | $8.24 |
| Stencil | $1.55 |
| Extended components fee, 4 types | $12.36 |
| SMT assembly | $1.32 |
| Hand-soldering labor | $3.61 |
| Manual assembly, through-hole joints | $2.23 |
| Nitrogen reflow | $0.91 |
| **Order total** | **$114.36** |

The ADS7057 pays no X-ray fee in Economic assembly. The through-hole part types (SMA, headers, trimmer) pay no extended-part fee.

## JLCPCB placement check

The JLCPCB viewer showed four problems on the first revision, and the CPL now corrects them. **New parts are not checked yet:** U8 (SOT-23-5, head), L1 and L2 (1210 inductors), J6 (SMA). Look at them in the viewer. These rotations assume JLCPCB counts counter-clockwise like KiCad, so check them again in the viewer after you upload the new CPL.

| Part | Problem | CPL rotation |
|---|---|---|
| U5 (XC6206) | Model rotated 90° against the pads | 270 → 180 |
| C29 (tantalum) | Plus sign on the wrong side | 180 → 0 |
| J2 (1×2 header) | Pins horizontal, pads vertical | 0 → 90 |
| J3 (2×6 header) | Row horizontal, pads vertical | 0 → 90 |

U1, U2, U3, U6 (pin 1), U4 (pin 1), U7, D1 (cathode) and the SMD passives matched the pads.

RV1 (trimmer) had the right rotation but the wrong position. JLCPCB draws its model about 2.5 mm to the right and 1 mm below the footprint, so it overhung the board edge. JLCPCB places through-hole parts from the model origin, not from pin 1. The CPL now shifts RV1 by −2.54 mm in x and +1.0 mm in y. J1 and J4 (SMA) have their four legs on the pads. J2 and J3 may have a similar offset, which can only be read after the rotation change, so check them in the viewer.

## Verification

| Check | Status | Result |
|---|---|---|
| ERC, DRC, schematic-to-board parity | Done | 0 errors, 0 unconnected, 0 mismatches |
| Pinouts and polarity against the datasheets | Done | All ICs, SS14, tantalum |
| JLCPCB placement viewer | Done once | 4 rotations fixed, RV1 moved. Check again after the new CPL |
| DC bias, AC response, noise | Done | Table below |
| Tolerance Monte Carlo, 150 runs | Done | 10 kHz loss under 40 dB in 11 of 150 runs |
| 250 kHz burst, headroom | Done | A 120 mV event reaches 16 % of full scale. Clipping starts near 0.54 V |
| ADC input settling | Done | 30 to 55 ns against 95 ns minimum |
| Cable on the SCOPE OUT SMA | Done | No peaking up to 5 nF |
| THS4531 into 10 Ω and 400 pF | **Open** | TI's model fails in ngspice and LTspice batch mode does not run here. `sim/ths4531_stability_estimate.py` gives 48 to 77° of margin for assumed output impedances. Run `sim/ltspice/ths4531_cap_load.cir` in LTspice |
| Head and bias-T, ngspice with the OPA365 model | Done | 0.16 dB loss at 250 kHz, 19 dB at 10 kHz, 4.7 mA from 5 V. `python3 sim/head_bias_t.py` |
| Head board, DRC | Done | 0 unconnected, no electrical errors. Two courtyard overlaps (TP/L1 and C34/R28) |
| Head: piezo wires, strain relief, RTV | Open | Mechanical, on the bench |
| Print the PCB 1:1 and test-fit parts | Open | |
| Fit on the ZedBoard PMOD | Open | |
| Bench bring-up | Open | See below |

`sim/vendor_chain.py` runs the checks and `sim/vendor_results.txt` holds the output. The OPA365 is TI's own model. The THS4531 is a datasheet-based model (27 MHz, 2.5 Ω), because TI's model gives a −3 dB point at 17 kHz in ngspice. The ADC input is the datasheet model: 50 Ω and 16 pF per leg. Run `python3 sim/models/fetch_models.py` to download the TI models, which are not stored in the repo.

| Result | Value | Target |
|---|---|---|
| DC points | VMID5 2.50 V, VOCM 1.65 V, ADC inputs 1.65 V | |
| Gain at 250 kHz, SMA to ADC | 12.2 dB (×4.1) | |
| Flatness 230 to 280 kHz | 0.08 dB | < 1 dB |
| Loss at 10 kHz, re 250 kHz | 40.5 dB, worst of 150 runs 39.7 dB | ≥ 40 dB |
| Loss at 2 MHz | 24.0 dB | ≥ 20 dB |
| −3 dB band | 106 to 502 kHz | |
| Board noise at the ADC | 77 µV rms, 0.2 LSB | |

Things the simulation does not cover:

- THS4531 stability with the 400 pF load. TI's guidance is a 2 pF differential load without an isolation resistor, so 20 Ω and 400 pF needs a measurement. If it rings, raise R16 and R17 from 10 Ω to 20 or 30 Ω.
- Temperature, battery droop and regulator noise.
- Layout coupling and the real ZedBoard supply.

Paper checks:

- The AMS1117-5.0 drops up to 1.3 V and the SS14 about 0.4 V, so the board works down to a battery of about 6.7 V.
- The 5 V rail dissipates under 0.1 W at 9 V.

## Bring-up

With the sensor head: connect it to J1 with the coax, power J2 at 9 V, and the head runs from the 5 V rail (about +5 mA). Measure 2.5 V on the OPA365 output, VREF and C35. Then continue from step 2.

1. Power J2 from a bench supply at 9 V with a 50 mA limit. Check +5V, AVDD (3.30 V), VOCM (1.65 V) and VMID5 (2.50 V) before the PMOD connects.
2. Plug the board into the ZedBoard and check that nWAKE reads high.
3. Feed J1 from the Analog Discovery 2 with a 250 kHz, 100 mV sine. Compare SCOPE OUT with the input on the scope (1 MΩ input).
4. Read SPI codes. Check the idle code and the amplitude against the scope.
5. Sweep 10 kHz to 2 MHz and compare with the table above. The 10 kHz loss is the thinnest margin.
6. Turn the trimmer until nWAKE drops as the amplitude crosses the window. Check the response time.

## Manual (`doc/`)

`doc/ADS7057_test_board_hardware_manual_letter_v0.2.pdf` explains the boards in 54 steps plus the sensor head: the basics, every block, the layout, the order and the bring-up. Two print versions (`_print`, `_print_duplex`) have a 14 mm binding margin.

Rebuild: `M4_PDF_PYTHON=<python with pymupdf> python3 doc/tools/make_adc_manual.py`. The figures read `doc/data/board.json` and `doc/data/sim.json`, made by `doc/tools/export_board.py` (KiCad python) and `doc/tools/export_sim.py`.

Correction: the board uses only 0.2 mm and 0.15 mm tracks, with no separate 0.35 mm power class.

## Files (`hw/`)

- `ADC_Test.kicad_pro/.kicad_sch`: the KiCad 10 project and the schematic of both boards.
- `ADC_Test.kicad_pcb`: main board. `ADC_Head.kicad_pcb`: sensor head. Both are built from the same netlist.
- `ADC_Test_schematic.pdf`: the schematic.
- `fab/ADC_Test_gerbers.zip`, `fab/ADC_Head_gerbers.zip`: Gerbers and drill files.
- `fab/ADC_*_BOM_JLC.csv` and `fab/ADC_*_CPL_JLC.csv`: BOM and pick-and-place for each board.
- `preview/`: renders and the 1:1 print PDFs of both boards.
- DRC: main board 0 errors and 0 unconnected (the parity warnings are the head parts, which are not on this board). Head board 0 unconnected, two courtyard warnings.

## Rebuild

```
python3 hw/tools/design.py hw          # schematic (then export netlist with kicad-cli)
FREEROUTING=/path/to/freerouting hw/tools/route.sh 60   # place, route, finish
BOARD=head FREEROUTING=/path/to/freerouting hw/tools/route.sh 60   # the sensor head
hw/tools/drc.sh; BOARD=head hw/tools/drc.sh
hw/tools/fab.sh && BOARD=adc python3 hw/tools/jlc_files.py && BOARD=head python3 hw/tools/jlc_files.py
```

Freerouting 2.4.1 needs Java 25 (the macOS .dmg bundles it).

## At JLCPCB checkout

- Two orders: upload `ADC_Test_*` and `ADC_Head_*` separately.
- Upload the new CPL, then open Component Placements and check U5, C29, J2 and J3 (see "JLCPCB placement check"). On the head also check U8 pin 1, L1, J6.
- Look at J1, J4 and J6 as well. The SMA model looked offset against its four legs.
- Check pin 1 of U4 (ADS7057) in particular.
