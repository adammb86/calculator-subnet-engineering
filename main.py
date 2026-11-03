from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

app = FastAPI()


def _parse_ipv4(ip: str) -> int:
    """Validate and convert an IPv4 dotted-decimal string to a 32-bit int."""
    if not isinstance(ip, str) or not ip:
        raise ValueError("IPv4 address required")

    parts = ip.split(".")
    if len(parts) != 4:
        raise ValueError("IPv4 address must have exactly 4 octets")

    octets = []
    for part in parts:
        if not part:
            raise ValueError("IPv4 address must have exactly 4 octets")
        if not part.isdigit():
            raise ValueError("IPv4 octets must be numeric")
        if len(part) > 1 and part[0] == "0":
            raise ValueError("leading zeros are not allowed")
        value = int(part)
        if not 0 <= value <= 255:
            raise ValueError("IPv4 octets must be between 0 and 255")
        octets.append(value)

    return (octets[0] << 24) | (octets[1] << 16) | (octets[2] << 8) | octets[3]


def _parse_prefix(prefix) -> int:
    """Validate a CIDR prefix and return it as an int in range 0..32."""
    if isinstance(prefix, bool) or not isinstance(prefix, int):
        raise ValueError("prefix must be an integer")
    if not 0 <= prefix <= 32:
        raise ValueError("prefix must be between 0 and 32")
    return prefix


def _int_to_ipv4(value: int) -> str:
    return ".".join(
        str((value >> shift) & 0xFF) for shift in (24, 16, 8, 0)
    )


def _mask_from_prefix(prefix: int) -> int:
    if prefix == 0:
        return 0
    return (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF


def hitung_subnet(ip: str, prefix: int) -> dict:
    ip_int = _parse_ipv4(ip)
    prefix = _parse_prefix(prefix)

    mask_int = _mask_from_prefix(prefix)
    network_int = ip_int & mask_int
    host_bits = 32 - prefix

    if prefix == 32:
        network_int = ip_int
        broadcast = None
        first_host = last_host = _int_to_ipv4(ip_int)
        usable_hosts = 1
    elif prefix == 31:
        broadcast = None
        first_host = _int_to_ipv4(network_int)
        last_host = _int_to_ipv4(network_int + 1)
        usable_hosts = 2
    else:
        broadcast_int = network_int | ((1 << host_bits) - 1)
        first_host = _int_to_ipv4(network_int + 1)
        last_host = _int_to_ipv4(broadcast_int - 1)
        broadcast = _int_to_ipv4(broadcast_int)
        usable_hosts = (1 << host_bits) - 2

    return {
        "mask": _int_to_ipv4(mask_int),
        "network": _int_to_ipv4(network_int),
        "broadcast": broadcast,
        "first_host": first_host,
        "last_host": last_host,
        "usable_hosts": usable_hosts,
    }


@app.get("/", response_class=HTMLResponse)
def read_index():
    index_path = Path(__file__).parent / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="index.html tidak ditemukan")
    return HTMLResponse(index_path.read_text(encoding="utf-8"))


@app.get("/api/subnet")
def api_subnet(ip: str = Query(...), prefix: int = Query(...)):
    try:
        return hitung_subnet(ip, prefix)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))