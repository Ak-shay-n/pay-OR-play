"""
Attack Simulation Controller
Orchestrates all simulation stages and provides the main API.

Discovery data gathered in the 'discovery' stage is forwarded as
context to every downstream simulator so that credentials, lateral
movement, exfiltration, etc. refer to the same procedurally-generated
environment.
"""

import uuid
import time
import random
from datetime import datetime
from pathlib import Path

from .initial_access import InitialAccessSimulator
from .persistence import PersistenceSimulator
from .discovery import DiscoverySimulator
from .credentials import CredentialSimulator
from .privilege_escalation import PrivilegeEscalationSimulator
from .lateral_movement import LateralMovementSimulator
from .evasion import EvasionSimulator
from .exfiltration import ExfiltrationSimulator
from .encryption_demo import EncryptionDemonstrator
from .monitoring import FileActivityMonitor, ProcessMonitor, DetectionEngine


# ── tiny helpers for procedural session metadata ─────────────────────
_HOST_PREFIXES = ["WS", "PC", "DT", "LT", "VM", "DEV", "ENG", "FIN"]
_OS_POOL = [
    "Windows 10 Enterprise", "Windows 10 Pro", "Windows 11 Enterprise",
    "Windows 11 Pro", "Windows Server 2022", "Windows Server 2019",
]


class AttackSimulationController:
    """Main controller that orchestrates the attack simulation lifecycle."""

    STAGES = [
        "initial_access",
        "persistence",
        "discovery",
        "credentials",
        "privilege_escalation",
        "lateral_movement",
        "evasion",
        "exfiltration",
        "ransomware",
    ]

    def __init__(self, sandbox_path):
        self.sandbox_path = Path(sandbox_path)
        self.sandbox_path.mkdir(parents=True, exist_ok=True)

        self.sessions = {}
        self.file_monitor = FileActivityMonitor(sandbox_path)
        self.process_monitor = ProcessMonitor()
        self.detection_engine = DetectionEngine()

    def create_session(self):
        """Create a new attack simulation session."""
        session_id = str(uuid.uuid4())[:8]
        subnet_third = random.randint(1, 254)
        host_num = random.randint(100, 254)
        self.sessions[session_id] = {
            "id": session_id,
            "created": datetime.now().isoformat(),
            "status": "active",
            "current_stage": None,
            "completed_stages": [],
            "events": [],
            "target": {
                "ip": f"192.168.{subnet_third}.{host_num}",
                "hostname": f"{random.choice(_HOST_PREFIXES)}-{session_id.upper()}",
                "user": "victim",
                "os": random.choice(_OS_POOL),
            },
            "discovery_data": None,
        }
        return self.sessions[session_id]

    def get_session(self, session_id):
        return self.sessions.get(session_id)

    def get_all_sessions(self):
        return list(self.sessions.values())

    # ── context builder ──────────────────────────────────────────────

    def _build_context(self, session):
        """Build a context dict from discovery data for downstream simulators."""
        dd = session.get("discovery_data") or {}
        return {
            "users": dd.get("users", []),
            "network": dd.get("network", {}),
            "software": dd.get("software", []),
            "shares": dd.get("shares", []),
            "target": session.get("target", {}),
        }

    # ── stage execution ──────────────────────────────────────────────

    def run_stage(self, session_id, stage):
        """Run a specific attack stage."""
        session = self.sessions.get(session_id)
        if not session:
            return {"error": f"Session {session_id} not found"}

        if stage not in self.STAGES:
            return {"error": f"Unknown stage: {stage}"}

        session["current_stage"] = stage
        session["status"] = "running"

        # Take file snapshot before simulation
        self.file_monitor.take_snapshot()

        events = self._execute_stage(session_id, stage)

        session["events"].extend(events)
        session["completed_stages"].append(stage)
        session["current_stage"] = None
        session["status"] = "active"

        # Check for file changes after simulation
        file_changes = self.file_monitor.detect_changes()
        events.extend(file_changes)

        # Run detection analysis
        alerts = self.detection_engine.analyze_events(events)

        return {
            "session_id": session_id,
            "stage": stage,
            "events": events,
            "alerts": alerts,
            "file_changes": file_changes,
        }

    def run_full_lifecycle(self, session_id):
        """Run all attack stages in sequence."""
        results = []
        for stage in self.STAGES:
            result = self.run_stage(session_id, stage)
            results.append(result)
            time.sleep(random.uniform(0.15, 0.40))
        return results

    def restore_sandbox(self, session_id):
        """Restore sandbox files after encryption demo."""
        enc = EncryptionDemonstrator(session_id, self.sandbox_path)
        return enc.restore_files()

    def get_monitoring_data(self):
        """Get current monitoring data."""
        return {
            "files": self.file_monitor.get_file_list(),
            "processes": self.process_monitor.get_process_list(),
            "alerts": self.detection_engine.get_alerts(),
            "rules": self.detection_engine.get_rules(),
        }

    def _execute_stage(self, session_id, stage):
        """Execute a specific simulation stage, forwarding context where available."""
        session = self.sessions.get(session_id, {})
        ctx = self._build_context(session)

        if stage == "initial_access":
            sim = InitialAccessSimulator()
            return sim.simulate_phishing_email()

        elif stage == "persistence":
            sim = PersistenceSimulator(session_id, context=ctx)
            return sim.simulate()

        elif stage == "discovery":
            sim = DiscoverySimulator(session_id, context=ctx)
            events = sim.simulate()
            if session:
                session["discovery_data"] = sim.get_discovery_data()
            return events

        elif stage == "credentials":
            sim = CredentialSimulator(session_id, context=ctx)
            return sim.simulate()

        elif stage == "privilege_escalation":
            sim = PrivilegeEscalationSimulator(session_id, context=ctx)
            return sim.simulate()

        elif stage == "lateral_movement":
            sim = LateralMovementSimulator(session_id, context=ctx)
            return sim.simulate()

        elif stage == "evasion":
            sim = EvasionSimulator(session_id, context=ctx)
            return sim.simulate()

        elif stage == "exfiltration":
            sim = ExfiltrationSimulator(session_id, context=ctx)
            return sim.simulate()

        elif stage == "ransomware":
            self.process_monitor.set_attack_active(True)
            sim = EncryptionDemonstrator(session_id, self.sandbox_path)
            return sim.simulate()

        return []
