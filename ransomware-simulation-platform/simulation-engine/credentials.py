"""
Credential Access Simulator
Simulates credential harvesting techniques.
No real credentials are accessed or stored.

All outputs are procedurally generated from context — nothing is hardcoded.
"""

import time
import random
import hashlib
import string
from datetime import datetime, timedelta


# ── Building blocks for procedural generation ─────────────────────────

_CRED_TYPES = [
    ("NTLM Hash", "SAM Database"),
    ("Kerberos TGT", "LSASS Memory"),
    ("Cached Domain", "Registry Cache"),
    ("Browser Password", "{browser} Password Store"),
    ("RDP Credential", "Credential Manager"),
    ("SSH Key", "User Profile .ssh"),
    ("API Token", "Environment Variables"),
    ("OAuth Token", "{browser} Cookie Store"),
    ("VPN Certificate", "VPN Client Config"),
    ("Wi-Fi PSK", "Wireless Profile Store"),
]

_BROWSERS = ["Chrome", "Firefox", "Edge", "Brave", "Opera"]

_TECHNIQUE_FAMILIES = [
    {"base": "OS Credential Dumping", "sub_ids": ["T1003.001", "T1003.002", "T1003.003", "T1003.004", "T1003.005", "T1003.006"]},
    {"base": "Credentials from Password Stores", "sub_ids": ["T1555.001", "T1555.003", "T1555.004", "T1555.005"]},
    {"base": "Input Capture", "sub_ids": ["T1056.001", "T1056.002", "T1056.004"]},
    {"base": "Steal or Forge Kerberos Tickets", "sub_ids": ["T1558.001", "T1558.003"]},
    {"base": "Unsecured Credentials", "sub_ids": ["T1552.001", "T1552.002", "T1552.004", "T1552.006"]},
]

_TECHNIQUE_DETAILS = {
    "T1003.001": ("LSASS Memory Dump", "memory dump of LSASS process"),
    "T1003.002": ("SAM Database Extraction", "local SAM database extraction"),
    "T1003.003": ("NTDS.dit Extraction", "domain controller NTDS.dit extraction"),
    "T1003.004": ("LSA Secrets", "LSA secret extraction from registry"),
    "T1003.005": ("Cached Domain Credentials", "cached logon credential extraction"),
    "T1003.006": ("DCSync", "domain replication request via DCSync"),
    "T1555.001": ("Keychain", "macOS Keychain credential extraction"),
    "T1555.003": ("Browser Credential Store", "browser password store access"),
    "T1555.004": ("Windows Credential Manager", "Windows Credential Manager dump"),
    "T1555.005": ("Password Manager", "third-party password manager extraction"),
    "T1056.001": ("Keylogging", "keylogger deployment for credential capture"),
    "T1056.002": ("GUI Input Capture", "GUI-level input interception"),
    "T1056.004": ("Web Portal Capture", "credential capture via cloned portal"),
    "T1558.001": ("Golden Ticket", "Kerberos golden ticket creation"),
    "T1558.003": ("Kerberoasting", "service ticket request for offline cracking"),
    "T1552.001": ("Credentials in Files", "plaintext credential search in files"),
    "T1552.002": ("Credentials in Registry", "credential extraction from registry"),
    "T1552.004": ("Private Keys", "private key file extraction"),
    "T1552.006": ("Group Policy Preferences", "GPP password extraction"),
}


def _fake_hash(seed: str) -> str:
    """Generate a deterministic but random-looking hash from a seed."""
    h = hashlib.md5(seed.encode()).hexdigest()
    return f"aad3b435b51404ee:{h[:16].upper()}"


def _fake_ticket(length: int = 24) -> str:
    chars = string.ascii_uppercase + string.digits
    return "SIMTKT_" + "".join(random.choices(chars, k=length))


class CredentialSimulator:
    """Simulates credential access techniques used in ransomware campaigns."""

    def __init__(self, session_id, context=None):
        self.session_id = session_id
        self.context = context or {}
        self.events = []

    # ── generators ────────────────────────────────────────────────────

    def _generate_techniques(self):
        """Build a randomised set of techniques from MITRE families."""
        count = random.randint(2, 5)
        picked = []
        families = random.sample(_TECHNIQUE_FAMILIES, k=min(count, len(_TECHNIQUE_FAMILIES)))
        for fam in families:
            tid = random.choice(fam["sub_ids"])
            name, desc = _TECHNIQUE_DETAILS.get(tid, (fam["base"], fam["base"].lower()))
            picked.append({
                "name": name,
                "mitre_id": tid,
                "family": fam["base"],
                "description": f"Simulated {desc}",
            })
        return picked[:count]

    def _generate_credentials(self, users):
        """Build credential artifacts from discovered users (or random ones)."""
        if not users:
            # Fallback – generate plausible usernames
            firsts = ["alice", "bob", "carol", "dave", "eve", "frank", "grace", "hank"]
            lasts = ["adams", "baker", "clark", "diaz", "evans", "ford", "grant", "hill"]
            users = [
                {"username": f"{random.choice(firsts)[0]}.{random.choice(lasts)}"}
                for _ in range(random.randint(3, 6))
            ]

        count = random.randint(2, min(len(users), 5))
        targets = random.sample(users, k=count)
        browser = random.choice(_BROWSERS)

        creds = []
        for u in targets:
            uname = u.get("username", u.get("user", "unknown"))
            ctype, source = random.choice(_CRED_TYPES)
            source = source.format(browser=browser)

            # Generate a plausible-looking value per type
            if "Hash" in ctype:
                value = _fake_hash(f"{self.session_id}-{uname}")
            elif "Ticket" in ctype or "Token" in ctype:
                value = _fake_ticket()
            elif "Key" in ctype or "Certificate" in ctype:
                value = "***SIMULATED_KEY_DATA***"
            else:
                value = "***SIMULATED***"

            creds.append({
                "type": ctype,
                "user": uname,
                "value": value,
                "source": source,
            })
        return creds

    # ── main entry ────────────────────────────────────────────────────

    def simulate(self):
        """Run credential access simulation."""
        events = []

        events.append(self._event("INFO", "Credential access simulation initiated"))
        time.sleep(random.uniform(0.15, 0.30))

        # Derive user list from earlier discovery stage if available
        discovered_users = self.context.get("users", [])
        techniques = self._generate_techniques()
        creds = self._generate_credentials(discovered_users)

        for tech in techniques:
            events.append(self._event(
                "INFO",
                f"Technique: {tech['name']} ({tech['mitre_id']})",
                {"technique": tech["name"], "mitre_id": tech["mitre_id"], "family": tech["family"]}
            ))
            events.append(self._event("INFO", f"  └─ {tech['description']}"))
            time.sleep(random.uniform(0.10, 0.25))

        events.append(self._event("INFO", f"[SIMULATION] {len(creds)} credential artifact(s) discovered"))
        time.sleep(random.uniform(0.05, 0.15))

        for cred in creds:
            events.append(self._event(
                "SIMULATION",
                f"  └─ {cred['type']}: {cred['user']} from {cred['source']}",
                {"credential_type": cred["type"], "user": cred["user"], "source": cred["source"]}
            ))
            time.sleep(random.uniform(0.05, 0.15))

        events.append(self._event(
            "WARNING",
            "NOTE: No real credentials were collected — all data is simulated",
            {"simulation_notice": True}
        ))

        events.append(self._event("INFO", "Credential access simulation complete"))
        self.events.extend(events)
        return events

    def _event(self, level, message, details=None):
        return {
            "timestamp": datetime.now().isoformat(),
            "stage": "credentials",
            "level": level,
            "message": message,
            "details": details or {},
            "session_id": self.session_id,
        }
