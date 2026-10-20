# Backplane plan: 16 channels with channel cards

Written 2026-10-20. Goal: scale the ADS7057 channel board from the 5 PMOD ports of the ZedBoard to **16 channels**, keep the ZedBoard, and keep today's 125 x 21.5 mm card as a plug-in module.

## 1. Requirements (from the user)
- About 16 channels (15 plants today). More later is welcome, but 16 is the target.
- The channels do **not** need to sample at the same instant. Plants emit at different times.
- Two modes:
  - **Continuous mode.** A small number of plants sample all the time.
  - **Wake mode.** All 16 chains stay on. The listener (WAKE_N, BIG_N) says which plant has an event. The FPGA then reads that channel.
- A backplane with one plug-in slot per channel card.

## 2. Facts checked in the datasheets
| Fact | Source |
|---|---|
| The ZedBoard has **five** Pmod ports: four on the PL (bank 13, 3.3 V) and JE on the PS side (MIO). | ZedBoard HW UG v2.2, section 2.9.2 |
| The LPC FMC exposes **68 single-ended I/O** (34 differential pairs) in PL banks 34 and 35. LA0 to LA16 are in one bank, LA17 to LA33 in the other. | UG section 2.9.1 |
| FMC I/O voltage is **Vadj**, set by jumper J18: 1.8 V default, 2.5 V, and 3.3 V only if you solder a short or a header on the 3V3 pads. | UG section 2.9.1 |
| The 3.3 V "Vcco/FMC/Pmod" rail is rated 3 A and is shared. | UG table 19 |
| **ADS7057: SDO is tri-stated when CS is high.** Tri-state after CS rising: 5.5 ns. Enable after CS falling: 6.5 ns max. | ADS7057 datasheet, section 8.4 and the timing table |
| ADS7057 DVDD range is 1.65 to 3.6 V, independent of AVDD. | ADS7057 datasheet, features |

The tri-state SDO means several cards can **share one SDO line** and the FPGA picks the card with its CS line. The chip-select timing gives about 16 ns of margin at 60 MHz if the FPGA leaves one SCLK period between one card's CS rising and the next card's CS falling.

## 3. Key finding: the current card plugs into the backplane as it is
The card's right-angle 2 x 6 header (J3) points out of the short end of the card, parallel to the card. If the backplane carries **vertical 2 x 6 female sockets**, each card stands perpendicular to the backplane and plugs in with **no change to the card**. The backplane only wires each socket to the right FPGA lines.

| Card pin (PMOD number) | Signal | Backplane wiring |
|---|---|---|
| 1 | CS | the card's own CS line |
| 3 | SDO | the shared SDO lane of the card |
| 4 | SCLK | buffered SCLK, one buffered branch per slot |
| 7 | BIG_N | the card's own BIG_N line |
| 10 | WAKE_N | the card's own WAKE_N line |
| 5, 11 | GND | ground |
| 6, 12 | 3V3 | backplane 3.3 V (not the ZedBoard rail) |
| 2, 8, 9 | not used | free for a slot ID later |

Mechanical note: a 125 mm card held only by the header is a lever. Add card guides or a front rail at the SMA end.

## 4. Architecture A (recommended): FMC, lanes, one CS per card
The backplane plugs into the FMC LPC connector. Needs J18 set to 3.3 V so the FPGA pins match the 3.3 V cards.

Signals (57 of 68 pins with 8 lanes):
- SCLK: 1
- CS: 16 (one per card)
- SDO lanes: 8 (two cards per lane). A 4-lane version uses 4 (four cards per lane).
- WAKE_N: 16, BIG_N: 16 (one per card)

Suggested FMC assignment (outputs in one bank, inputs in the other):

| FMC group | Signals | Pins used |
|---|---|---|
| LA0 to LA16 (bank A, 34 pins) | SCLK (on the clock-capable LA0_P), CS0 to CS15, SDO lane 0 to 7 | 25, 9 spare |
| LA17 to LA33 (bank B, 34 pins) | WAKE_N0 to WAKE_N15, BIG_N0 to BIG_N15 | 32, 2 spare |

The exact FPGA pin for each LA signal comes from the ZedBoard master UCF (not in this repo).

Lane layout: cards (0,1) on lane 0, (2,3) on lane 1, and so on. Put plants that may emit together on different lanes.

### How the two modes work
1. **Continuous mode:** up to 8 channels, one per lane, each at the full rate in parallel. One lane at 25 MHz SCLK gives about 1.2 MSPS. At 60 MHz it gives up to 2.5 MSPS.
2. **Wake mode, all 16:** the FPGA watches the 16 WAKE_N inputs. When one falls, it drops that card's CS and reads about 100 to 200 us (120 to 240 samples).
   - Latency: comparator 260 ns, plus a few FPGA clocks, so under 1 us. A burst lasts 26 to 83 us, so only the first sample or two is missed.
   - If two cards on one lane fire together, the FPGA alternates them and each gets half the rate (600 kSPS, Nyquist 300 kHz, which is marginal for 275 kHz events). Rare, but it is the reason to spread likely plants across lanes.

Data rate: 8 channels at 1.2 MSPS x 2 bytes is about 19 MB/s. No problem for the PL and DDR.

## 5. Architecture B (fallback): PMOD only, address and serial flags
If the FMC mezzanine connector is hard to source, use two PMOD ports (16 I/O) and put a little logic on the backplane.

| Lines | Count |
|---|---|
| SCLK | 1 |
| CS strobe + 4 address bits into a 4-to-16 decoder (two LVC138 or one 154) | 5 |
| SDO lanes (4 lanes of 4 cards) | 4 |
| Flags: a 32-bit shift register chain (CLK, LOAD, DATA) | 3 |
| ANY_WAKE (wired-OR of the 16 WAKE_N) | 1 |
| Total | 14 |

Trade-off: the FPGA first sees ANY_WAKE, then clocks out 32 flag bits (about 2 us at 20 MHz), then sets the address. About 3 to 4 us of the event start is missed instead of about 1 us. The PMOD route avoids the J18 solder and the FMC connector, and a short 2 x 6 ribbon cable replaces a hard-to-find extension cable. It scales by adding decoders and shift registers.

## 6. Backplane electrical design
- **Layers:** 4 layers. 16 slots x (CS, WAKE_N, BIG_N) plus 8 SDO lanes plus 16 SCLK branches is about 72 traces along the board.
- **Length:** 16 slots at 22.7 mm pitch is about 365 mm. Put the FMC connector in the middle so no trace is longer than about 185 mm. Or build two 8-slot boards and join them with a short cable.
- **SCLK:** one branch per slot from a fan-out buffer (octal LVC-type), 22 ohm in series at the source. The ADS7057 SCLK input is a light load.
- **SDO lanes:** two cards per lane, so a simple point-to-point line with a 22 ohm series resistor at the FPGA.
- **Power:** 5 V in from a bench or wall supply. A low-noise 3.3 V regulator (for example, two 500 mA ultra-low-noise LDOs, one per 8 slots) removes the unknown noise of the ZedBoard 3.3 V rail. The load is 16 x about 32 mA = 0.5 A. Add 10 uF and 100 nF per slot at the socket.
- **Ground:** one solid plane with a star point at the regulator. Plants that share a tray or soil can make ground loops. Keep each head's coax shield grounded only at the card.
- **Hot-plug:** the cards have no hot-plug protection. Power down the backplane when you change cards.

## 7. FPGA design (outline)
- RTL parameters: number of lanes, cards per lane.
- A scheduler: reads the WAKE_N inputs, queues events, serves one card per lane at a time, writes samples tagged with channel and time through DMA.
- Continuous mode is the same scheduler with a fixed card list.
- Reuse the SPI rules: 18 clocks per frame, and the first frame after power-up is 24 clocks (offset calibration).

## 8. Open items and risks
1. **J18 on the ZedBoard** must be set to 3.3 V (solder). The UG warns about damage from a wrong setting, so set it before any card is attached.
2. **FMC connector sourcing** in Chile (a Samtec ASP-134604-01 class mezzanine connector). If it fails, use Architecture B.
3. **SCLK signal integrity** over 185 mm at 25 MHz. Check with a scope on the first board.
4. **Card retention:** design the card guides or the front rail before the layout.
5. **Slot ID:** optional, on the unused PMOD pins 2, 8 and 9.
6. The ZedBoard 3.3 V rail noise is still unmeasured. The backplane regulator makes it less important.

## 9. Next steps
1. Choose A or B (the user decides after the connector check).
2. Draw the schematic of one slot and the FMC pin table in the KiCad generator (`hw/tools`), then the layout.
3. Quote the backplane at JLCPCB (size, 4 layers).
4. RTL plan for the scheduler and the two modes.
5. Bench: two cards on one lane, then 16.
