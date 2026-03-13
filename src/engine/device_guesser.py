CATEGORIES = ["Server", "IOT", "Mobile", "PC", "Router"]


def guess_device_category(mac_vendor: str, os_name: str, ports: list, uptime_seconds: float) -> "tuple[str, float]":
    scores = {c: 0.0 for c in CATEGORIES}
    if mac_vendor != "Unknown":
        scores = mac_vendor_guess(mac_vendor, scores)

    if os_name != "Unknown":
        scores = os_guess(os_name, scores)

    if ports:
        scores = port_id_guess(ports, scores)

    if uptime_seconds > 0:
        scores = uptime_guess(uptime_seconds, scores)

    # Normalize scores
    total_score = sum(scores.values())
    if total_score > 0:
        for category in scores:
            scores[category] /= total_score

    # Get category with highest score
    sorted_by_value = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    best_category, best_score = sorted_by_value[0]
    if best_score < 0.2 or (best_score - sorted_by_value[1][1]) < 0.1:  # If no category has a strong score, classify as Unknown
        return ("Unknown", 0.0)
    return (best_category, round(min(best_score * 100 + 20, 100), 2))


# Returns an updated scores version, with an added value
def uptime_guess(uptime_seconds: float, scores: dict) -> dict:
    days = uptime_seconds / (24 * 3600)

    if days >= 7:  # likely server or router
        scores["Server"] += 0.6
        scores["Router"] += 0.4
    elif 1 <= days < 7:  # PC / IoT / server
        scores["PC"] += 0.5
        scores["IOT"] += 0.3
        scores["Server"] += 0.2
    else:  # PC / Mobile
        scores["PC"] += 0.4
        scores["Mobile"] += 0.5
        scores["IOT"] += 0.1

    return scores


def port_id_guess(ports: list, scores: dict) -> dict:
    PORT_RULES = {
        135: {"PC": 0.8, "Server": 0.2},
        137: {"PC": 0.7, "Server": 0.3},
        138: {"PC": 0.7, "Server": 0.3},
        139: {"PC": 0.7, "Server": 0.3},
        53: {"Router": 0.7, "IOT": 0.2, "Server": 0.1},
        445: {"PC": 0.7, "Server": 0.3},
        22: {"Server": 0.8, "PC": 0.2},
        21: {"Server": 1.0},
        25: {"Server": 1.0},
        80: {"Server": 0.4, "Router": 0.4, "IOT": 0.2},
        443: {"Server": 0.7, "IOT": 0.3},
        3306: {"Server": 1.0},
        5432: {"Server": 1.0},
        8080: {"Server": 0.7, "IOT": 0.3},
        8443: {"Server": 0.7, "IOT": 0.3},
        23: {"Router": 0.7, "IOT": 0.3},
        161: {"Router": 1.0},
        162: {"Router": 1.0},
        500: {"Router": 1.0},
        67: {"Router": 1.0},
        68: {"Router": 1.0},
        1883: {"IOT": 1.0},
        8883: {"IOT": 1.0},
        554: {"IOT": 1.0},
        5353: {"IOT": 0.7, "PC": 0.3},
        5223: {"Mobile": 1.0},
        5228: {"Mobile": 1.0},
    }

    for port in ports:
        port_id = port.id
        if port_id in PORT_RULES:
            for category, prob in PORT_RULES[port_id].items():
                scores[category] += prob

    return scores


def os_guess(os_name: str, scores: dict) -> dict:
    OS_RULES = {
        "windows": {"PC": 0.8, "Server": 0.2},
        "mac os": {"PC": 1.0},
        "macos": {"PC": 1.0},
        "ios": {"Mobile": 1.0},
        "iphone os": {"Mobile": 1.0},
        "android": {"Mobile": 0.85, "IOT": 0.15},
        "linux": {"Server": 0.3, "IOT": 0.3, "Router": 0.5},
        "ubuntu": {"Server": 0.7, "PC": 0.3},
        "debian": {"Server": 0.8, "IOT": 0.2},
        "centos": {"Server": 1.0},
        "red hat": {"Server": 1.0},
        "openwrt": {"Router": 1.0},
        "dd-wrt": {"Router": 1.0},
        "routeros": {"Router": 1.0},
        "vyos": {"Router": 0.8, "Server": 0.2},
        "freebsd": {"Server": 0.8, "Router": 0.2},
        "busybox": {"IOT": 0.8, "Router": 0.2},
        "darwin": {"Mobile": 0.6, "PC": 0.4},
    }

    os_name = os_name.lower()

    if not os_name or os_name == "unknown":
        return scores

    for os_key, category_probs in OS_RULES.items():
        if os_key in os_name:
            for category, prob in category_probs.items():
                scores[category] += prob

    return scores


def mac_vendor_guess(mac_vendor: str, scores: dict) -> dict:
    MAC_VENDOR_RULES = {
        "apple": {"Mobile": 0.6, "PC": 0.4},
        "samsung": {"Mobile": 0.8, "IOT": 0.2},
        "xiaomi": {"Mobile": 0.5, "IOT": 0.5},
        "google": {"Mobile": 0.7, "IOT": 0.3},
        "huawei": {"Mobile": 0.6, "Router": 0.4},
        "oneplus": {"Mobile": 0.9, "IOT": 0.1},
        "oppo": {"Mobile": 0.9, "IOT": 0.1},
        "sony": {"Mobile": 0.5, "IOT": 0.5},
        "dell": {"PC": 0.9, "Server": 0.1},
        "hp": {"PC": 0.8, "Server": 0.2},
        "hewlett-packard": {"PC": 0.8, "Server": 0.2},
        "lenovo": {"PC": 0.9, "Server": 0.1},
        "asus": {"PC": 0.7, "Router": 0.3},
        "acer": {"PC": 0.9, "Server": 0.1},
        "msi": {"PC": 0.9, "Server": 0.1},
        "tp-link": {"Router": 0.7, "IOT": 0.3},
        "netgear": {"Router": 0.7, "IOT": 0.3},
        "d-link": {"Router": 0.8, "IOT": 0.2},
        "cisco": {"Router": 0.8, "Server": 0.2},
        "ubiquiti": {"Router": 0.9, "IOT": 0.1},
        "mikrotik": {"Router": 0.9, "Server": 0.1},
        "juniper": {"Router": 0.8, "Server": 0.2},
        "aruba": {"Router": 0.9, "Server": 0.1},
        "zte": {"Router": 0.8, "IOT": 0.2},
        "nokia": {"Router": 0.7, "Server": 0.3},
        "fibrain": {"Router": 0.7, "IOT": 0.3},
        "philips": {"IOT": 0.9, "Mobile": 0.1},
        "tuya": {"IOT": 1.0},
        "wyze": {"IOT": 1.0},
        "ring": {"IOT": 1.0},
        "sonoff": {"IOT": 1.0},
        "espressif": {"IOT": 1.0},
        "raspberry": {"IOT": 0.7, "Server": 0.3},
        "intel": {"PC": 0.5, "Server": 0.3, "Router": 0.2},
        "realtek": {"PC": 0.4, "Router": 0.3, "IOT": 0.3},
        "broadcom": {"Router": 0.4, "PC": 0.3, "IOT": 0.3},
        "qualcomm": {"Mobile": 0.6, "Router": 0.2, "IOT": 0.2},
        "mediatek": {"Router": 0.4, "Mobile": 0.3, "IOT": 0.3},
        "vmware": {"Server": 0.7, "PC": 0.3},
        "microsoft": {"Server": 0.6, "PC": 0.4},
        "virtualbox": {"PC": 0.7, "Server": 0.3},
    }
    mac_vendor = mac_vendor.lower()

    if not mac_vendor or mac_vendor == "unknown":
        return scores

    for vendor, category_probs in MAC_VENDOR_RULES.items():
        if vendor in mac_vendor:
            for category, prob in category_probs.items():
                scores[category] += prob

    return scores
