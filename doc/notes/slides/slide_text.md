# Slide text for slides 3 to 6 (STE style: short sentences, simple tenses, no semicolons)

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
