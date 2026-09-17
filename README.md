# scd4x-gadget

Poll a [Sensirion SCD4x CO² Gadget](https://sensirion.com) (MyCO2) from Bluetooth Low Energy advertisements. No GATT connection is required.

Prints CO₂ (ppm), temperature (°C), and relative humidity on each advertisement.

## Requirements

- Python 3.10+
- [bleak](https://github.com/hbldh/bleak)
- A Bluetooth adapter with BlueZ (Linux) or the platform BLE stack (macOS)

On Debian/Ubuntu:

```bash
sudo apt install python3-bleak
```

On Linux the invoking user needs permission to talk to BlueZ (typically membership in the `bluetooth` group). Root is not required.

```bash
sudo usermod -aG bluetooth "$USER"
# log out and back in so the group applies
```

## Usage

```bash
python3 scd4x_gadget.py --once              # one sample, then exit
python3 scd4x_gadget.py --timeout 0         # until Ctrl-C
python3 scd4x_gadget.py --address AA:BB:CC:DD:EE:FF
python3 scd4x_gadget.py -v                  # also log other BLE devices
```

`--address` is optional. If omitted, every Sensirion type-8 (SCD4x / MyCO2) advertisement is printed.

## Protocol

Manufacturer ID `0x06D5` (Sensirion AG), payload type `00 08`:

| Offset | Field |
|--------|--------|
| 0–1 | type `00 08` |
| 2–3 | device id |
| 4–5 | temperature ticks (uint16 LE) |
| 6–7 | humidity ticks (uint16 LE) |
| 8–9 | CO₂ ppm (uint16 LE) |

```
T  = -45 + 175 * ticks / 65535
RH = 100 * ticks / 65535
CO2 = ticks as ppm
```

See Sensirion's BLE communication protocol and the type-8 sample in [akx/sensirion-ble](https://github.com/akx/sensirion-ble).

## Tests

```bash
python3 -m unittest tests.test_scd4x_gadget -v
```

## License

MIT. Not affiliated with Sensirion AG.
