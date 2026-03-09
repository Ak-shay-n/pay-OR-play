"""
Persistence Simulator
Simulates techniques attackers use to maintain access.
All operations are simulated — no actual system changes are made.

Techniques, paths, and artefact names are assembled procedurally
from component pools. No two simulation runs produce identical output.
"""

import time
import random
import string
from datetime import datetime


# ── Component pools ───────────────────────────────────────────────────

_SERVICE_STEMS = [
    "Update", "Health", "Sync", "Helper", "Manager", "Monitor",
    "Agent", "Worker", "Scheduler", "Bridge", "Daemon", "Indexer",
]
_SERVICE_PREFIXES = [
    "Windows", "System", "Security", "Microsoft", "Network", "Runtime",
]

_TASK_INTERVALS = [5, 10, 15, 30, 60]  # minutes

_REG_RUN_PATHS = [
    r"HKCU\Software\Microsoft\Windows\CurrentVersion\Run",
    r"HKLM\Software\Microsoft\Windows\CurrentVersion\Run",
    r"HKCU\Software\Microsoft\Windows\CurrentVersion\RunOnce",
    r"HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce",
]

_STARTUP_DIRS = [
    r"C:\Users\{user}\AppData\Roaming\Microsoft\Windows\Start Menu\Startup",
    r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs\StartUp",
]

_LNK_NAMES = ["{stem}.lnk", "{stem}_loader.lnk", "{stem}.url"]

_TECHNIQUE_DEFS = [
    {
        "family": "Boot/Logon Auto-Start",
        "mitre_ids": ["T1547.001", "T1547.004", "T1547.005", "T1547.009"],
        "generate": "_gen_registry_run",
    },
    {
        "family": "Scheduled Task",
        "mitre_ids": ["T1053.005"],
        "generate": "_gen_scheduled_task",
    },
    {
        "family": "Startup Folder",
        "mitre_ids": ["T1547.001"],
        "generate": "_gen_startup_folder",
    },
    {
        "family": "WMI Event Subscription",
        "mitre_ids": ["T1546.003"],
        "generate": "_gen_wmi_persistence",
    },
    {
        "family": "Service Installation",
        "mitre_ids": ["T1543.003"],
        "generate": "_gen_service_install",
    },
    {
        "family": "DLL Search-Order Hijack",
        "mitre_ids": ["T1574.001"],
        "generate": "_gen_dll_hijack",
    },
    {
        "family": "Registry Modification",
        "mitre_ids": ["T1112"],
        "generate": "_gen_registry_mod",
    },
]


def _rand_name():
    prefix = random.choice(_SERVICE_PREFIXES)
    stem = random.choice(_SERVICE_STEMS)
    return f"{prefix}{stem}"


class PersistenceSimulator:
    """Simulates persistence mechanisms used by ransomware operators."""

    def __init__(self, session_id, context=None):
        self.session_id = session_id
        self.context = context or {}
        self.events = []

    # ── technique generators ─────────────────────────────────────────

    def _gen_registry_run(self, mitre_id):
        name = _rand_name()
        path = random.choice(_REG_RUN_PATHS)
        return {
            "name": "Registry Run Key",
            "mitre_id": mitre_id,
            "description": "Simulated registry modification for auto-start",
            "detail": f"{path} → '{name}'",
        }

    def _gen_scheduled_task(self, mitre_id):
        name = _rand_name()
        interval = random.choice(_TASK_INTERVALS)
        return {
            "name": "Scheduled Task",
            "mitre_id": mitre_id,
            "description": "Simulated scheduled task creation",
            "detail": f"Task: '{name}' → runs every {interval} minutes",
        }

    def _gen_startup_folder(self, mitre_id):
        user = self._pick_user()
        stem = _rand_name().lower()
        lnk = random.choice(_LNK_NAMES).format(stem=stem)
        folder = random.choice(_STARTUP_DIRS).format(user=user)
        return {
            "name": "Startup Folder",
            "mitre_id": mitre_id,
            "description": "Simulated shortcut placed in startup folder",
            "detail": f"{folder}\\{lnk}",
        }

    def _gen_wmi_persistence(self, mitre_id):
        filter_name = _rand_name() + "Filter"
        return {
            "name": "WMI Event Subscription",
            "mitre_id": mitre_id,
            "description": "Simulated WMI persistence",
            "detail": f"EventFilter: '{filter_name}' → CommandLineEventConsumer",
        }

    def _gen_service_install(self, mitre_id):
        svc = _rand_name()
        return {
            "name": "Service Installation",
            "mitre_id": mitre_id,
            "description": "Simulated malicious service installation",
            "detail": f"Service: '{svc}' → Auto-start",
        }

    def _gen_dll_hijack(self, mitre_id):
        dll = _rand_name().lower() + ".dll"
        host = random.choice(["explorer.exe", "svchost.exe", "services.exe", "taskhost.exe"])
        return {
            "name": "DLL Search-Order Hijack",
            "mitre_id": mitre_id,
            "description": "Simulated DLL placed in search path of legitimate host",
            "detail": f"{dll} targeting {host}",
        }

    def _gen_registry_mod(self, mitre_id):
        name = _rand_name()
        return {
            "name": "Registry Key Modification",
            "mitre_id": mitre_id,
            "description": "Simulated registry modification for persistence",
            "detail": f"HKLM\\SYSTEM\\CurrentControlSet\\Services\\{name}",
        }

    def _pick_user(self):
        users = self.context.get("users", [])
        if users:
            u = random.choice(users)
            return u.get("username", u.get("user", "victim"))
        return "victim"

    # ── main entry ────────────────────────────────────────────────────

    def simulate(self):
        """Run persistence simulation with procedurally generated techniques."""
        events = []
        count = random.randint(2, 4)
        defs = random.sample(_TECHNIQUE_DEFS, k=min(count, len(_TECHNIQUE_DEFS)))

        events.append(self._event("INFO", "Persistence simulation initiated"))
        time.sleep(random.uniform(0.10, 0.25))

        for d in defs:
            mitre_id = random.choice(d["mitre_ids"])
            gen_fn = getattr(self, d["generate"])
            tech = gen_fn(mitre_id)

            events.append(self._event(
                "INFO",
                f"Persistence mechanism simulated: {tech['name']} ({tech['mitre_id']})",
                {
                    "technique": tech["name"],
                    "mitre_id": tech["mitre_id"],
                    "detail": tech["detail"],
                    "family": d["family"],
                }
            ))
            time.sleep(random.uniform(0.10, 0.25))

            events.append(self._event(
                "INFO",
                f"  └─ {tech['description']}: {tech['detail']}",
                {"action": "persistence_established"}
            ))
            time.sleep(random.uniform(0.08, 0.20))

        events.append(self._event(
            "INFO",
            f"Persistence simulation complete — {len(defs)} technique(s) demonstrated",
            {"techniques_count": len(defs)}
        ))

        self.events.extend(events)
        return events

    def _event(self, level, message, details=None):
        return {
            "timestamp": datetime.now().isoformat(),
            "stage": "persistence",
            "level": level,
            "message": message,
            "details": details or {},
            "session_id": self.session_id,
        }
