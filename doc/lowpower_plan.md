# Low-power 3.3 V revision (v3): plan

Status: plan. Nothing is built. Date: 2026-10-15.
Authors' note: numbers marked ESTIMATE or "verify" are not from a datasheet I read in full. The part data comes from the JLCPCB library listing and from my memory of the TI families.

## 1. What this revision is for

The product must run on a battery for one year. Today's board draws about 27 mA plus 5 mA for the head from 5 V. A year at that load needs about 280 Ah. A 3 Ah battery allows an average of about 340 µA for everything, including the RISC-V and LoRa.

This revision does three things:

1. It runs from **3.3 V only**, taken from the ZedBoard PMOD pins. No USB, no 5 V, no regulator in the signal path.
2. It splits the board into an **always-on listener** and a **switchable capture chain**.
3. It lets you **measure** what the plant really does (events per hour, amplitude, noise) and what each block really draws. That decides the product architecture.

It is a learning board, not the product. The default mode keeps everything on, as today.

## 2. Findings that shape the design

| # | Finding | Consequence |
|---|---|---|
| F1 | An AE burst lasts 26 to 83 µs. A capture chain that turns on after the wake-up needs milliseconds to settle. It cannot see the event that woke it. | The board must offer two modes. LAB: the whole chain stays on and captures waveforms. LISTEN: the listener extracts features (hit, amplitude class, count) and the chain wakes for what follows. Pre-trigger capture needs a running ADC and is not possible at 165 µA. |
| F2 | The real data (`cavitation_logger/data`, 25 captures from 15:56 to 19:09 on 2026-09-21, trigger 70 mV) has **7 true events** and **18 noise triggers**. The true events have a 100 to 500 kHz peak of 39 to 237 mV (1.8 to 11 pC). The noise triggers peak at 7 to 13 mV in band. They fired on low-frequency noise of 5 to 15 mV rms (`sim/listener_first_look.py`). | A 100 kHz high-pass removes the false triggers. Seven true events in 3 h is about 2 per hour. At 100 ms of 32 mA per event, that is about 0.02 µA average. The listener decides the year. |
| F3 | The LM393 input range ends at VCC − 1.5 V. It cannot work at 3.3 V near the mid-rail. | Replace it with a rail-to-rail comparator (TLV7021 or TLV7022, 5 µA each, 260 ns, open-drain). |
| F4 | The ADS7057 limits digital inputs to DVDD + 0.3 V and every pin to 10 mA. If the FPGA drives SPI while the ADC is unpowered, the 22 Ω resistors pass 150 mA. | Gate AVDD and the analog rail only. Keep DVDD on. Never gate DVDD while the FPGA can drive SPI. |
| F5 | In the 100 to 500 kHz band the perfboard noise is 1.3 mV rms median (0.06 pC) and 3.2 mV rms worst (0.15 pC) in the 25 captures. Below 100 kHz it is 5 to 15 mV rms (0.2 to 0.7 pC). The true events are 1.8 to 11 pC. | Set thresholds in charge, not in volts. A passive 100 kHz high-pass in front of the comparators removes the low-frequency noise. A threshold of 0.75 pC is 5σ of the worst band noise and 2.4× below the smallest event. |
| F6 | The ZedBoard 3.3 V rail comes from a switching regulator. | Filter every analog rail from it (RC or ferrite plus capacitor). Check the PMOD current rating of the ZedBoard (open item). |
| F7 | The charge amplifier is the largest always-on load. A 3 MHz amplifier needs a larger Cf: noise gain = 1 + Cp/Cf and the −3 dB point is GBW / noise gain. | Cf = 220 pF gives a noise gain of 8.3 and a corner of 360 kHz. Events become 23 mV for 5 pC. Downstream gain rises to about ×20. |

## 3. Architecture

```
  piezo ──> HEAD (always on)               ┌──────── always-on rail  +3V3_L ──────────────┐
            charge amp OPA314, Cf 220 pF   │  head amp 150 µA, comparators 4 × 5 µA,       │
            └─ coax with bias-T ─────────> │  dividers 1M, latch                          │
                                           │                                              │
   SIG_IN ─┬─ passive HPF 100 kHz ─> window comparators ─> WAKE_N, BIG_N (open drain) ─> PMOD
           │                                              └> latch (cleared by FPGA)
           │
           └─ C33 ─> capture chain, gated rail +3V3_C  (TPS22916, jumper SJ_CAP)
                      HPF ─ gain ─ LPF ─ THS4531 ─ ADS7057
                      AVDD from +3V3_C through RC; DVDD from +3V3_L (always)
```

Rails:
- `+3V3`: PMOD pins 6 and 12, or the header J7 (battery later). A solder jumper SJ_PMOD joins the PMOD pins to the rail. Bridged by default. Cut it when you use a battery.
- `+3V3_L`: `+3V3` through a 100 Ω and 10 µF filter. Powers the listener and the head.
- `+3V3_C`: switched by a TPS22916 load switch. Powers the filters, gain, driver and the ADC analog side. Jumper SJ_CAP selects the enable: `+3V3` (always on, default), `CAP_EN` from the FPGA, or `WAKE_LATCH`.

PMOD pins (digital only): 1 CS, 3 SDO, 4 SCLK, 10 WAKE_N (existing); 2 CAP_EN (in); 7 BIG_N (out); 8 WAKE_CLR (in); 9 spare.

## 4. Parameters to set (start values, with the equation or the reason)

| Parameter | Start | How it is derived | Check |
|---|---|---|---|
| Cf | 220 pF C0G | GBW / (1 + Cp/Cf) ≥ 360 kHz | S1, bandwidth at 250 kHz within 2 dB |
| Rf | 1 MΩ | low corner 1/(2π Rf Cf) = 720 Hz | DC offset from bias current and leakage under 1 mV |
| Charge amp | OPA314 (single, SC-70-5, 150 µA) | 3 MHz, 14 nV/√Hz, 0.2 pA | S1, S2, stability into the coax |
| Listener HPF | 100 pF and 16 kΩ at SIG_IN | corner 100 kHz, first order | S2, false alarms |
| Threshold 1 (WAKE) | ±0.75 pC → ±3.4 mV at 220 pF | 5σ of the worst in-band noise (0.15 pC) | S2, miss and false-alarm rate. Close to the comparator offset: check DC3 |
| Threshold 2 (BIG) | ±4 pC → ±18 mV | amplitude class: 4 of the 7 events are above 5 pC | S2 |
| Comparator | TLV7022 dual, open drain | 5 µA, 260 ns, 1.6 V to 5.5 V | offset and hysteresis from the datasheet (verify) |
| Reference for comparators | 1 MΩ / 1 MΩ + 1 µF from `+3V3_L` | 1.65 µA, τ = 0.5 s | settle after power-up under 3 s |
| Threshold dividers | 1 MΩ range | comparator bias 5 pA | leakage and humidity, guard |
| Mid-rail of the capture chain | 10k / 10k + buffer U2B, on `+3V3_C` | τ = 5 ms, as today | wake to ready under 30 ms |
| VOCM | 1k / 1k from AVDD | as today, gated | none |
| Bias-T at 3.3 V | L 470 µH, R 47 Ω, C 100 nF | head V+ ≈ 3.3 − 150 µA × 92 Ω = 3.29 V | S3, loss at 250 kHz under 0.3 dB |
| Wake latch | 74AUP1G74, 0.5 µA | holds the first hit until the FPGA clears it | S6 |

Gain in the capture chain moves from ×4.9 to about ×20 because the head output is 4.7× smaller. R3 and R4 set it. The clip level at the gain stage moves with it (S1).

## 5. Parts (JLCPCB library, 2026-10-15; all extended, +$3.09 per new type)

| Block | Part | LCSC | Price | Note |
|---|---|---|---|---|
| Charge amp | OPA314AIDCKR | C529572 | $1.12 | stock 4672. Dual OPA2314 C2058438 had 95 in stock |
| Comparator, open drain | TLV7022DDFR | C2862588 | $0.71 | stock 553 |
| Comparator, alternative | TLV7021DBVR | C2860939 | $0.37 | single, stock 6273 |
| Load switch | TPS22916BYFPR | C2150095 | $0.18 | 0.7 mm DSBGA. Hard to hand rework |
| Latch | SN74AUP1G74DQER | C2677745 | $0.19 | X2SON, tiny |
| Supply filter | existing 0603 parts | | | |

Dropped: USB-C, J2, SS14 ×2, FB1, C23, XC6206 (AVDD becomes an RC filter), LM393, the head's OPA365.

Open: the OPA314 TI model for ngspice, and the TLV7022 model (S1, S2). The TI PSpice models may not run in ngspice, as with the THS4531. A behavioural comparator is the fallback.

## 6. Simulations

| ID | Question | Tool and model | Input | Pass criterion |
|---|---|---|---|---|
| S1 | Does the whole chain work on 3.3 V? | ngspice, OPA365 vendor model, THS4531 behavioural | `sim/vendor_chain.py` with V5 = 3.3, gain ×20 | gain at 250 kHz as designed, 10 kHz loss ≥ 40 dB, clip level ≥ 2× a 120 mV event, noise ≤ 1 LSB at the ADC |
| S2 | What threshold gives no misses and few false alarms? | Python (`sim/listener_first_look.py` first), then ngspice for the comparator | the 25 raw captures (62 500 points at 250 MS/s, 7 true events and 18 noise triggers), band noise 0.06 to 0.15 pC | all 7 events detected at 0.75 pC, none of the 18 noise triggers fire after the 100 kHz high-pass |
| S3 | Does the bias-T at 3.3 V cost signal? | ngspice, `sim/head_bias_t.py` with V = 3.3 and OPA314 | 1 m cable, Cp 1.6 nF ± 20 % | loss at 250 kHz ≤ 0.3 dB, V+ at the head ≥ 3.1 V |
| S4 | Is the 150 µA charge amp stable into the coax and Cp? | ngspice AC with the TI model if it runs, else behavioural plus a loop-gain calculation | Cp 1.28 to 1.92 nF, cable 0 to 1 nF | phase margin ≥ 45° |
| S5 | How long does the gated chain take to be ready? | ngspice transient | TPS22916 turn-on, VMID5, VOCM, AVDD RC | all rails within 0.5 LSB of final in 30 ms |
| S6 | What does the latch and the comparator timing look like? | ngspice with behavioural comparator and flip-flop | a burst at 250 kHz, 23 mV | WAKE_N goes low within 1 µs of the first threshold crossing and stays until cleared |
| S7 | What does the supply do to the signal? | ngspice AC of PSRR, with 50 mV ripple at 100 kHz to 1 MHz on `+3V3` | filter values from section 4 | ripple at the charge amp output ≤ 10 µV |
| S8 | What is the average current per state, and the battery life? | Python spreadsheet from the power table | listener, capture, MCU, LoRa | for the 3 Ah case, listener ≤ 200 µA, total ≤ 300 µA |
| S9 | Monte Carlo of tolerances | ngspice, 150 runs | R 1 %, C0G 5 %, X5R 10 %, Cp ± 20 %, comparator offset | detection and band meet S1 and S2 in 95 % of runs |
| S10 | Is the ZedBoard rail noisy enough to matter? | measure first (bench), then model | scope at the PMOD pins 6 and 12 | measured, then feeds S7 |

## 7. Design checks

| ID | Check |
|---|---|
| DC1 | DC operating point of every node in LISTEN and in LAB (ngspice `op`). No node outside 0.1 V to 3.2 V. |
| DC2 | Every IC supply pin inside the datasheet range at 3.0 V, 3.3 V and 3.6 V. |
| DC3 | Comparator offset and hysteresis against the threshold (worst case, from the datasheet). |
| DC4 | Leakage budget: board leakage at 80 % humidity (about 1 nA across 1 mm) against the 1 MΩ dividers and Rf. |
| DC5 | Power-up sequence: AVDD stable before the first SPI frame. FPGA SPI idle low while `+3V3_C` is off. |
| DC6 | Absolute maximum on every pin when `+3V3_C` is off and the head still drives SIG_IN. |
| DC7 | Inrush of the load switch into the capture rail capacitance (about 30 µF). |
| DC8 | Pull-ups: open-drain WAKE_N, BIG_N to `+3V3_L`. |
| DC9 | Latch default state at power-up. WAKE_N must not hold the FPGA in reset. |
| DC10 | JLCPCB stock and rotation of every new part. |
| DC11 | ERC and DRC clean. Parity between schematic and board. |
| DC12 | The bill of materials still fits the cost target (about $150 for 2 + 5 boards). |

## 8. Layout and parasitic rules

| ID | Rule |
|---|---|
| L1 | The summing node of the head (TP1, Rf, Cf, amp input) is the most sensitive node. Keep it under 6 mm of track. No test point, no via. Guard ring tied to VREF around it. |
| L2 | The 1 MΩ dividers and the comparator inputs sit away from the PMOD and the SPI lines. At least 3 mm, with a ground pour between. |
| L3 | No solder mask opening or silkscreen over the guard. Leave the head for conformal coating. |
| L4 | Test-point stubs: 1 kΩ at the node end for SIG, HPF, GAIN, LPF, DRV±, AIN±. Isolates the stub capacitance (about 0.5 pF per cm). |
| L5 | The listener rail `+3V3_L` has its own filter and a star point at the PMOD connector. |
| L6 | The gated rail `+3V3_C` returns to the same ground plane. No split ground. |
| L7 | The load switch and its capacitors sit next to the capture chain, not at the PMOD. |
| L8 | The capture chain keeps the current block order, left to right. The listener sits between the SMA and the capture chain. |
| L9 | Bottom ground plane stays unbroken under the listener. |
| L10 | The PMOD signal pins have 22 Ω series resistors, as now. WAKE_N and BIG_N get 100 Ω to limit the FPGA input current. |
| L11 | Parasitic extraction: estimate stub capacitance, summing node capacitance and coupling to SDO and SCLK from the board file with a script. Feed the values back into S1 and S2. |
| L12 | Board size target: 57 × 38 mm or smaller. The head stays 10 × 22 mm with the + pad on the centre line. |

## 9. Power measurement plan

Add a two-pin footprint (solder jumper, 0 Ω) at the entry of each domain, so one meter can read each block:

| Link | Domain |
|---|---|
| M1 | head, through the bias-T |
| M2 | listener: comparators, dividers, latch |
| M3 | capture rail: filters, gain, driver |
| M4 | ADS7057 AVDD |
| M5 | ADS7057 DVDD |

States to measure with a µA meter or Joulescope: LAB (all on), LISTEN idle, LISTEN with an event, and capture running. The table feeds S8.

## 10. Bench validation

| ID | Test | Result |
|---|---|---|
| T1 | Power-up from the ZedBoard PMOD only. | rails, ripple, current |
| T2 | Current per domain in each state. | µA table |
| T3 | Charge amp response with 10 pF step injection into TP1. | gain and bandwidth |
| T4 | Listener threshold sweep with the AD2, 250 kHz bursts. | detection curve |
| T5 | False alarms over 24 h on the plant, no touch. | count per hour |
| T6 | Event log over several days: WAKE_N and BIG_N timestamps by the FPGA. | events per day, amplitude classes |
| T7 | Capture chain with CAP_EN from the FPGA: wake to ready time. | ms |
| T8 | Supply ripple injection. | µV at the ADC |
| T9 | SPI at 10 and 60 MHz while listening. | noise change |
| T10 | Day and night temperature drift. | threshold drift |

## 11. Work breakdown and gates

| Step | Work | Output | Gate to the next step |
|---|---|---|---|
| G0 | Confirm answers to the open items (section 12). | decisions | you sign off |
| G1 | S1, S2, S3, S4 | parameter table final | S2 passes with the real events |
| G2 | Schematic: new rails, listener, load switch, jumpers, test-point isolators. | `.kicad_sch`, ERC clean | DC1 to DC9 |
| G3 | Placement and route, parasitic estimate (L11), S5 to S9 on the extracted values. | `.kicad_pcb`, DRC clean | S5 to S9 pass |
| G4 | Files, quote, manual pass (power, listener, wake-up, new test steps). | fab zip, BOM, CPL, manual v0.3 | DC10 to DC12 |
| G5 | Order, bring-up by T1 to T10. | measured power and event log | the product decision |

Estimated work on my side: G1 about one day, G2 and G3 about one to two days, G4 half a day. G5 is yours.

## 12. Open items and risks

| # | Item | Why it matters |
|---|---|---|
| O1 | Current limit of the ZedBoard PMOD 3.3 V pins (reference manual). | LISTEN is tiny, LAB peaks at about 35 mA per board, four boards 140 mA |
| O2 | Noise on the ZedBoard 3.3 V rail at 100 kHz to 1 MHz. | S7, filter values |
| O3 | Whether a 3 MHz amplifier at 150 µA is enough for waveform capture. | LAB mode may need the OPA365 on the head. Option: a header to fit it |
| O4 | TI SPICE models for OPA314 and TLV7022 in ngspice. | S2, S4, S6 |
| O5 | Real events per day, and the amplitude spread. | decides the product duty cycle (T6) |
| O6 | Battery type and voltage range of the product. | rail, brown-out, LDO |
| O7 | The listener sits at 8σ of the in-band noise only if the 4 mV was electronic. | If the plant picks up more noise, the threshold rises (T5) |
| O8 | Extended part fees: OPA314, TLV7022, TPS22916, 74AUP1G74 = +$12 per order. | cost step |

Decisions I made without asking: single-ended ADC chain stays (it does not change power), the head keeps the bias-T, LAB is the default. Say if any of these should change.
