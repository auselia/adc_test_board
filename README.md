# ADS7057 test board (low-power 3.3 V version, v3)

The middle step between the perfboard and the AFE PCB. It takes the signal from the sensor, filters it, digitizes it with the ADS7057, and gives the SPI bus and two listener lines to a ZedBoard PMOD port. **It is powered only from the PMOD 3.3 V. There is no USB and no regulator.**

The 5 V / USB-C revision is kept in the git tag `v2-usb-5v`.

There are **two boards**, ordered separately:

| Board | What it is | Size |
|---|---|---|
| ADC test board (`ADC_Test`) | HPF, gain, LPF, driver, ADS7057, listener (WAKE_N, BIG_N), PMOD, bias-T for the head, current-measurement links, test points | **125 × 21.5 mm** |
| Sensor head (`ADC_Head`) | The perfboard charge amplifier on a PCB. The piezo wires solder to it. It is powered through the coax | 10 × 22 mm |

The head connects to **SENSOR IN (J1)** with one coax cable. The coax carries 3.3 V to the head (a bias-T) and the signal back. To use a function generator instead of the head, cut JP1.

The board is a narrow strip (21.5 mm) so that boards fit on adjacent PMOD ports (pitch about 22.7 mm). It is **always on**: the whole chain and the listener run all the time, and the listener only observes.

## What changed from v2 (5 V, USB-C)

| | v2 | v3 |
|---|---|---|
| Supply | USB-C or header, 5 V, SS14, ferrite, XC6206 for AVDD | **PMOD 3.3 V only**, through the 5-pin header J7 (jumper 1-2). AVDD through 10 Ω and 10 µF |
| Rails | 5 V, 2.3 V VMID5, 1.65 V VOCM | 3.3 V, **1.65 V** VMID5 and VOCM |
| Wake-up | LM393 window, trimmer RV1, nWAKE | **Listener**: passive 159 kHz high-pass, 723 kHz low-pass, two TLV7022 comparators. WAKE_N (35 mV) and BIG_N (111 mV) at SIG_IN, on PMOD pins 10 and 7. Observer only |
| Current measurement | none | J7: 4-wire source-measure unit connection (below). JP3 (capture rail) can be opened to measure or switch the chain alone |
| Test points | TP3 to TP20 on a bottom strip | TP3 to TP20 inside each block, names on the back |
| Size | 57 × 37.6 mm | 125 × 21.5 mm |
| Head | OPA365, 5 V from the coax | OPA365 at 3.3 V (V+ 2.9 V). Low-power option: OPA314 and Cf 220 pF on the same pads |

## Uses

The board serves two purposes. In the plant experiments, four boards sit on ZedBoard PMODs JA to JD: two control plants, one drying plant and one reference sensor. Each board is one channel. The listener lines tell the FPGA, next to the full waveform, how often a burst crosses a small or a large threshold. That data decides whether the battery product can run on a listener alone.

## Circuit

| Block | Parts | Values |
|---|---|---|
| High-pass filter | Sallen-Key, U1A | 100 pF C0G ×2, 10k, 20k: f0 = 113 kHz, Q = 0.71 |
| Gain | U1B | 1 + 3.9k/1k = 4.9 |
| Low-pass filter | Sallen-Key, U2A | 2.2k ×2, C1 = 2 × 100 pF, C2 = 100 pF: f0 = 512 kHz, Q = 0.71 |
| VMID5 (signal ground, half of +3V3_C, 1.65 V) | 10k/10k divider, U2B buffer | 10 Ω, 10 µF |
| Driver | THS4531, gain 1 | 1k in and feedback; VOCM = 1k/1k divider on AVDD |
| ADC input filter | | 10 Ω per leg, 4 × 100 pF C0G = 400 pF |
| AVDD (reference) | from +3V3_C through R34 10 Ω, C21 10 µF | 4.7 µF + 100 nF at the ADS7057 AVDD pin. RC corner 1.6 kHz |
| 3.3 V input | PMOD J3 pins 6 and 12 to J7 pin 1; J7 pins 2 and 3 are the board rail | C23 10 µF. No USB, no diode |
| Rail link | JP3 joins +3V3_C (U1, U2, U3, AVDD) to +3V3 (closed). The listener and DVDD are on +3V3 | Open JP3 to measure or switch the capture chain alone |
| MON output | 51 Ω from LPF_OUT to SMA J4 | The scope sees the same signal the ADC samples |
| Bias-T on SENSOR IN (J1) | JP1 (bridged), R26 47R + C32 10 µF, L2 470 µH, C33 100 nF, R27 1M | 3.3 V reaches the coax centre through 47 Ω and 470 µH. C33 passes the head signal to the filters |
| Listener filter | C40 100 pF + R35 10k (high-pass 159 kHz), R36 10k + C41 22 pF (low-pass 723 kHz) | Output LST, TP15. Gain 0.68 at 250 kHz (the filters load each other) |
| Listener thresholds | R21 1M, R22 33k, R39 15k, R40 15k, R41 33k, R23 1M from +3V3_L to ground; REFL = 1.65 V | WAKE_N ±24 mV and BIG_N ±76 mV at LST, which is 35 mV and 111 mV at SIG_IN (1.6 pC and 5.2 pC at Cf 47 pF) |
| Listener comparators | U6 (WAKE_N), U9 (BIG_N), TLV7022, 5 µA per channel, 260 ns | Open drain, 47k pull-ups R24 and R42 to 3.3 V |

Main board: 125 × 21.5 mm, 2 layers, all SMD parts on top, GND pour on both layers, 786 + 100 tracks.

### Sensor head

The perfboard circuit (TRL3 schematic), on its own board:

| Block | Parts | Values |
|---|---|---|
| Charge amplifier | U8 OPA365 (SOT-23-5) | 50 MHz, about 4.6 mA. Low-power option: OPA314 (3 MHz, 150 µA) with Cf 220 pF |
| Feedback | R28 1 MΩ, C34 47 pF C0G | Corner 3.4 kHz, gain 1/Cf |
| Reference | R29, R30 1M, C35 10 µF | VREF = V+/2, about 1.45 V |
| Output | R31 49.9 Ω, C38 100 nF | 50 Ω, AC-coupled onto the coax |
| Power from the coax | L1 470 µH, C36 100 nF, C37 10 µF | 3.3 V comes in on the coax centre. About 4.3 mA, V+ = 2.9 V |
| Piezo | TP1 (+, to the summing node), TP2 (−, to ground) | Two 1 mm holes. TP1 is on the centre line of the board and sets the piezo position |
| Output connector | J6 SMA, vertical | To SENSOR IN (J1) on the main board |

The bias-T at 3.3 V costs 0.17 dB at 250 kHz and 19 dB at 10 kHz (`python3 sim/head_bias_t.py 3.3`). The board is 22 mm long, not the 20 mm of the capsule drawing v3.

**Two head amplifiers.** The OPA365 is the lab default: it keeps the waveform faithful (noise gain 35 gives 1.4 MHz bandwidth) but draws 4.6 mA. The OPA314 draws 150 µA and fits the battery goal, but its 3 MHz gain-bandwidth needs Cf 220 pF (−3 dB near 360 kHz) and it has 14 nV/√Hz of noise against 4.5. Both are SOT-23-5 with the same pinout. Swap the amplifier and Cf.

## Silkscreen

| Label | What it is |
|---|---|
| SENSOR IN (J1) | SMA input for the sensor head. The centre pin carries 3.3 V while the jumper JP1 is bridged. Cut JP1 before you connect a function generator. |
| SCOPE OUT (J4) | SMA monitor output. It carries the same signal the ADC samples, through 51 Ω. Use a 1 MΩ scope input. A 50 Ω input halves the signal. |
| Test point names (back) | SIG_IN, HPF_OUT, GAIN_OUT, LPF_OUT, DRV_OUTP, DRV_OUTN, AINP, AINM, +3V3, AVDD, VMID5, VOCM, LST, WAKE_N, BIG_N, REFL, GND, GND |
| Silkscreen (top) | Test point numbers (TP3 to TP20) and IC numbers (U1 to U4, U6, U9); head: TP1, TP2, U8. Jumper names and PMOD pin legend on the back |
| PMOD pin list (back) | Pins used and their names |
| Leaf and waves (back) | Auselia mark |

Reference designators (R1, C4 and so on) are on the F.Fab layer, not on the silkscreen. Open the KiCad file to see them.

## Power

All power comes from the ZedBoard PMOD. J3 pins 6 and 12 carry 3.3 V and pins 5 and 11 carry GND. The ZedBoard feeds the PMOD connectors from its 3.3 V rail, rated 3 A and shared with the FMC and the other PMODs. This board draws about 27 mA, plus 5 mA for the head, so four boards are about 130 mA. Feed J7 instead (and cut JP6) to run on the bench.

J7 is a 5-pin header: 1 Onboard + (PMOD 3.3 V), 2 Force +, 3 Sense +, 4 Sense −, 5 Force −. Pins 2 and 3 are the board rail, pins 4 and 5 are ground. A jumper from pin 1 to pin 2 powers the board from the ZedBoard. To power it from a source-measure unit (for example a Keysight B2901BL) remove the jumper and connect Force to pins 2 and 5 and Sense to pins 3 and 4. The SMU then measures the total board current. JP3 (closed) joins the capture rail: open it to feed or switch U1, U2, U3 and AVDD separately. JP1 is the head power link.

AVDD is the ADC reference, and full scale is ±AVDD. It comes from the rail through 10 Ω and 10 µF. The ZedBoard 3.3 V noise is not known yet: probe TP11 and TP12.

The long-term product runs from a battery for a year. This board is the lab version. The listener (about 25 µA) and the OPA314 head (150 µA) are the building blocks for that, and the plan is in `doc/lowpower_plan.md`.

## Through-hole parts

JLCPCB solders these. They are in the BOM and the pick-and-place file.

| Ref | Part | LCSC |
|---|---|---|
| J1, J4 (and J6 on the head) | SMA jack, vertical, 5 pins (sensor in, MON, head out) | C496549 |
| J7 | 1×5 pin header, 2.54 mm (power / source-measure unit) | C492404 |
| J3 | 2×6 right-angle pin header, 2.54 mm | C60565 |

If JLCPCB declines a through-hole part, delete its line from the BOM and solder it yourself. The board has the same footprints either way.

## Connectors

- **J1 SENSOR IN:** SMA for the sensor head, carries +3.3 V on the centre pin (JP1 bridged).
- **J4 SCOPE OUT:** SMA monitor output, LPF_OUT through 51 Ω.
- **J7 header:** power and 4-wire SMU connection (jumper 1-2 for the PMOD supply).
- **H1, H2:** M3 mounting holes.
- **J3 PMOD:** 1 CS, 3 SDO, 4 SCLK, 5/11 GND, 6/12 3V3, 7 BIG_N, 10 WAKE_N.

All device ports are SMA female. Use one cable type everywhere (SMA male to male, RG316 or RG174, short): head to SENSOR IN, SENSOR IN to a generator, SCOPE OUT to the oscilloscope through an SMA male to BNC female adapter. The RP-SMA parts in some shops do not mate with these jacks. Connect the head to the oscilloscope only through the board, since the bias-T that powers the head is on the board.

Before you plug the board into JA–JD, check that pins 5/6 and 11/12 line up with GND/VCC on the ZedBoard silkscreen. Adjacent ports are about 22.7 mm apart and the board is 21.5 mm wide.

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
| ADC board × 2 | $66.84 | $32.20 | $30.64 |
| ADC board × 3 | $83.83 | $48.30 | $31.54 |
| ADC board × 5 | $117.82 | $80.50 | $33.33 |
| Sensor head × 5 | $40.77 | $15.65 | $21.12 |
| Sensor head × 10 | $57.94 | $31.29 | $22.65 |

Both orders together, with shipping (Global Standard $10.75 per parcel) and 19 % IVA:

| | One parcel | Two parcels |
|---|---|---|
| 2 ADC boards + 5 heads | $140.84 | $153.64 |
| 2 ADC boards + 10 heads | $161.46 | $174.26 |

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

> The model is calibrated on the first quote. A real quote of this revision (2026-10-15, 5 ADC boards, 5 heads, one checkout) showed merchandise $159.73 and shipping $52.45 because the cart was above $150. Split it in two orders (Global Standard $10.75 each) to stay below that line.

## JLCPCB placement check

The JLCPCB viewer showed four problems on the first revision, and the CPL corrects them. **New parts are not checked yet:** U6 and U9 (TLV7022, SOT-23-8), U8 (SOT-23-5, head), L1 and L2 (1210 inductors), J6 (SMA). Look at them in the viewer.

| Part | Problem | CPL rotation |
|---|---|---|
| J7 (1×5 header) | Rotation as in the CPL (90), not checked in the viewer | check |
| J3 (2×6 header) | Row horizontal, pads vertical | 0 → 90 |

J3 and J7 have their origin on pin 1 in the KiCad footprint, so they are placed by that pin.

## Verification

| Check | Status | Result |
|---|---|---|
| ERC, DRC, schematic-to-board parity | Done | 0 errors, 0 unconnected, 0 mismatches |
| Pinouts and polarity against the datasheets | Done | All ICs, SS14 |
| JLCPCB placement viewer | **Open** for U6, U9, U8, L1, L2, J6 | 2 rotations fixed. Check again after the new CPL |
| DC bias, AC response, noise | Done | Table below |
| Tolerance Monte Carlo, 150 runs | Done | 10 kHz loss under 40 dB in 11 of 150 runs |
| 250 kHz burst, headroom at 3.3 V | Done | A 120 mV event reaches 16 % of full scale. Clipping starts near 0.37 V (`doc/data/sim.json`) |
| As-built netlist, rails to listener | Done | `python3 sim/netlist_verify.py`: 18 DC checks, gains and bursts all pass. It found that the first listener filter passed only 0.45 of the signal, which was fixed (R36, C41, R39, R40) |
| Listener on 25 real captures | Done | 7 of 7 events above WAKE_N, none of the 18 noise captures (peak 26 mV against 35 mV). Rate of false alarms per hour is open (`sim/g1_listener.py`) |
| ADC input settling | Done | 30 to 55 ns against 95 ns minimum |
| Cable on the SCOPE OUT SMA | Done | No peaking up to 5 nF |
| THS4531 into 10 Ω and 400 pF | **Open** | TI's model fails in ngspice and LTspice batch mode does not run here. `sim/ths4531_stability_estimate.py` gives 48 to 77° of margin for assumed output impedances. Run `sim/ltspice/ths4531_cap_load.cir` in LTspice |
| Head and bias-T, ngspice with the OPA365 model | Done | 0.17 dB loss at 250 kHz, 19 dB at 10 kHz, about 4.3 mA at 3.3 V. `python3 sim/head_bias_t.py 3.3` |
| ZedBoard 3.3 V rail noise | **Open** | Probe TP11 and TP12 with the board plugged in |
| Adjacent PMOD ports (22.7 mm) | **Open** | Print 1:1 and test |
| Head board, DRC | Done | 0 unconnected, no electrical errors. Two courtyard overlaps (TP/L1 and C34/R28) |
| Head: piezo wires, strain relief, RTV | Open | Mechanical, on the bench |
| Print the PCB 1:1 and test-fit parts | Open | |
| Fit on the ZedBoard PMOD | Open | |
| Bench bring-up | Open | See below |

`sim/vendor_chain.py` runs the checks and `sim/vendor_results.txt` holds the output. The OPA365 is TI's own model. The THS4531 is a datasheet-based model (27 MHz, 2.5 Ω), because TI's model gives a −3 dB point at 17 kHz in ngspice. The ADC input is the datasheet model: 50 Ω and 16 pF per leg. Run `python3 sim/models/fetch_models.py` to download the TI models, which are not stored in the repo.

| Result | Value | Target |
|---|---|---|
| DC points | VMID5 1.65 V, VOCM 1.65 V, ADC inputs 1.65 V | |
| Gain at 250 kHz, SMA to ADC | 12.2 dB (×4.1) | |
| Flatness 230 to 280 kHz | 0.08 dB | < 1 dB |
| Loss at 10 kHz, re 250 kHz | 40.5 dB, worst of 150 runs 39.7 dB | ≥ 40 dB |
| Loss at 2 MHz | 24.0 dB | ≥ 20 dB |
| −3 dB band | 106 to 502 kHz | |
| Board noise at the ADC | 77 µV rms, 0.2 LSB | |

Things the simulation does not cover:

- THS4531 stability with the 400 pF load. TI's guidance is a 2 pF differential load without an isolation resistor, so 20 Ω and 400 pF needs a measurement. If it rings, raise R16 and R17 from 10 Ω to 20 or 30 Ω.
- Temperature and the noise of a real power bank.
- Layout coupling and the real ZedBoard supply.

Paper checks:

- The chain was simulated at 3.3 V (`sim/vendor_chain.py`, `sim/g1_chain33.py`).
- The board draws about 27 mA plus 5 mA for the head, about 0.1 W.

## Bring-up

With the sensor head: connect it to J1 with the coax, power the board from the PMOD (or J7 at 3.3 V), and the head runs from the rail (about +4.3 mA). Measure about 2.9 V on C37 and 1.45 V on the OPA365 output, VREF and C35. Then continue from step 3.

1. Remove the J7 jumper and feed pins 2 and 5 with 3.3 V and a 100 mA limit (SMU Force), Sense on pins 3 and 4. Check +3V3 (3.30 V), AVDD (3.30 V), VOCM (1.65 V), VMID5 (1.65 V) and REFL (1.65 V) at the test points before the PMOD connects. Then fit the jumper 1-2 and connect the PMOD.
2. Plug the board into the ZedBoard and check that WAKE_N and BIG_N read high (3.3 V).
3. Feed J1 from the Analog Discovery 2 with a 250 kHz, 100 mV sine. Compare SCOPE OUT with the input on the scope (1 MΩ input).
4. Read SPI codes. Check the idle code and the amplitude against the scope.
5. Sweep 10 kHz to 2 MHz and compare with the table above. The 10 kHz loss is the thinnest margin.
6. Raise a 250 kHz burst from 10 mV: WAKE_N must drop near 35 mV and BIG_N near 111 mV at J1 (±12 mV from the comparator offset). Log TP15 to TP18 on the scope.
7. With the SMU on J7, read the total current (about 25 mA). Open JP3 to read the capture chain and the listener separately.

## Manual (`doc/`)

`doc/ADS7057_test_board_hardware_manual_letter_v0.3.pdf` explains the boards in 54 steps plus the sensor head: the basics, every block, the layout, the order and the bring-up. Two print versions (`_print`, `_print_duplex`) have a 14 mm binding margin.

Rebuild: `M4_PDF_PYTHON=<python with pymupdf> python3 doc/tools/make_adc_manual.py`. The figures read `doc/data/board.json` and `doc/data/sim.json`, made by `doc/tools/export_board.py` (KiCad python) and `doc/tools/export_sim.py`.

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
NOPLANE=1 FREEROUTING=/path/to/freerouting hw/tools/route.sh 60   # place (layout_v3.py), route, finish
BOARD=head FREEROUTING=/path/to/freerouting hw/tools/route.sh 60   # the sensor head
hw/tools/drc.sh; BOARD=head hw/tools/drc.sh
hw/tools/fab.sh && BOARD=adc python3 hw/tools/jlc_files.py && BOARD=head python3 hw/tools/jlc_files.py
```

Freerouting 2.4.1 needs Java 25 (the macOS .dmg bundles it).

## At JLCPCB checkout

- Two orders: upload `ADC_Test_*` and `ADC_Head_*` separately.
- Upload the new CPL, then open Component Placements and check U6, U9 (pin 1), J7 and J3 (see "JLCPCB placement check"). On the head also check U8 pin 1, L1, J6.
- Look at J1, J4 and J6 as well. The SMA model looked offset against its four legs.
- Check pin 1 of U4 (ADS7057) in particular.
