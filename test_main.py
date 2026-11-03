import pytest
from fastapi.testclient import TestClient

from main import app, hitung_subnet


client = TestClient(app)


# --- Kasus Sukses -----------------------------------------------------------

@pytest.mark.parametrize(
    "ip, prefix, expected",
    [
        # Subnet Standar
        (
            "172.16.5.130",
            25,
            {
                "network": "172.16.5.128",
                "broadcast": "172.16.5.255",
                "first_host": "172.16.5.129",
                "last_host": "172.16.5.254",
                "usable_hosts": 126,
            },
        ),
        # Blok Minimum Standar
        (
            "10.0.0.0",
            30,
            {
                "network": "10.0.0.0",
                "broadcast": "10.0.0.3",
                "first_host": "10.0.0.1",
                "last_host": "10.0.0.2",
                "usable_hosts": 2,
            },
        ),
        # Point-to-Point (RFC 3021)
        (
            "192.168.1.0",
            31,
            {
                "network": "192.168.1.0",
                "broadcast": None,
                "first_host": "192.168.1.0",
                "last_host": "192.168.1.1",
                "usable_hosts": 2,
            },
        ),
        # Host Route
        (
            "192.168.1.5",
            32,
            {
                "network": "192.168.1.5",
                "broadcast": None,
                "first_host": "192.168.1.5",
                "last_host": "192.168.1.5",
                "usable_hosts": 1,
            },
        ),
    ],
)
def test_hitung_subnet_sukses(ip, prefix, expected):
    result = hitung_subnet(ip, prefix)
    assert result["network"] == expected["network"]
    assert result["broadcast"] == expected["broadcast"]
    assert result["first_host"] == expected["first_host"]
    assert result["last_host"] == expected["last_host"]
    assert result["usable_hosts"] == expected["usable_hosts"]


# --- Kasus Input Tidak Valid ------------------------------------------------

@pytest.mark.parametrize(
    "ip, prefix",
    [
        # IP Tidak Valid (Oktet >255)
        ("256.1.1.1", 24),
        # IP Tidak Valid (Leading Zero)
        ("192.168.01.1", 24),
        # Format Input Rusak
        ("192.168.1", 24),
        ("abc", 24),
        ("", 24),
        # Prefix di Luar Batas
        ("192.168.1.1", 33),
        ("192.168.1.1", -1),
    ],
)
def test_hitung_subnet_invalid(ip, prefix):
    with pytest.raises(ValueError):
        hitung_subnet(ip, prefix)


# --- API: GET /api/subnet (Sukses) ------------------------------------------

def test_api_subnet_sukses():
    response = client.get("/api/subnet", params={"ip": "172.16.5.130", "prefix": 25})
    assert response.status_code == 200
    body = response.json()
    assert body["network"] == "172.16.5.128"
    assert body["broadcast"] == "172.16.5.255"
    assert body["usable_hosts"] == 126


# --- API: GET /api/subnet (Input Tidak Valid) --------------------------------

@pytest.mark.parametrize(
    "ip, prefix",
    [
        ("256.1.1.1", 24),
        ("192.168.01.1", 24),
        ("192.168.1", 24),
        ("abc", 24),
        ("192.168.1.1", 33),
        ("192.168.1.1", -1),
    ],
)
def test_api_subnet_invalid(ip, prefix):
    response = client.get("/api/subnet", params={"ip": ip, "prefix": prefix})
    assert response.status_code == 400


# --- API: GET / -------------------------------------------------------------

def test_root_mengembalikan_200():
    response = client.get("/")
    assert response.status_code == 200