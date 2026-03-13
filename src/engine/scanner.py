# import subprocess
import netifaces
import ipaddress
import xmltodict
import re
from .device_guesser import guess_device_category
from .types import DeviceInfo, MacAddressInfo, OSInfo, UptimeInfo, PortInfo, DeviceAnalysisInfo
from db_writer import save_scan_results_to_db


def scan_network() -> None:
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

    time_stamp = re.search(r"scan initiated(.*?) as", content)
    if time_stamp:
        print(time_stamp)

    host_blocks = re.findall(r"(<host starttime=.*?</host>)", content, re.DOTALL)

    host_list = []
    print("The amount of hosts is: ", len(host_blocks))
    for host_data in host_blocks:
        host = make_host_into_datatype(host_data)
        host_list.append(host)


# Function gets xml host input, returns dict of all required info.
def make_host_into_datatype(host_block: str) -> DeviceInfo:
    data = xmltodict.parse(host_block)
    print(data)

    try:
        mac_addresss = data["host"]["address"][1]["@addr"]
    except (KeyError, IndexError):
        mac_addresss = "Unknown"
    try:
        mac_vendor = data["host"]["address"][1]["@vendor"]
    except (KeyError, IndexError):
        mac_vendor = "Unknown"

    macInfo = MacAddressInfo(mac_address=mac_addresss, mac_vendor=mac_vendor)
    try:
        osInfo = OSInfo(os_name=data["host"]["os"]["osmatch"][0]["@name"], os_accuracy=int(data["host"]["os"]["osmatch"][0]["@accuracy"]))
    except (KeyError, TypeError, IndexError):
        osInfo = OSInfo(os_name="Unknown", os_accuracy=0)

    try:
        uptimeInfo = UptimeInfo(seconds=int(data["host"]["uptime"]["@seconds"]), lastboot=data["host"]["uptime"]["@lastboot"])
    except KeyError:
        uptimeInfo = UptimeInfo(seconds=0, lastboot="Unknown")

    try:
        portsList = []
        ports = data["host"]["ports"]["port"]
        if isinstance(ports, dict):
            ports = [ports]

        for port in ports:
            portInfo = PortInfo(number=int(port["@portid"]), protocol=port["@protocol"], state=port["state"]["@state"], service_name=port["service"]["@name"], service_product=port["service"].get("@product", "Unknown"))
            portsList.append(portInfo)

    except KeyError:
        portsList = []

    try:
        ip_addr = data["host"]["address"][0]["@addr"], data["host"]["address"][0]["@addrtype"]
    except KeyError:
        ip_addr = (data["host"]["address"]["@addr"], data["host"]["address"]["@addrtype"])

    device_guess, accuracy_percent = guess_device_category(macInfo.mac_vendor, osInfo.os_name, portsList, uptimeInfo.seconds)
    device_analysis = DeviceAnalysisInfo(device_guess=device_guess, device_guess_accuracy=accuracy_percent)
    host = DeviceInfo(state=data["host"]["status"]["@state"], ip_addr=ip_addr, mac=macInfo, ports=portsList, os=osInfo, uptime=uptimeInfo, device_analysis=device_analysis)
    return host
