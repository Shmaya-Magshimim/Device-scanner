from socket import AddressInfo
import subprocess
import netifaces
import ipaddress
import xmltodict
import re
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
    id: int
    protocol: str
    state: str
    service_name: str
    service_product: str


@dataclass
class XMlHost:
    state: str
    ip_addr: tuple
    mac: MacAddressInfo
    ports: list  # A list of all portInfo data class
    os: OSInfo
    uptime: UptimeInfo


def main():
    default_gateway = netifaces.gateways()
    # Grab the tuple for the default IPv4 gateway
    gw_info = default_gateway["default"][netifaces.AF_INET]

    gateway_ip, default_interface = gw_info[:2]
    netmask = netifaces.ifaddresses(default_interface)[netifaces.AF_INET][0]["netmask"]
    network = ipaddress.IPv4Network(f"{gateway_ip}/{netmask}", strict=False)
    # subprocess.run(["nmap", "-O", "-sV", "-oX", "scan.xml", str(network)])

    print("Scan finished")

    with open("scan.xml") as file:
        content = file.read()

    host_blocks = re.findall(r"(<host starttime=.*?</host>)", content, re.DOTALL)

    host_list = []
    print("The amount of hosts is: ", len(host_blocks))
    for host_data in host_blocks:
        host = make_host_into_datatype(host_data)
        host_list.append(host)


# Function gets xml host input, returns dict of all required info.
def make_host_into_datatype(host_block):
    data = xmltodict.parse(host_block)
    macInfo = MacAddressInfo(mac_address=data["host"]["address"][1]["@addr"], mac_vendor=data["host"]["address"][1]["@vendor"])
    osInfo = OSInfo(os_name=data["host"]["os"]["osmatch"][0]["@name"], os_accuracy=int(data["host"]["os"]["osmatch"][0]["@accuracy"]))
    uptimeInfo = UptimeInfo(seconds=int(data["host"]["uptime"]["@seconds"]), lastboot=data["host"]["uptime"]["@lastboot"])
    portsList = []
    for port in data["host"]["ports"]["port"]:
        portInfo = PortInfo(id=int(port["@portid"]), protocol=port["@protocol"], state=port["state"]["@state"], service_name=port["service"]["@name"], service_product=port["service"].get("@product", "Unknown"))
        portsList.append(portInfo)

    host = XMlHost(state=data["host"]["status"]["@state"], ip_addr=(data["host"]["address"][0]["@addr"], data["host"]["address"][0]["@addrtype"]), mac=macInfo, ports=portsList, os=osInfo, uptime=uptimeInfo)
    return host


if __name__ == "__main__":
    main()
