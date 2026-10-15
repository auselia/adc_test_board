# Plan for the ADS7057 test board manual

Status: plan, not built. It follows `Auselia_AFE_v1/doc/manual_method.md`.

## 1. Reader and goal

The reader knows hardware and has used a scope. The reader does not know this board, the ADS7057 or how an acoustic emission front end is built.

After the manual the reader can do four things:

1. Say what every block of the board does and why it is there.
2. Find any part on the board and say which block it belongs to.
3. Read the routing and the layers, and say why they look as they do.
4. Order, assemble and bring up a board without asking anyone.

Name: "ADS7057 test board, hardware manual, version 0.1". The other manuals say "assembly manual". This one covers design and routing too, so "hardware manual" is more accurate.

## 2. Sources (read before writing)

| Source | What it gives |
|---|---|
| `hw/ADC_Test.net`, `.kicad_sch` | Every part, value, net and LCSC number |
| `hw/ADC_Test.kicad_pcb` | Positions, track lengths, widths, vias, layers, pours |
| `hw/fab/*` | BOM, CPL, Gerber and drill files |
| `hw/tools/design.py`, `build_board.py` | The reasons behind placement and values |
| `sim/vendor_results.txt`, `sim/adc_chain.py` | Gain, band, noise, headroom, settling, Monte Carlo |
| ADS7057, THS4531, OPA365, LM393, XC6206, AMS1117 datasheets | Facts and limits |
| `Auselia_AFE_v1/doc/Auselia_AFE_PCB_design_description_v0.1.pdf` | Why the topology and values |
| `Auselia_AFE_v1/sim/data` | The seven recorded AE events (real waveforms for the figures) |
| README, JLCPCB quote and viewer files | Cost, rotations, the fixes |

Every number in a figure comes from a small calculation in the generator or from one of these files, with an `assert`.

## 3. What the reader must understand, in order

1. What the board is for and where it sits (sensor, perfboard, this board, FPGA).
2. What the signal looks like at the input.
3. Why there is a mid-rail (2.5 V and 1.65 V).
4. What the ADC measures and how big one code is.
5. Why the signal is filtered before the ADC.
6. How each stage works and what its numbers are.
7. How the ADC is driven so it settles in time.
8. How the SPI frame works, including the power-up calibration.
9. How the wake-up works and how to set it.
10. How the board is laid out and where each part is.
11. How it is made and what it costs.
12. How to turn it on and check it.

## 4. Structure

| Page | Content | Pages |
|---|---|---|
| Cover | Mark, title, one sentence | 1 |
| Reading guide | Six cards, colors by role | 1 |
| One view | Block diagram of the whole board and the power tree, with a card per section | 1 |
| Part 0 | The basics, steps 0.1 to 0.6, no board details yet | 1 + section page |
| Sections 1 to 8 | One green page and then steps, four per page | about 12 + 8 |
| Notes | Ruled panels at the end of each section | as needed |
| Back cover | Where the files, datasheets and simulations live | 1 |

About 54 steps and about 28 pages in Letter landscape. A short version (steps marked **core**, 36 steps, about 20 pages) is possible.

## 5. The steps

Figure data in brackets.

### Part 0: The basics (0.1 to 0.6)

| Step | Question | Figure |
|---|---|---|
| 0.1 | What is this board for? | Chain: plant, sensor, perfboard, this board, ZedBoard |
| 0.2 | What does the perfboard output look like? | A recorded event on 4.8 V DC, 40 to 120 mV (AE data) |
| 0.3 | Why 2.5 V and 1.65 V? | Voltage ladder 0, 1.65, 2.5, 3.3, 5, 9 V |
| 0.4 | What does the ADC measure? | Differential input and the 14-bit code ladder, LSB 0.40 mV |
| 0.5 | Why filter before sampling? | Spectrum with the fold at 1.2 MSPS |
| 0.6 | How do I read a PCB? | Pad, track, via, pour, silkscreen on the real board |

### Section 1: Power and references (steps 1 to 6)

| Step | Question | Figure (data) |
|---|---|---|
| 1 | How does 9 V become 5 V? **core** | Battery voltage against the 5 V rail, minimum 6.7 V (AMS1117 dropout, SS14) |
| 2 | Why a tantalum on the 5 V regulator? | The datasheet rule: 22 µF solid tantalum, and what the ceramic would do |
| 3 | Where does the ADC reference come from? **core** | AVDD from the XC6206, the 4.7 µF and 100 nF at the pin |
| 4 | How is the 2.5 V mid-rail made? | Divider, buffer, 10 Ω, 10 µF, settle time 5 ms (computed) |
| 5 | How is the 1.65 V made? | AVDD/2 divider, datasheet range AVDD/2 ± 0.1 V |
| 6 | How much current, and where do I probe? | Current per rail (estimate, marked) and test points |

### Section 2: The signal path (steps 7 to 16)

| Step | Question | Figure (data) |
|---|---|---|
| 7 | How does the signal get in? **core** | J1, 50 Ω source, 100 pF coupling |
| 8 | How does the high-pass work? **core** | Sallen-Key with values, f0 = 112 kHz, Q = 0.71 (computed) |
| 9 | Why 112 kHz? | Perfboard noise spectrum against the band |
| 10 | How is the gain set? **core** | 1 + 3.9k/1k = 4.9, bandwidth 10 MHz |
| 11 | How does the low-pass work? **core** | Sallen-Key, f0 = 512 kHz, Q = 0.71 |
| 12 | What is the total response? **core** | Simulated curve against the targets, 10 kHz margin 0.5 dB, Monte Carlo band |
| 13 | What clips first? | Waveforms at 120, 300 and 500 mV; clipping near 0.54 V |
| 14 | What is SCOPE OUT? | 51 Ω, the cable, the 1 MΩ input |
| 15 | What does the OPA2365 do here? | Datasheet facts and which channel is which stage |
| 16 | Where are these parts? | Mini placement map of the block |

### Section 3: Driver and ADC (steps 17 to 24)

| Step | Question | Figure (data) |
|---|---|---|
| 17 | How does one wire become two? **core** | THS4531 gain of 1, VOCM, the 160 Hz coupling |
| 18 | What must I know about the THS4531? | PD pin, VOCM range, the 2 pF load guidance (open risk) |
| 19 | What are the 10 Ω and 400 pF for? **core** | Kickback bucket: 25 × the 16 pF sampling capacitor, pole at 19.9 MHz |
| 20 | What does the ADC input look like? | 50 Ω and 16 pF per leg, settling 30 to 55 ns against 95 ns (simulation) |
| 21 | What is the ADS7057? **core** | Pin map, X2QFN size, key numbers table |
| 22 | How is it decoupled? | AVDD and DVDD capacitors, placement rule |
| 23 | How does a voltage become a code? **core** | Worked example from a simulated event, two's complement |
| 24 | How much noise do we see? | Sensor 40 to 53 LSB, board 0.2 LSB, ADC 0.6 LSB |

### Section 4: The SPI link (steps 25 to 30)

| Step | Question | Figure (data) |
|---|---|---|
| 25 | Which pin is which on the PMOD? **core** | J3 with KiCad and PMOD numbers, nWAKE |
| 26 | Why 22 Ω in each line? | Edge rate at 60 MHz |
| 27 | What does one frame look like? **core** | CS, SCLK, SDO waveform with the 18 clocks |
| 28 | Why is the data one frame late? **core** | Three frames, result of the previous one |
| 29 | What happens at power-up? **core** | 24 SCLKs, offset calibration, zeros on SDO |
| 30 | How fast can I go? | Timing table: 16.66 ns, 7 ns, 8 ns, 15 ns, 10 ns |

### Section 5: The wake-up (steps 31 to 35)

| Step | Question | Figure (data) |
|---|---|---|
| 31 | What is a window comparator? **core** | Two thresholds around 2.5 V |
| 32 | How is the window set? **core** | Divider formula and table, Rp against mV (computed) |
| 33 | Why is nWAKE open-collector? | Wired-OR and the 10k pull-up to 3.3 V |
| 34 | How fast and how accurate? | 1.3 µs, 5 mV offset, noise against the smallest setting |
| 35 | How do I set the trimmer? | Bench procedure with SCOPE OUT |

### Section 6: The board (steps 36 to 44)

| Step | Question | Figure (data) |
|---|---|---|
| 36 | What is the stack and the size? **core** | Two layers, 50 × 32 mm, GND on both, via count (from the board file) |
| 37 | How is the floor planned? **core** | Zones: signal left to right, power bottom left, digital right |
| 38 | Where is every part? **core** | Placement map, every reference designator colored by block |
| 39 | Why is the ADC corner built like this? | Close-up of U4, the four capacitors, the 10 Ω and 22 Ω |
| 40 | How are the analog tracks routed? | Length and width per net (computed from the board) |
| 41 | How are power and ground routed? | Pours, stitching vias, the AMS1117 tab, the DNC pin |
| 42 | What does each label on the silkscreen mean? **core** | The labeled top view |
| 43 | Which footprints are tricky? | X2QFN land pattern, SOT-23 orientation, the viewer fixes |
| 44 | What does it look like? | The three renders with callouts |

### Section 7: Making the board (steps 45 to 48)

| Step | Question | Figure (data) |
|---|---|---|
| 45 | Which files go to the factory? **core** | Gerber zip, BOM, CPL, what each contains |
| 46 | What is in the BOM? | Parts by block with LCSC numbers, basic or extended |
| 47 | What did the placement viewer correct? | Table of the four rotations and the RV1 shift |
| 48 | What does it cost? **core** | Real quote breakdown and the total in USD and CLP |

### Section 8: Bring-up and checks (steps 49 to 54)

| Step | Question | Figure (data) |
|---|---|---|
| 49 | What do I check before I plug in the PMOD? **core** | Expected voltages table |
| 50 | What is the first signal test? **core** | AD2 into J1, what MON and SPI show |
| 51 | What response should I measure? | Sweep table from the simulation |
| 52 | How do I set and test the wake-up? | Procedure and expected waveforms |
| 53 | What if it does not work? | Symptom, likely cause, check |
| 54 | What has been verified and what is open? | The verification table, with sources |

## 6. Figures: how they are made

- The placement map, the track lengths and the via count come from the `.kicad_pcb` file by script. Nobody types them.
- The response curves come from `sim/adc_chain.py` and `sim/vendor_chain.py`.
- The events come from the AFE recordings.
- The filter values come from `design.py` and are checked against the netlist with `assert`.
- Colors follow the method: purple logic, pink control and example data, white with a purple border for registers and pins, blue memory, green bus, amber the item of the step.

## 7. Facts to check before writing

- ADS7057 output coding and the transfer function (datasheet Figure 35).
- XC6206 minimum output capacitance (the text I extracted had no number).
- AMS1117 ESR range (the datasheet gives none).
- THS4531 with 10 Ω and 400 pF: stays "open" until the LTspice netlist is run.
- LM393 response time and offset (datasheet values, not simulated).

Anything not confirmed is marked "ESTIMATE" in the text and in the figure.

## 8. Build and outputs

- Copy `m4lib.py` and its helpers into `doc/tools/` of this repo, then write `adc_part_a.py` to `adc_part_h.py` and `make_adc_manual.py`.
- Outputs: a screen PDF and two print PDFs with a 14 mm binding margin, like the other manuals.
- The build prints the layout warnings and the STE check. Every page is looked at as a PNG.

## 9. Decisions needed

1. Full (54 steps) or short (36 core steps)?
2. English only, or a Spanish version as well?
3. Keep the cost step (48), or leave money out of the manual?
4. Should the manual live in this repo (`doc/`), or in `Auselia_AFE_v1/doc/` with the others?
5. Who reads it first? The advisor, the lab, or someone who will build more boards?
