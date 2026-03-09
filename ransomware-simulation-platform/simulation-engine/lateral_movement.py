"""
Lateral Movement Simulator
Simulates network lateral movement techniques.
No actual network connections are made.

Target hosts are derived from the discovery context when available,
otherwise generated procedurally. Techniques are assembled from
MITRE families with randomised parameters.
"""

import time
import random
from datetime import datetime


# ── Component pools ───────────────────────────────────────────────────

_SERVER_ROLES = [
    ("FILESERVER", "File Server", "Windows Server 2022"),
    ("DC", "Domain Controller", "Windows Server 2022"),
    ("SQLSERVER", "Database Server", "Windows Server 2019"),
    ("BACKUPSVR", "Backup Server", "Windows Server 2022"),
    ("WEBSERVER", "Web Server", "Ubuntu 22.04"),
    ("MAILSERVER", "Mail Server", "Windows Server 2019"),
    ("APPSERVER", "Application Server", "Windows Server 2022"),
    ("PRINTSVR", "Print Server", "Windows Server 2016"),
    ("DEVBOX", "Development Server", "Ubuntu 24.04"),
    ("BUILDSVR", "Build Server", "Windows Server 2022"),
]

_OS_WORKSTATION = ["Windows 10", "Windows 11", "macOS 14", "Ubuntu 22.04"]

_TECHNIQUE_FAMILIES = [
    {"family": "Remote Services", "mitre_ids": ["T1021.001", "T1021.002", "T1021.003", "T1021.004", "T1021.006"],
     "details": [
         ("SMB/Admin Shares", "SMB"),
         ("Remote Desktop Protocol", "RDP"),
         ("Distributed COM", "DCOM"),
         ("SSH", "SSH"),
         ("PowerShell Remoting", "WinRM"),
     ]},
    {"family": "Lateral Tool Transfer", "mitre_ids": ["T1570"],
     "details": [("Tool Transfer via SMB", "SMB"), ("Tool Transfer via HTTP", "HTTP")]},
    {"family": "Remote Execution", "mitre_ids": ["T1047", "T1569.002"],
     "details": [("WMI Remote Execution", "WMI"), ("PsExec", "SMB")]},
    {"family": "Taint Shared Content", "mitre_ids": ["T1080"],
     "details": [("Tainted Shared Folder", "SMB")]},
    {"family": "Internal Spear-phishing", "mitre_ids": ["T1534"],
     "details": [("Internal Phishing via Email", "SMTP"), ("Internal Phishing via Chat", "HTTP")]},
    {"family": "Exploitation of Remote Services", "mitre_ids": ["T1210"],
     "details": [("Remote Service Exploit", "TCP")]},
]


def _gen_targets(subnet_third: int, count: int):
    """Generate unique target hosts on the same subnet."""
    roles = random.sample(_SERVER_ROLES, k=min(count, len(_SERVER_ROLES)))
    targets = []
    used_ips = set()
    for label, role, os_name in roles:
        while True:
            octet = random.randint(2, 50)
            if octet not in used_ips:
                used_ips.add(octet)
                break
        num = f"{random.randint(1,9):02d}"
        targets.append({
            "hostname": f"{label}{num}",
            "ip": f"192.168.{subnet_third}.{octet}",
            "os": os_name,
            "role": role,
        })
    # Occasionally add a workstation
    if random.random() < 0.5:
        ws_num = random.randint(1, 50)
        targets.append({
            "hostname": f"WS-{ws_num:03d}",
            "ip": f"192.168.{subnet_third}.{random.randint(100, 200)}",
            "os": random.choice(_OS_WORKSTATION),
            "role": "Workstation",
        })
    random.shuffle(targets)
    return targets[:count]


class LateralMovementSimulator:
    """Simulates lateral movement across a simulated network."""

    def __init__(self, session_id, context=None):
        self.session_id = session_id
        self.context = context or {}
        self.events = []

    def simulate(self):
        """Run lateral movement simulation."""
        events = []

        events.append(self._event("INFO", "Lateral movement simulation initiated"))
        time.sleep(random.uniform(0.10, 0.25))

        events.append(self._event("INFO", "Scanning simulated network for accessible hosts..."))
        time.sleep(random.uniform(0.25, 0.50))

        # Build target list from discovery context or generate fresh
        network = self.context.get("network", {})
        subnet = network.get("subnet_third", random.randint(1, 254))
        target_count = random.randint(3, 6)
        targets = _gen_targets(subnet, target_count)

        events.append(self._event("INFO", f"Discovered {len(targets)} accessible host(s)"))

        for target in targets:
            events.append(self._event(
                "INFO",
                f"  └─ {target['hostname']} ({target['ip']}) — {target['role']}",
                {"target": target}
            ))
            time.sleep(random.uniform(0.05, 0.15))

        time.sleep(random.uniform(0.10, 0.25))

        # Attempt lateral movement to 1-3 hosts
        pivot_count = random.randint(1, min(3, len(targets)))
        pivot_targets = random.sample(targets, k=pivot_count)

        for pivot_target in pivot_targets:
            fam = random.choice(_TECHNIQUE_FAMILIES)
            mitre_id = random.choice(fam["mitre_ids"])
            tech_name, protocol = random.choice(fam["details"])

            events.append(self._event(
                "INFO",
                f"Lateral movement technique: {tech_name} ({mitre_id})",
                {"technique": tech_name, "protocol": protocol, "family": fam["family"]}
            ))
            time.sleep(random.uniform(0.10, 0.25))

            events.append(self._event(
                "INFO",
                f"Attempting access to: {pivot_target['hostname']} via {protocol}",
                {"target": pivot_target["hostname"], "protocol": protocol}
            ))
            time.sleep(random.uniform(0.20, 0.50))

            success = random.random() > 0.25
            if success:
                events.append(self._event(
                    "WARNING",
                    f"Access established to {pivot_target['hostname']} ({pivot_target['ip']}) — simulation",
                    {"status": "success", "target": pivot_target}
                ))
            else:
                events.append(self._event(
                    "INFO",
                    f"Access denied to {pivot_target['hostname']} — access controls effective (simulation)",
                    {"status": "denied", "target": pivot_target}
                ))
            time.sleep(random.uniform(0.08, 0.20))

        events.append(self._event("INFO", "Lateral movement simulation complete"))
        self.events.extend(events)
        return events

    def _event(self, level, message, details=None):
        return {
            "timestamp": datetime.now().isoformat(),
            "stage": "lateral_movement",
            "level": level,
            "message": message,
            "details": details or {},
            "session_id": self.session_id,
        }
