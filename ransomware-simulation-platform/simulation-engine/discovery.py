"""
System Discovery Simulator
Simulates reconnaissance and system enumeration.
Returns fabricated system data — no real system info is collected.

All user accounts, software lists, network configs, and shares are
procedurally generated at runtime so every session produces a unique
target environment.
"""

import time
import random
import platform
from datetime import datetime, timedelta


# ── Procedural component pools ────────────────────────────────────────

_FIRST_NAMES = [
    "james", "sarah", "michael", "linda", "robert", "maria", "david",
    "jennifer", "william", "elizabeth", "daniel", "patricia", "richard",
    "susan", "thomas", "nancy", "charles", "karen", "joseph", "betty",
]
_LAST_NAMES = [
    "smith", "johnson", "williams", "brown", "jones", "garcia", "miller",
    "davis", "rodriguez", "martinez", "hernandez", "lopez", "gonzalez",
    "wilson", "anderson", "thomas", "taylor", "moore", "jackson", "martin",
]

_DEPARTMENTS = [
    "Domain Users", "Engineering", "Finance", "IT Support", "Marketing",
    "HR", "Sales", "Operations", "Legal", "Executive", "Research",
]
_ELEVATED_GROUPS = [
    "Administrators", "Remote Desktop Users", "Backup Operators",
    "Power Users", "Server Operators", "DNS Admins",
]

_SW_POOL = [
    ("Microsoft Office", "16.0.{b1}"),
    ("Google Chrome", "{major}.0.{b1}"),
    ("Mozilla Firefox", "{major}.0.{minor}"),
    ("Adobe Acrobat Reader", "20{yy}.001.{b1}"),
    ("Slack", "4.{major}.{b1}"),
    ("Zoom", "6.{minor}.{patch}"),
    ("Visual Studio Code", "1.{major}.{minor}"),
    ("Python", "3.{major}.{minor}"),
    ("7-Zip", "{major}.{minor:02d}"),
    ("Notepad++", "8.{major}.{minor}"),
    ("WinSCP", "6.{minor}.{patch}"),
    ("PuTTY", "0.{major}"),
    ("VLC Media Player", "3.0.{b1}"),
    ("Wireshark", "4.{minor}.{patch}"),
    ("Git", "2.{major}.{minor}"),
    ("Node.js", "20.{major}.{minor}"),
    ("Docker Desktop", "4.{major}.{minor}"),
    ("Postman", "11.{minor}.{patch}"),
    ("FileZilla", "3.{major}.{minor}"),
    ("KeePass", "2.{major}"),
]

_OS_CHOICES = [
    ("Windows 10 Enterprise", "10.0.19045", "19045"),
    ("Windows 10 Pro", "10.0.19044", "19044"),
    ("Windows 11 Enterprise", "10.0.22631", "22631"),
    ("Windows 11 Pro", "10.0.22621", "22621"),
    ("Windows Server 2022", "10.0.20348", "20348"),
]

_DOMAIN_WORDS = ["corp", "global", "internal", "hq", "office", "prod"]
_DOMAIN_ORGS = ["acme", "initech", "globex", "contoso", "simulco", "nexagen", "cyphertek"]

_SHARE_NAMES = [
    "SharedDocs", "Finance", "Engineering", "Marketing", "IT",
    "HR_Confidential", "Projects", "Archive", "Media", "Legal",
]
_SHARE_ACCESS = ["Read/Write", "Read", "Denied", "Read", "Read/Write"]

_SERVER_ROLES = [
    ("FILESERVER", "File Server"),
    ("DC", "Domain Controller"),
    ("SQLSERVER", "Database Server"),
    ("BACKUPSVR", "Backup Server"),
    ("WEBSERVER", "Web Server"),
    ("MAILSERVER", "Mail Server"),
    ("APPSERVER", "Application Server"),
    ("PRINTSVR", "Print Server"),
]


def _gen_username():
    first = random.choice(_FIRST_NAMES)
    last = random.choice(_LAST_NAMES)
    fmt = random.choice([
        f"{first[0]}.{last}",
        f"{first}.{last[0]}",
        f"{first}_{last}",
        f"{first[0]}{last}",
    ])
    return fmt


def _gen_user(base_ip_third_octet: int):
    uname = _gen_username()
    groups = [random.choice(_DEPARTMENTS)]
    if random.random() < 0.25:
        groups.append(random.choice(_ELEVATED_GROUPS))
    days_ago = random.randint(0, 14)
    hours = random.randint(0, 23)
    minutes = random.randint(0, 59)
    last_login = (datetime.now() - timedelta(days=days_ago)).replace(
        hour=hours, minute=minutes, second=random.randint(0, 59)
    )
    return {
        "username": uname,
        "groups": groups,
        "last_login": last_login.strftime("%Y-%m-%d %H:%M:%S"),
    }


def _gen_svc_account():
    prefixes = ["svc", "srv", "app", "sql", "bak", "adm"]
    names = ["backup", "agent", "monitor", "sql", "web", "deploy", "scan", "sync"]
    uname = f"{random.choice(prefixes)}_{random.choice(names)}"
    return {
        "username": uname,
        "groups": [random.choice(_ELEVATED_GROUPS)],
        "last_login": (datetime.now() - timedelta(days=random.randint(0, 7))).strftime("%Y-%m-%d %H:%M:%S"),
    }


def _gen_software(count: int):
    items = random.sample(_SW_POOL, k=min(count, len(_SW_POOL)))
    result = []
    for name, ver_tpl in items:
        ver = ver_tpl.format(
            major=random.randint(80, 130),
            minor=random.randint(0, 20),
            patch=random.randint(0, 99),
            b1=random.randint(10000, 99999),
            yy=random.randint(24, 26),
        )
        result.append({"name": name, "version": ver})
    return result


def _gen_network(session_seed: str):
    """Generate a plausible network config seeded on the session."""
    subnet_third = random.randint(1, 254)
    host_octet = random.randint(100, 200)
    ip = f"192.168.{subnet_third}.{host_octet}"
    gateway = f"192.168.{subnet_third}.1"
    dns1 = f"192.168.{subnet_third}.{random.randint(2, 15)}"
    dns2 = f"192.168.{subnet_third}.{random.randint(2, 15)}"
    word = random.choice(_DOMAIN_WORDS)
    org = random.choice(_DOMAIN_ORGS)
    domain = f"{word}.{org}.local"
    hostname = f"WS-{session_seed[:6].upper()}"
    mac = ":".join(f"{random.randint(0,255):02X}" for _ in range(6))

    interfaces = [{"name": "Ethernet0", "ip": ip, "status": "Up"}]
    if random.random() < 0.4:
        interfaces.append({"name": "Wi-Fi", "ip": "N/A", "status": "Disconnected"})
    if random.random() < 0.2:
        vpn_ip = f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(2,254)}"
        interfaces.append({"name": "VPN-Tunnel0", "ip": vpn_ip, "status": "Up"})

    return {
        "hostname": hostname,
        "domain": domain,
        "ip_address": ip,
        "subnet_mask": "255.255.255.0",
        "gateway": gateway,
        "dns_servers": [dns1, dns2],
        "mac_address": mac,
        "interfaces": interfaces,
        "subnet_third": subnet_third,  # shared with share / lateral generators
    }


def _gen_shares(subnet_third: int, count: int):
    server_names = random.sample(_SERVER_ROLES, k=min(count, len(_SERVER_ROLES)))
    share_names = random.sample(_SHARE_NAMES, k=min(count, len(_SHARE_NAMES)))
    shares = []
    for i in range(count):
        srv_label, _ = server_names[i % len(server_names)]
        srv_num = f"{random.randint(1, 9):02d}"
        srv_ip = f"192.168.{subnet_third}.{random.randint(2, 30)}"
        share = share_names[i % len(share_names)]
        access = random.choice(_SHARE_ACCESS)
        shares.append({
            "name": f"\\\\{srv_label}{srv_num}\\{share}",
            "ip": srv_ip,
            "type": "SMB",
            "access": access,
        })
    return shares


class DiscoverySimulator:
    """Simulates system discovery techniques used during ransomware attacks."""

    def __init__(self, session_id, context=None):
        self.session_id = session_id
        self.context = context or {}
        self.events = []
        self.discovery_data = {}

    def simulate(self):
        """Run full system discovery simulation with generated data."""
        events = []

        events.append(self._event("INFO", "System discovery simulation initiated"))
        time.sleep(random.uniform(0.10, 0.25))

        # ── OS Info ───────────────────────────────────────────────────
        os_name, os_ver, os_build = random.choice(_OS_CHOICES)
        arch = random.choice(["x86_64", "AMD64"])
        network = _gen_network(self.session_id)
        os_info = {
            "os": os_name,
            "version": os_ver,
            "build": os_build + f".{random.randint(1000, 9999)}",
            "architecture": arch,
            "hostname": network["hostname"],
        }
        self.discovery_data["os_info"] = os_info
        events.append(self._event(
            "INFO",
            f"OS: {os_info['os']} Build {os_info['build']} ({arch})",
            {"os_info": os_info},
        ))
        time.sleep(random.uniform(0.08, 0.20))

        # ── Users ─────────────────────────────────────────────────────
        num_users = random.randint(3, 7)
        users = [_gen_user(network["subnet_third"]) for _ in range(num_users)]
        # Add 1-2 service accounts
        for _ in range(random.randint(1, 2)):
            users.append(_gen_svc_account())
        random.shuffle(users)
        self.discovery_data["users"] = users
        events.append(self._event("INFO", f"Discovered {len(users)} user account(s)", {"users": users}))
        for u in users:
            events.append(self._event(
                "INFO",
                f"  └─ {u['username']} | Groups: {', '.join(u['groups'])} | Last: {u['last_login']}"
            ))
            time.sleep(random.uniform(0.04, 0.12))

        # ── Network ──────────────────────────────────────────────────
        self.discovery_data["network"] = network
        events.append(self._event(
            "INFO",
            f"Network: {network['ip_address']} ({network['domain']})",
            {"network": network},
        ))
        time.sleep(random.uniform(0.08, 0.20))

        # ── Shares ───────────────────────────────────────────────────
        num_shares = random.randint(3, 6)
        shares = _gen_shares(network["subnet_third"], num_shares)
        self.discovery_data["shares"] = shares
        events.append(self._event("INFO", f"Discovered {len(shares)} network share(s)", {"shares": shares}))
        for s in shares:
            events.append(self._event("INFO", f"  └─ {s['name']} [{s['type']}] Access: {s['access']}"))
            time.sleep(random.uniform(0.03, 0.10))

        # ── Software ─────────────────────────────────────────────────
        num_sw = random.randint(5, 12)
        software = _gen_software(num_sw)
        self.discovery_data["software"] = software
        events.append(self._event("INFO", f"Discovered {len(software)} installed application(s)", {"software": software}))
        for sw in software:
            events.append(self._event("INFO", f"  └─ {sw['name']} v{sw['version']}"))
            time.sleep(random.uniform(0.02, 0.08))

        events.append(self._event("INFO", "System discovery simulation complete"))
        self.events.extend(events)
        return events

    def get_discovery_data(self):
        return self.discovery_data

    def _event(self, level, message, details=None):
        return {
            "timestamp": datetime.now().isoformat(),
            "stage": "discovery",
            "level": level,
            "message": message,
            "details": details or {},
            "session_id": self.session_id,
        }
