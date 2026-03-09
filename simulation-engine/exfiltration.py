"""
Data Exfiltration Simulator
Simulates data staging and exfiltration techniques.
No actual data is exfiltrated.

Files, sizes, and exfiltration channels are assembled procedurally
from component pools and optional discovery context.
"""

import time
import random
from datetime import datetime


# ── Component pools ─────────────────────────────────────────────────

_FILE_CATEGORIES = {
    "Financial":              {"stems": ["Financial_Report", "Revenue_Summary", "Budget_FY", "Expense_Audit"],
                               "exts": [".xlsx", ".csv", ".pdf"], "size_range": (0.5, 25)},
    "PII":                    {"stems": ["Employee_Records", "HR_Directory", "Payroll_Data", "SSN_Export"],
                               "exts": [".csv", ".xlsx", ".json"], "size_range": (0.2, 12)},
    "Intellectual Property":  {"stems": ["source_code", "product_design", "firmware_v", "algo_spec"],
                               "exts": [".zip", ".tar.gz", ".7z"], "size_range": (5, 120)},
    "Legal":                  {"stems": ["Client_Contracts", "NDA_Pack", "Litigation_Docs", "Compliance_Report"],
                               "exts": [".pdf", ".docx"], "size_range": (1, 30)},
    "Credentials":            {"stems": ["Passwords", "Vault_Export", "CertBundle", "API_Keys"],
                               "exts": [".kdbx", ".p12", ".json", ".env"], "size_range": (0.01, 0.5)},
    "Database":               {"stems": ["database_backup", "customer_db", "orders_export", "analytics_dump"],
                               "exts": [".sql", ".bak", ".sqlite"], "size_range": (50, 500)},
    "Strategy":               {"stems": ["Strategic_Plan", "M_A_Brief", "Board_Deck", "Roadmap"],
                               "exts": [".pptx", ".pdf", ".docx"], "size_range": (1, 15)},
}

_QUARTERS = ["Q1", "Q2", "Q3", "Q4"]

_BASE_DIRS = [
    "C:\\Users\\{user}\\Documents",
    "C:\\Users\\{user}\\Desktop",
    "C:\\Projects",
    "C:\\Backups",
    "C:\\Shares\\{dept}",
]

_DEPARTMENTS = ["Finance", "Engineering", "HR", "Legal", "Marketing", "Operations"]

_EXFIL_METHODS = [
    {"method": "HTTPS POST",       "protocol": "HTTPS", "dest_tpl": "https://{host}/upload"},
    {"method": "DNS Tunneling",    "protocol": "DNS",   "dest_tpl": "data.{host}"},
    {"method": "Cloud Storage",    "protocol": "HTTPS", "dest_tpl": "{bucket}.cloud-storage.example.com"},
    {"method": "FTP Upload",       "protocol": "FTP",   "dest_tpl": "ftp://{host}"},
    {"method": "Encrypted Archive","protocol": "Local", "dest_tpl": "Staged locally for manual extraction"},
    {"method": "ICMP Tunnel",      "protocol": "ICMP",  "dest_tpl": "{host}"},
    {"method": "WebSocket",        "protocol": "WSS",   "dest_tpl": "wss://{host}/stream"},
]

_C2_WORDS = ["shadow", "cobalt", "nimbus", "delta", "apex", "relay", "orbit", "signal"]
_C2_TLDS = [".example.com", ".example.net", ".example.org"]


class ExfiltrationSimulator:
    """Simulates data exfiltration techniques."""

    def __init__(self, session_id, context=None):
        self.session_id = session_id
        self.context = context or {}
        self.events = []

    # ── generators ────────────────────────────────────────────────────

    def _pick_user(self):
        """Return a username from context or generate one."""
        users = self.context.get("users", [])
        if users:
            names = [u.get("username") or u.get("name", "victim") for u in users
                     if u.get("type") != "service"]
            if names:
                return random.choice(names)
        return "victim"

    def _gen_file(self, category):
        info = _FILE_CATEGORIES[category]
        stem = random.choice(info["stems"])
        ext = random.choice(info["exts"])
        suffix = ""
        if random.random() < 0.4:
            suffix = f"_{random.choice(_QUARTERS)}_{random.randint(2023, 2026)}"
        user = self._pick_user()
        dept = random.choice(_DEPARTMENTS)
        base = random.choice(_BASE_DIRS).format(user=user, dept=dept)
        size_val = round(random.uniform(*info["size_range"]), 1)
        unit = "KB" if size_val < 1 else "MB"
        if unit == "KB":
            size_val = round(size_val * 1024, 0)
        return {
            "path": f"{base}\\{stem}{suffix}{ext}",
            "size": f"{size_val} {unit}",
            "size_mb": size_val if unit == "MB" else size_val / 1024,
            "category": category,
        }

    def _gen_channel(self):
        tpl = random.choice(_EXFIL_METHODS)
        word = random.choice(_C2_WORDS)
        seq = random.randint(10, 99)
        host = f"{word}{seq}{random.choice(_C2_TLDS)}"
        bucket = f"simulated-{word}-{seq}"
        dest = tpl["dest_tpl"].format(host=host, bucket=bucket)
        return {
            "method": tpl["method"],
            "protocol": tpl["protocol"],
            "destination": dest,
        }

    # ── main entry ────────────────────────────────────────────────────

    def simulate(self):
        """Run data exfiltration simulation."""
        events = []

        events.append(self._event("INFO", "Data exfiltration simulation initiated"))
        time.sleep(random.uniform(0.10, 0.25))

        # Stage 1: File discovery
        events.append(self._event("INFO", "Scanning for sensitive files..."))
        time.sleep(random.uniform(0.15, 0.35))

        count = random.randint(3, 6)
        categories = random.sample(list(_FILE_CATEGORIES.keys()), k=min(count, len(_FILE_CATEGORIES)))
        files = [self._gen_file(cat) for cat in categories]
        total_mb = 0.0

        for f in files:
            total_mb += f["size_mb"]
            events.append(self._event(
                "INFO",
                f"  └─ [{f['category']}] {f['path']} ({f['size']})",
                {"file": f}
            ))
            time.sleep(random.uniform(0.05, 0.12))

        events.append(self._event(
            "INFO",
            f"Identified {len(files)} sensitive file(s) for staging",
            {"file_count": len(files)}
        ))
        time.sleep(random.uniform(0.10, 0.25))

        # Stage 2: Data staging
        archive_name = f"staged_{random.randint(1000,9999)}.7z"
        events.append(self._event("INFO", "Staging data for exfiltration (simulated compression)..."))
        time.sleep(random.uniform(0.15, 0.35))
        events.append(self._event("INFO", f"  └─ Created archive: {archive_name} ({total_mb:.1f} MB compressed)"))
        time.sleep(random.uniform(0.10, 0.25))

        # Stage 3: Exfiltration — may use 1‑2 channels
        num_channels = 1 if random.random() < 0.7 else 2
        for _ in range(num_channels):
            channel = self._gen_channel()
            events.append(self._event(
                "WARNING",
                f"Exfiltration channel: {channel['method']} via {channel['protocol']}",
                {"channel": channel}
            ))
            time.sleep(random.uniform(0.10, 0.20))

            events.append(self._event(
                "WARNING",
                f"Simulated data exfiltration to: {channel['destination']}",
                {"destination": channel["destination"], "simulated": True}
            ))
            time.sleep(random.uniform(0.15, 0.30))

        events.append(self._event(
            "ALERT",
            f"Unusual outbound data transfer detected — {total_mb:.1f} MB via {channel['protocol']}",
            {"alert_type": "data_exfiltration", "size_mb": round(total_mb, 1)}
        ))

        events.append(self._event("INFO", "Data exfiltration simulation complete"))
        self.events.extend(events)
        return events

    def _event(self, level, message, details=None):
        return {
            "timestamp": datetime.now().isoformat(),
            "stage": "exfiltration",
            "level": level,
            "message": message,
            "details": details or {},
            "session_id": self.session_id,
        }
