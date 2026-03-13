from dataclasses import dataclass


@dataclass
class UptimeInfo:
    seconds: int
    lastboot: str


@dataclass
class OSInfo:
    os_name: str
    os_accuracy: int


@dataclass
class MacAddressInfo:
    mac_address: str
    mac_vendor: str


@dataclass
class PortInfo:
    number: int
    protocol: str
    state: str
    service_name: str
    service_product: str


@dataclass
class DeviceAnalysisInfo:
    device_guess: str
    device_guess_accuracy: float


@dataclass
class DeviceInfo:
    state: str
    ip_addr: tuple
    mac: MacAddressInfo
    ports: list  # A list of all portInfo data class
    os: OSInfo
    uptime: UptimeInfo
    device_analysis: DeviceAnalysisInfo
