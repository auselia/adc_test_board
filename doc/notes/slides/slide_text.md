# Slide text for slides 3 to 13 (STE style: short sentences, simple tenses, no semicolons)

## Slide 3. Input and bias-T
Subtitle: One cable brings the signal in and the power out
- One coax cable carries the signal and the 3.3 V power. Two 470 µH inductors pass the DC. Two 100 nF capacitors pass the signal.
- The head gets 2.9 V. R26 and the two inductors drop 0.4 V (4.3 mA through 92 Ω).
- The bias-T is also a high-pass filter with a 33 kHz corner. It removes 19 dB at 10 kHz and only 0.2 dB at 250 kHz.
Files: s03_biast.pdf, s03_circuit.svg, s03_graph.svg

## Slide 4. High-pass filter
Subtitle: Cut the plant noise below the AE band
- A Sallen-Key high-pass filter has its corner at 112.5 kHz, just below the AE band.
- The baseline noise below 100 kHz is 11 to 27 mV rms, but only 4 mV rms in the band. The filter removes 42 dB at 10 kHz.
- Q is 0.707, so the response is flat with no peak. Part tolerances move the corner between 106 and 120 kHz.
Files: s04_hpf.pdf, s04_circuit.svg, s04_graph.svg

## Slide 5. Gain stage
Subtitle: Amplify the burst, not the DC
- The gain stage multiplies the signal by 4.9 (3.9 kΩ and 1 kΩ). The tolerance is ±1.6 %.
- The 1 kΩ resistor returns to the 1.65 V mid-rail. DC passes at ×1 and does not clip.
- The stage clips at about 0.35 V at the head output. A typical event is 0.12 V, so the margin is 2.9 times.
Files: s05_gain.pdf, s05_circuit.svg, s05_graph.svg

## Slide 6. Low-pass filter and the filter chain
Subtitle: Remove what the ADC cannot represent
- A second Sallen-Key filter, a low-pass at 512 kHz with Q = 0.707, limits the band before the ADC.
- With the high-pass, the chain is a band-pass from 106 to 502 kHz with 12.3 dB of gain. It removes 40 dB at 10 kHz and 24 dB at 2 MHz.
- The ADC samples at about 1.2 MSPS, so signals above 600 kHz fold back. The filter gives only 8 dB at 800 kHz.
Files: s06_lpf.pdf, s06_circuit.svg, s06_graph.svg

## Slide 7. Driver (THS4531)
Subtitle: Turn one wire into the two the ADC needs
- The ADC measures the difference between two inputs. The THS4531 makes a mirror image of the signal around 1.65 V.
- The gain is 1 (four 1 kΩ resistors). Each output carries half of the signal, in opposite directions. DC passes at 1.65 V on both, so nothing clips.
- C11 blocks DC with a corner at 119 Hz, far below the band.
Files: s07_driver.pdf, s07_circuit.svg, s07_graph.svg

## Slide 8. ADC input and ADS7057
Subtitle: A 14-bit ADC and the network that feeds it
- The ADS7057 is a 14-bit ADC with 0.40 mV per code. A 120 mV event at the head gives about 1280 codes.
- When the ADC samples, its 16 pF capacitor pulls 9 pC. Four 100 pF capacitors (400 pF, 25 times more) take it, and the node dips by 22 mV.
- Two 10 Ω resistors recharge the capacitors in 38 ns (hand estimate) and 54 ns at worst (ngspice). The ADC allows 95 ns.
Files: s08_adc.pdf, s08_circuit.svg, s08_graph.svg

## Slide 9. SPI link
Subtitle: Three wires to the ZedBoard
- One frame has 18 clocks: a zero, 14 data bits and three zeros. The data is the sample from the frame before.
- The first frame after power-up has 24 clocks. It calibrates the offset and returns zeros.
- One sample takes 18 clocks plus 95 ns. At 25 MHz the rate is 1.23 MSPS. At 60 MHz it is 2.5 MSPS.
Files: s09_spi.pdf, s09_circuit.svg, s09_graph.svg (frame), s09_rate.svg (sample rate)

## Slide 10. Power and rails
Subtitle: 3.3 V from the PMOD alone
- The board takes 3.3 V from the PMOD. It draws about 25 mA. Four solder jumpers split the rail so each block can be measured alone.
- AVDD is the ADC reference. A 10 Ω resistor and 10 µF give a 1.6 kHz filter. It removes 44 dB at 250 kHz.
- The two 1.65 V mid-rails follow the supply. VMID5 needs about 25 ms to settle after power-up.
Files: s10_power.pdf, s10_circuit.svg, s10_graph.svg (current), s10_avdd.svg (AVDD filter)

## Slide 11. Listener
Subtitle: WAKE_N and BIG_N watch the signal without gating it
- A band-pass (159 kHz to 723 kHz) feeds two window comparators. The chain stays on and the FPGA sees the full waveform.
- One resistor chain sets the thresholds. WAKE_N fires at 35 mV and BIG_N at 111 mV at the input, each within about 12 mV.
- On 25 real captures the largest noise peak is 26 mV and the smallest event is 52 mV. The margin on the noise side is only 1.3 times.
Files: s11_listener.pdf, s11_circuit.svg, s11_graph.svg

## Slide 12. Board and layout
Subtitle: A strip that fits adjacent PMOD ports
- The board is 125 × 21.5 mm with two copper layers. The signal flows from the SMA on the left to the PMOD on the right.
- It holds 105 footprints in six blocks. Every stage has a test point, and four solder jumpers measure the current of each block.
- Five boards with parts cost about 118 dollars. Sixteen cards and heads would cost about 383 dollars, so 16 channels need a bigger budget.
Files: s12_board.pdf, s12_circuit.svg, s12_graph.svg

## Slide 13. Verification and next steps
Subtitle: What the simulation proves and what is open
- A script reads the real netlist and runs ngspice. All DC, gain, current and burst checks pass.
- Nothing has run on a real board yet. The open items are the THS4531 stability with 400 pF, the anti-aliasing margin, the listener margin and the ZedBoard rail noise.
- Next: bring up one board, then scale to 16 channels with the backplane.
Files: s13_verification.pdf, s13_circuit.svg, s13_graph.svg
