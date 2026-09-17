#!/usr/bin/env python3
"""Poll a Sensirion SCD4x CO2 Gadget from BLE advertisements."""

from __future__ import annotations

import argparse
import asyncio
import struct
import sys
from dataclasses import dataclass

COMPANY_ID = 0x06D5  # Sensirion AG
TYPE_SCD4X = b"\x00\x08"


@dataclass(frozen=True)
class Sample:
    device_id: str
    temperature_c: float
    humidity_rh: float
    co2_ppm: int

    def line(self, address: str = "", rssi: int | None = None) -> str:
        extra = ""
        if address:
            extra += f"  {address}"
        if rssi is not None:
            extra += f"  rssi={rssi}"
        return (
            f"{self.co2_ppm:4d} ppm  {self.temperature_c:5.1f} °C  "
            f"{self.humidity_rh:5.1f} %RH  id={self.device_id}{extra}"
        )


def parse_advertisement(raw: bytes) -> Sample | None:
    """Decode a Sensirion type-8 (MyCO2 / SCD4x Gadget) manufacturer payload."""
    if len(raw) < 10 or raw[:2] != TYPE_SCD4X:
        return None
    device_id = raw[2:4].hex().upper()
    temp_ticks, humidity_ticks, co2 = struct.unpack_from("<HHH", raw, 4)
    temperature_c = round(-45 + (175.0 * temp_ticks) / (2**16 - 1), 1)
    humidity_rh = round((100.0 * humidity_ticks) / (2**16 - 1), 1)
    return Sample(device_id, temperature_c, humidity_rh, co2)


def _payloads_from_adv(advertisement_data) -> list[bytes]:
    md = getattr(advertisement_data, "manufacturer_data", None) or {}
    out = []
    for key, value in md.items():
        if key == COMPANY_ID:
            out.append(bytes(value))
    return out


async def _scan(args: argparse.Namespace) -> int:
    try:
        from bleak import BleakScanner
    except ImportError:
        print("bleak is required: pip install bleak  (or: apt install python3-bleak)", file=sys.stderr)
        return 1

    seen: dict[str, Sample] = {}
    stop = asyncio.Event()

    def on_detect(device, advertisement_data) -> None:
        name = (device.name or advertisement_data.local_name or "") or ""
        for payload in _payloads_from_adv(advertisement_data):
            sample = parse_advertisement(payload)
            if sample is None:
                continue
            if args.address and device.address.upper() != args.address.upper():
                continue
            seen[device.address] = sample
            print(sample.line(address=device.address, rssi=advertisement_data.rssi), flush=True)
            if args.once:
                stop.set()
            return
        if args.verbose and (name or advertisement_data.manufacturer_data):
            print(f"# {device.address}  name={name!r}  rssi={advertisement_data.rssi}", flush=True)

    print("scanning for Sensirion SCD4x CO2 Gadget (BLE advertisements)…", file=sys.stderr)
    async with BleakScanner(on_detect):
        try:
            if args.timeout <= 0:
                await stop.wait()
            else:
                await asyncio.wait_for(stop.wait(), timeout=args.timeout)
        except asyncio.TimeoutError:
            pass
        except KeyboardInterrupt:
            pass

    if not seen:
        print("no SCD4x Gadget advertisements seen", file=sys.stderr)
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--timeout", type=float, default=30.0, help="scan duration in seconds (0 = until interrupted)")
    p.add_argument("--once", action="store_true", help="print one sample and exit")
    p.add_argument("--address", help="only accept this BLE MAC")
    p.add_argument("-v", "--verbose", action="store_true", help="log other BLE devices")
    args = p.parse_args(argv)
    return asyncio.run(_scan(args))


if __name__ == "__main__":
    sys.exit(main())
