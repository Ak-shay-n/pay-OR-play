"""
Privilege Escalation Simulator
Simulates techniques used to gain elevated privileges.
No actual privilege changes are made.

Techniques are composed procedurally from MITRE families, with
dynamic from/to privilege levels and contextual artefact details.
"""

import time
import random
from datetime import datetime


# ── Component pools ───────────────────────────────────────────────────

_PRIV_LEVELS = ["Standard User", "User", "Power User", "Administrator", "SYSTEM", "Domain Admin"]

_TECHNIQUE_FAMILIES = [
    {
        "family": "Access Token Manipulation",
        "mitre_ids": ["T1134.001", "T1134.002", "T1134.003", "T1134.005"],
        "templates": [
            ("Token Impersonation", "token duplication for {to_level} privileges"),
            ("Token Theft", "stolen access token from privileged process"),
            ("Create Process with Token", "spawned process with stolen {to_level} token"),
        ],
    },
    {
        "family": "Abuse Elevation Control",
        "mitre_ids": ["T1548.002", "T1548.003", "T1548.004"],
        "templates": [
            ("UAC Bypass via {binary}", "bypass of User Account Control"),
            ("Sudo Caching Exploit", "leveraged cached sudo credentials"),
        ],
    },
    {
        "family": "Exploitation for Privilege Escalation",
        "mitre_ids": ["T1068"],
        "templates": [
            ("Kernel Exploit", "exploited {cve} for kernel-level access"),
            ("Local Privilege Exploit", "leveraged {cve} in local service"),
        ],
    },
    {
        "family": "Create or Modify System Process",
        "mitre_ids": ["T1543.003", "T1543.002"],
        "templates": [
            ("Service Exploit", "exploitation of misconfigured service '{svc_name}'"),
            ("Systemd Unit Override", "overrode systemd unit for code execution as root"),
        ],
    },
    {
        "family": "Hijack Execution Flow",
        "mitre_ids": ["T1574.001", "T1574.002", "T1574.009"],
        "templates": [
            ("DLL Side-Loading", "DLL hijacking of privileged process '{binary}'"),
            ("Unquoted Service Path", "exploitation of unquoted path in service '{svc_name}'"),
            ("Path Interception", "binary planted in search path before legitimate '{binary}'"),
        ],
    },
    {
        "family": "Process Injection",
        "mitre_ids": ["T1055.001", "T1055.003", "T1055.012"],
        "templates": [
            ("DLL Injection", "DLL injection into {binary} (PID {pid})"),
            ("Thread Execution Hijack", "hijacked thread in {binary} for privilege context"),
            ("Process Hollowing", "hollowed {binary} and replaced with payload"),
        ],
    },
    {
        "family": "Valid Accounts",
        "mitre_ids": ["T1078.002", "T1078.003"],
        "templates": [
            ("Cached Domain Admin Creds", "used cached domain admin credentials"),
            ("Local Admin Account", "leveraged local admin account '{user}'"),
        ],
    },
]

_UAC_BINARIES = ["fodhelper.exe", "eventvwr.exe", "sdclt.exe", "computerdefaults.exe", "slui.exe"]
_PRIV_BINARIES = ["svchost.exe", "spoolsv.exe", "lsass.exe", "services.exe", "winlogon.exe", "taskhost.exe"]
_SVC_STEMS = ["Update", "Health", "Backup", "Print", "Telemetry", "Indexer", "Logger"]
_SVC_PREFIXES = ["Windows", "System", "Microsoft", "Network"]


class PrivilegeEscalationSimulator:
    """Simulates privilege escalation techniques."""

    def __init__(self, session_id, context=None):
        self.session_id = session_id
        self.context = context or {}
        self.events = []

    def _pick_user(self):
        users = self.context.get("users", [])
        if users:
            u = random.choice(users)
            return u.get("username", u.get("user", "victim"))
        return "victim"

    def simulate(self):
        """Run privilege escalation simulation."""
        events = []

        # Choose 1-3 techniques
        count = random.randint(1, 3)
        families = random.sample(_TECHNIQUE_FAMILIES, k=min(count, len(_TECHNIQUE_FAMILIES)))

        events.append(self._event("INFO", "Privilege escalation simulation initiated"))
        time.sleep(random.uniform(0.10, 0.25))

        for fam in families:
            mitre_id = random.choice(fam["mitre_ids"])
            name, desc_template = random.choice(fam["templates"])

            # Determine from/to levels – ensure escalation direction
            from_idx = random.randint(0, len(_PRIV_LEVELS) - 3)
            to_idx = random.randint(from_idx + 1, len(_PRIV_LEVELS) - 1)
            from_level = _PRIV_LEVELS[from_idx]
            to_level = _PRIV_LEVELS[to_idx]

            # Fill template placeholders
            cve = f"CVE-{random.randint(2023, 2026)}-{random.randint(10000, 99999)}"
            binary = random.choice(_UAC_BINARIES if "UAC" in name else _PRIV_BINARIES)
            svc_name = f"{random.choice(_SVC_PREFIXES)}{random.choice(_SVC_STEMS)}"
            pid = random.randint(800, 9999)
            user = self._pick_user()

            name = name.format(binary=binary, svc_name=svc_name, user=user)
            description = f"Simulated {desc_template.format(to_level=to_level, cve=cve, binary=binary, svc_name=svc_name, pid=pid, user=user)}"

            events.append(self._event(
                "INFO",
                f"Current privilege level: {from_level}",
                {"current_level": from_level}
            ))
            time.sleep(random.uniform(0.10, 0.25))

            events.append(self._event(
                "INFO",
                f"Escalation technique: {name} ({mitre_id})",
                {"technique": name, "mitre_id": mitre_id, "family": fam["family"]}
            ))
            time.sleep(random.uniform(0.10, 0.25))

            events.append(self._event("INFO", f"  └─ {description}"))
            time.sleep(random.uniform(0.15, 0.35))

            success = random.random() > 0.15  # ~85 % success rate
            if success:
                events.append(self._event(
                    "WARNING",
                    f"Privilege level elevated: {from_level} → {to_level} (simulation)",
                    {"from": from_level, "to": to_level, "simulated": True}
                ))
            else:
                events.append(self._event(
                    "INFO",
                    f"Escalation attempt blocked: {name} — defense effective (simulation)",
                    {"from": from_level, "to": to_level, "blocked": True, "simulated": True}
                ))
            time.sleep(random.uniform(0.10, 0.25))

        events.append(self._event("INFO", "Privilege escalation simulation complete"))
        self.events.extend(events)
        return events

    def _event(self, level, message, details=None):
        return {
            "timestamp": datetime.now().isoformat(),
            "stage": "privilege_escalation",
            "level": level,
            "message": message,
            "details": details or {},
            "session_id": self.session_id,
        }
