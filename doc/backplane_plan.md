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

## 4. Architecture A (chosen): FMC adapter + two 8-slot modules
Hardware files: `hw/backplane/` (generator scripts, KiCad boards, JLCPCB files in `hw/backplane/fab/`).

```
ZedBoard FMC LPC ---[ FMC adapter ]--2x 50-pin ribbon--> [ module A: slots 0-7 ]
                    (8 level shifters)                    [ module B: slots 8-15 ]
```

**FMC adapter** (84 x 70 mm, 4 layers, parts on both sides). The FMC mezzanine plug (Samtec ASP-134602-01) sits on the bottom side and mates with the ZedBoard FMC socket. Eight SN74LVC8T245 level shifters translate between the FPGA bank voltage VADJ (A side) and 3.3 V (B side, from the FMC 3P3V pins). This removes the need to solder J18: the ZedBoard default VADJ of 1.8 V would otherwise put 3.3 V pull-ups of the cards onto Zynq pins rated 1.8 V + 0.55 V.
- 58 lines: 18 outputs (16 CS, 2 SCLK) with 47 ohm series resistors, 40 inputs (16 WAKE_N, 16 BIG_N, 8 SDO lanes).
- PRSNT_M2C_L (H2) is grounded and TDI is tied to TDO (D30 to D31), so the ZedBoard keeps its JTAG chain working with the adapter plugged in.
- Two 2 x 25 box headers, one ribbon per module.

**Module** (246 x 72 mm, 4 layers, all SMD on top). Eight vertical 2 x 6 sockets at 25.4 mm pitch, a SN74LVC244A SCLK buffer with 22 ohm per branch, a TPS7A8300 low-noise LDO (5 V to 3.3 V, ANY-OUT pins 100 mV + 800 mV + 1.6 V to GND), 100 k pull-ups on CS, WAKE_N and BIG_N so an empty slot reads "idle", and a 5 V screw terminal. Inner layers: GND and 3.3 V planes.

**Ribbon cable (same on both ends, conductor n = pin n):** GND next to SCLK and to every SDO lane, GND after every 2 to 4 of the CS, WAKE_N and BIG_N lines. 29 signals and 21 grounds. See `hw/backplane/ribbon.py`.

**Socket wiring.** The card stands perpendicular to the backplane, so the two rows of its right-angle header swap on the socket: card pin 1 (CS) lands on socket pad 2, pin 2 (BIG_N) on pad 1, pin 5 (SDO) on pad 6, pin 7 (SCLK) on pad 8, pin 8 (WAKE_N) on pad 7, pins 9 and 10 (GND) stay, pins 11 and 12 (3V3) stay. The card must be inserted with its component side facing +X (arrow on the silkscreen). A card inserted the other way round gets no GND and no 3.3 V and stays dead (no damage expected: the logic pins only see the 22 ohm resistors).

Signals (58 of 68 LA pins). West group (FMC rows C and D, 24 pads) carries module A CS, WAKE_N and BIG_N; east group (rows G and H) carries module B CS, WAKE_N, BIG_N, all 8 SDO lanes and both SCLK. Exact FMC pad of every signal: `hw/backplane/out/FMC_Adapter_model.json` and the generated schematic.

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

## 6. Backplane electrical design (as built in `hw/backplane/`)
- **Layers:** 4 on both boards. Module: F.Cu and B.Cu signals, In1 GND plane, In2 +3V3 plane. Adapter: In1 GND plane, In2 free for signals (BGA-style fan-out of the FMC plug).
- **Sockets:** pitch 25.4 mm so the SMA cables of the cards have room. Two modules of 8 slots (246 x 72 mm each) instead of one 365 mm board.
- **SCLK:** FPGA, 47 ohm, ribbon, SN74LVC244A (one gate per slot), 22 ohm per slot, socket, card (22 ohm more). Series termination at the driver, high-impedance load at the card.
- **SDO lanes:** two cards per lane. Hi-Z while CS is high. 100 k pull-down on the adapter side.
- **Power:** 5 V screw terminal, SS14 reverse protection, TPS7A8300 at 3.3 V (dropout is 1.7 V minus the diode, power about 0.4 W at 8 x 32 mA). 8 x (10 uF + 100 nF) at the sockets. Ground is one solid plane; keep each head's coax shield grounded only at the card.
- **Hot-plug:** none. Power the module down before changing a card.
- **Level shifting:** the adapter, not the ZedBoard jumper, handles VADJ. Use any of 1.8, 2.5 or 3.3 V. The 3.3 V of the adapter comes from the FMC 3P3V pins (3 A shared with the board; the adapter takes a few mA).

## 7. FPGA design (outline)
- RTL parameters: number of lanes, cards per lane.
- A scheduler: reads the WAKE_N inputs, queues events, serves one card per lane at a time, writes samples tagged with channel and time through DMA.
- Continuous mode is the same scheduler with a fixed card list.
- Reuse the SPI rules: 18 clocks per frame, and the first frame after power-up is 24 clocks (offset calibration).
- **Round-trip delay.** Each level shifter adds about 5 ns, the ribbon and the backplane trace about 3 to 4 ns each way, the SCLK buffer 4 ns and the ADS7057 SDO delay about 14 ns. The SDO data arrives about 35 ns after the SCLK edge that launched it. At 20 MHz (50 ns period) sample SDO one clock later than a plain SPI master would (use an IDELAY or a phase-shifted capture clock). Start at 10 MHz and raise it.
- Use the FMC pin names of the ZedBoard master XDC (`FMC-LAxx_P/N`). The LA name of every signal is in `hw/backplane/out/FMC_Adapter_model.json` and in the adapter schematic.

## 8. Open items and risks
1. **JLCPCB placement of the FMC plug.** ASP-134602-01 (C2875619) is a 400-ball BGA-style connector. The footprint keeps only the used balls (columns A, C, D, G, H, K), the others are left off the pads on purpose so every used ball has a via next to it. Check the part in the JLCPCB placement viewer (bottom side, rotation) before paying, and ask support if they accept it.
2. **CPL rotations** of the TSSOP, QFN, IDC headers and terminal block follow the community table and are not verified. Check each one in the viewer. A 180 degree turn of an IDC box header reverses the cable.
3. **Mechanics:** no card guide or retention yet. A 125 mm card held only by a 2 x 6 socket is a lever. Add a rail at the SMA end. The adapter hangs on the FMC plug and the two ribbon cables pull on it: use a standoff or a cable tie.
4. **ZedBoard FMC rail and JTAG:** check that JTAG still sees the Zynq with the adapter plugged in (TDI tied to TDO, PRSNT grounded).
5. **SCLK integrity** over the module (about 200 mm): look at SCLK at the last slot with a scope on the first module.
6. **Card orientation:** a card inserted with its components facing the wrong way is dead but undamaged. Add a keyed card guide.
7. The ZedBoard 3.3 V rail noise is not measured. The module LDO makes it less important for the cards.
8. Not run: ERC of the generated schematics beyond pin types, a SPICE check of the SCLK line, and a JLCPCB quote (the cost below is an estimate).

## 9. Next steps
1. Check the CPL and BOM in the JLCPCB viewer (items 1 and 2 above), then order the adapter and the modules, or hand-solder the headers.
2. RTL plan for the scheduler and the two modes.
3. Bench: one module with two cards, then 16.
