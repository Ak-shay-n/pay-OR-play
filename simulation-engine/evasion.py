"""
Security Evasion Simulator
Simulates techniques used to bypass security controls.
No actual security tools are modified.

Techniques and their command artefacts are assembled procedurally
from MITRE families, with randomised process targets, PIDs, and
tool-specific parameters.
"""

import time
import random
from datetime import datetime


# ── Component pools ───────────────────────────────────────────────────

_AV_PRODUCTS = [
    "Windows Defender", "CrowdStrike Falcon", "SentinelOne",
    "Sophos Endpoint", "Symantec Endpoint", "McAfee ENS",
    "ESET NOD32", "Kaspersky Endpoint", "Trend Micro Apex One",
    "Carbon Black", "Cylance", "Bitdefender GravityZone",
]

_LOG_CHANNELS = ["Security", "System", "Application", "PowerShell/Operational",
                 "Windows PowerShell", "Sysmon/Operational", "Microsoft-Windows-WMI-Activity/Operational"]

_INJECT_TARGETS = ["svchost.exe", "explorer.exe", "notepad.exe", "taskhost.exe",
                   "RuntimeBroker.exe", "SearchUI.exe", "dwm.exe", "sihost.exe"]

_FW_PROFILES = ["allprofiles", "domainprofile", "publicprofile", "privateprofile"]

_TECHNIQUE_FAMILIES = [
    {
        "family": "Impair Defenses",
        "mitre_ids": ["T1562.001", "T1562.002", "T1562.004", "T1562.006"],
        "generate": "_gen_impair_defenses",
    },
    {
        "family": "Indicator Removal",
        "mitre_ids": ["T1070.001", "T1070.003", "T1070.004", "T1070.006"],
        "generate": "_gen_indicator_removal",
    },
    {
        "family": "Process Injection",
        "mitre_ids": ["T1055.001", "T1055.002", "T1055.003", "T1055.012"],
        "generate": "_gen_process_injection",
    },
    {
        "family": "Masquerading",
        "mitre_ids": ["T1036.003", "T1036.004", "T1036.005"],
        "generate": "_gen_masquerading",
    },
    {
        "family": "Obfuscated Files/Information",
        "mitre_ids": ["T1027", "T1027.002", "T1027.004"],
        "generate": "_gen_obfuscation",
    },
    {
        "family": "Rootkit",
        "mitre_ids": ["T1014"],
        "generate": "_gen_rootkit",
    },
]


class EvasionSimulator:
    """Simulates defense evasion techniques."""

    def __init__(self, session_id, context=None):
        self.session_id = session_id
        self.context = context or {}
        self.events = []

    # ── technique generators ─────────────────────────────────────────

    def _gen_impair_defenses(self, mitre_id):
        product = random.choice(_AV_PRODUCTS)
        profile = random.choice(_FW_PROFILES)
        variants = [
            {
                "name": f"Disable {product}",
                "description": f"Simulated disabling of {product} real-time protection",
                "commands": [
                    f"Set-MpPreference -DisableRealtimeMonitoring $true (SIMULATED — {product})",
                ],
            },
            {
                "name": "Firewall Rule Modification",
                "description": f"Simulated firewall rule manipulation ({profile})",
                "commands": [
                    f"netsh advfirewall set {profile} state off (SIMULATED)",
                ],
            },
            {
                "name": f"Tamper {product} Service",
                "description": f"Simulated stopping of {product} service",
                "commands": [
                    f"sc stop \"{product}Service\" (SIMULATED)",
                ],
            },
        ]
        v = random.choice(variants)
        v["mitre_id"] = mitre_id
        return v

    def _gen_indicator_removal(self, mitre_id):
        channels = random.sample(_LOG_CHANNELS, k=random.randint(1, 3))
        variants = [
            {
                "name": "Clear Event Logs",
                "description": f"Simulated clearing of {len(channels)} Windows event log channel(s)",
                "commands": [f"wevtutil cl {ch} (SIMULATED)" for ch in channels],
            },
            {
                "name": "Timestomping",
                "description": "Simulated modification of file timestamps",
                "commands": ["Modify CreationTime, LastWriteTime, LastAccessTime (SIMULATED)"],
            },
            {
                "name": "File Deletion",
                "description": "Simulated secure-deletion of attack artefacts",
                "commands": ["cipher /w:C:\\Windows\\Temp (SIMULATED)"],
            },
        ]
        v = random.choice(variants)
        v["mitre_id"] = mitre_id
        return v

    def _gen_process_injection(self, mitre_id):
        target = random.choice(_INJECT_TARGETS)
        pid = random.randint(800, 9999)
        return {
            "name": "Process Injection",
            "mitre_id": mitre_id,
            "description": f"Simulated code injection into legitimate process",
            "commands": [f"Target: {target} PID {pid} (SIMULATED)"],
        }

    def _gen_masquerading(self, mitre_id):
        real = random.choice(["svchost.exe", "csrss.exe", "lsass.exe", "services.exe"])
        fake = real.replace(".exe", f"{random.randint(1,9)}.exe")
        return {
            "name": "Masquerading",
            "mitre_id": mitre_id,
            "description": f"Simulated binary renamed to mimic {real}",
            "commands": [f"ren payload.exe {fake} (SIMULATED)"],
        }

    def _gen_obfuscation(self, mitre_id):
        method = random.choice(["Base64", "XOR", "AES-256", "RC4"])
        return {
            "name": f"{method} Obfuscation",
            "mitre_id": mitre_id,
            "description": f"Simulated payload obfuscation using {method} encoding",
            "commands": [f"Encode payload with {method} (SIMULATED)"],
        }

    def _gen_rootkit(self, mitre_id):
        return {
            "name": "Kernel Rootkit",
            "mitre_id": mitre_id,
            "description": "Simulated rootkit hiding processes and files from OS APIs",
            "commands": ["Hook NtQuerySystemInformation (SIMULATED)"],
        }

    # ── AMSI bypass as a special case ────────────────────────────────

    def _gen_amsi_bypass(self):
        return {
            "name": "AMSI Bypass",
            "mitre_id": "T1562.001",
            "description": "Simulated AMSI (Antimalware Scan Interface) bypass",
            "commands": ["amsiutils patch (SIMULATED)"],
        }

    # ── main entry ────────────────────────────────────────────────────

    def simulate(self):
        """Run security evasion simulation."""
        events = []

        events.append(self._event("INFO", "Security evasion simulation initiated"))
        time.sleep(random.uniform(0.10, 0.25))

        count = random.randint(2, 5)
        families = random.sample(_TECHNIQUE_FAMILIES, k=min(count, len(_TECHNIQUE_FAMILIES)))

        # Optionally prepend AMSI bypass
        all_techs = []
        if random.random() < 0.4:
            all_techs.append(self._gen_amsi_bypass())

        for fam in families:
            mitre_id = random.choice(fam["mitre_ids"])
            gen_fn = getattr(self, fam["generate"])
            tech = gen_fn(mitre_id)
            if "mitre_id" not in tech:
                tech["mitre_id"] = mitre_id
            all_techs.append(tech)

        for tech in all_techs:
            events.append(self._event(
                "WARNING",
                f"Evasion technique: {tech['name']} ({tech['mitre_id']})",
                {"technique": tech["name"], "mitre_id": tech["mitre_id"]}
            ))
            time.sleep(random.uniform(0.08, 0.20))

            events.append(self._event("INFO", f"  └─ {tech['description']}"))

            for cmd in tech["commands"]:
                events.append(self._event("INFO", f"     └─ {cmd}"))
                time.sleep(random.uniform(0.05, 0.15))

            events.append(self._event(
                "ALERT",
                f"Security service evasion attempt detected: {tech['name']}",
                {"detection": True, "technique": tech["name"]}
            ))
            time.sleep(random.uniform(0.10, 0.25))

        events.append(self._event("INFO", f"Security evasion simulation complete — {len(all_techs)} technique(s)"))
        self.events.extend(events)
        return events

    def _event(self, level, message, details=None):
        return {
            "timestamp": datetime.now().isoformat(),
            "stage": "evasion",
            "level": level,
            "message": message,
            "details": details or {},
            "session_id": self.session_id,
        }
