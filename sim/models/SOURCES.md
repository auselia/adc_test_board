# Vendor models for the verification suite

Run `python3 fetch_models.py` to download and prepare them. The `.lib` files are not stored in the repo.

| Part | Source | Use in ngspice |
|---|---|---|
| OPA365 (OPA2365 is two channels) | https://www.ti.com/lit/tsm/sbom203 (TINA container, netlist extracted) | Works. Used for all four op-amp channels. |
| THS4531 | https://www.ti.com/lit/zip/slom263 | Loads, but the gain is 0.72 at 10 kHz and the -3 dB point is 17 kHz. Not used. Use `sim/ltspice/ths4531_cap_load.cir` in LTspice. |
| ADS7057 | https://www.ti.com/lit/zip/SBAM365 (TINA, encrypted) | Not usable. The datasheet input model (50 ohm, 16 pF per leg) is used. |
| LM393 | not found on ti.com | Not simulated. The comparator window is calculated. |
