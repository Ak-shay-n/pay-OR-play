"""
Ransomware Encryption Demonstrator
Demonstrates file encryption on DEMO FILES ONLY in a sandboxed directory.
Uses reversible encryption to show the concept without causing harm.
"""

import os
import time
import base64
import hashlib
import random
import string
from datetime import datetime
from pathlib import Path


RANSOM_NOTE = """\
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║          ⚠  It's PRIME's Ransom Notice Dear  ⚠              ║
║                                                              ║
║   This is a ransom note.                                     ║
║   Your files have been encrypted or damaged.                 ║
║                                                              ║
║   To recover your files:                                     ║
║   Send 99 Bitcoin to Legendary AK                            ║
║   BTC Address: {btc_address:<46}                             ║
║                                                              ║
║   --- SIMULATED RANSOMWARE ---                               ║
║                                                              ║
║   Files Encrypted: {file_count:<42}                          ║
║   Encryption Key:  {enc_key:<42}                             ║
║   Simulation ID:   {session_id:<42}                          ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝"""

DEMO_LOCKED_EXT = ".demo_locked"
DEMO_KEY = b"SIMULATED_DEMO_KEY_32BYTESLONG!!"  # 32 bytes for demo

_BTC_CHARS = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


def _gen_btc_address():
    """Generate a fake-looking Base58 Bitcoin address (simulation only)."""
    prefix = random.choice(["1", "3", "bc1q"])
    length = random.randint(26, 33) if prefix in ("1", "3") else random.randint(20, 28)
    body = "".join(random.choices(_BTC_CHARS, k=length))
    return prefix + body


def _gen_enc_key():
    """Generate a fake hex encryption key string (simulation only)."""
    return "".join(random.choices(string.hexdigits.upper(), k=32))


class EncryptionDemonstrator:
    """Demonstrates ransomware encryption on sandbox demo files only."""

    ALLOWED_EXTENSIONS = {".txt", ".pdf", ".docx", ".xlsx", ".csv", ".json", ".xml", ".html", ".md", ".log"}

    def __init__(self, session_id, sandbox_path):
        self.session_id = session_id
        self.sandbox_path = Path(sandbox_path)
        self.events = []
        self.encrypted_files = []
        self.btc_address = _gen_btc_address()
        self.enc_key = _gen_enc_key()

    def simulate(self):
        """Run encryption demonstration on sandbox files."""
        events = []

        if not self.sandbox_path.exists():
            events.append(self._event("ERROR", f"Sandbox directory not found: {self.sandbox_path}"))
            return events

        events.append(self._event("INFO", "Ransomware encryption demonstration initiated"))
        events.append(self._event("WARNING", "⚠ Operating ONLY on sandbox demo files — no real files affected"))
        time.sleep(0.3)

        # Scan for target files
        events.append(self._event("INFO", "Scanning sandbox directory for target files..."))
        time.sleep(0.2)

        target_files = []
        for f in self.sandbox_path.rglob("*"):
            if f.is_file() and f.suffix in self.ALLOWED_EXTENSIONS and not f.name.startswith("RANSOM_NOTE"):
                target_files.append(f)

        if not target_files:
            events.append(self._event("INFO", "No target files found in sandbox. Creating demo files..."))
            target_files = self._create_demo_files()
            time.sleep(0.2)

        events.append(self._event("INFO", f"Found {len(target_files)} file(s) to encrypt"))
        time.sleep(0.2)

        # Encrypt files
        for f in target_files:
            try:
                original_name = f.name
                encrypted_name = f.name + DEMO_LOCKED_EXT

                # Read and "encrypt" (base64 encode with marker)
                content = f.read_bytes()
                marker = b"DEMO_ENCRYPTED:"
                encrypted_content = marker + base64.b64encode(content)

                # Write encrypted file
                encrypted_path = f.parent / encrypted_name
                encrypted_path.write_bytes(encrypted_content)

                # Remove original
                f.unlink()

                self.encrypted_files.append({
                    "original": original_name,
                    "encrypted": encrypted_name,
                    "size": len(content),
                })

                events.append(self._event(
                    "WARNING",
                    f"  └─ {original_name} → {encrypted_name}",
                    {"original": original_name, "encrypted": encrypted_name, "size": len(content)}
                ))
                time.sleep(0.15)

            except Exception as e:
                events.append(self._event("ERROR", f"  └─ Failed to process {f.name}: {str(e)}"))

        # Create ransom note
        note_content = RANSOM_NOTE.format(
            file_count=len(self.encrypted_files),
            session_id=self.session_id,
            btc_address=self.btc_address,
            enc_key=self.enc_key,
        )
        note_path = self.sandbox_path / "RANSOM_NOTE_SIMULATION.txt"
        note_path.write_text(note_content, encoding="utf-8")

        events.append(self._event(
            "ALERT",
            f"Ransom note created: RANSOM_NOTE_SIMULATION.txt",
            {"ransom_note": str(note_path)}
        ))
        time.sleep(0.2)

        events.append(self._event(
            "ALERT",
            f"Encryption demonstration complete — {len(self.encrypted_files)} file(s) encrypted",
            {"encrypted_count": len(self.encrypted_files), "files": self.encrypted_files}
        ))

        # Detection alert
        events.append(self._event(
            "ALERT",
            "⚠ DETECTION: Potential ransomware activity detected — mass file modification",
            {"detection": "ransomware_behavior", "indicators": ["mass_rename", "high_entropy", "ransom_note"]}
        ))

        self.events.extend(events)
        return events

    def restore_files(self):
        """Restore demo files from encrypted state."""
        events = []
        events.append(self._event("INFO", "Restoring sandbox demo files..."))
        restored = 0

        for f in self.sandbox_path.rglob(f"*{DEMO_LOCKED_EXT}"):
            try:
                content = f.read_bytes()
                marker = b"DEMO_ENCRYPTED:"
                if content.startswith(marker):
                    original_content = base64.b64decode(content[len(marker):])
                    original_name = f.name.replace(DEMO_LOCKED_EXT, "")
                    original_path = f.parent / original_name
                    original_path.write_bytes(original_content)
                    f.unlink()
                    restored += 1
                    events.append(self._event("INFO", f"  └─ Restored: {original_name}"))
            except Exception as e:
                events.append(self._event("ERROR", f"  └─ Failed to restore {f.name}: {str(e)}"))

        # Remove ransom note
        note_path = self.sandbox_path / "RANSOM_NOTE_SIMULATION.txt"
        if note_path.exists():
            note_path.unlink()
            events.append(self._event("INFO", "  └─ Removed ransom note"))

        events.append(self._event("INFO", f"Restoration complete — {restored} file(s) restored"))
        self.events.extend(events)
        return events

    def _create_demo_files(self):
        """Create sample demo files for the sandbox."""
        demo_files_data = {
            "report.pdf": b"%%SIMULATED PDF CONTENT%% Quarterly Report Q1 2026 - Simulated Company Inc.",
            "employee_data.csv": b"Name,Department,Email\nJohn Smith,Engineering,j.smith@example.com\nJane Doe,Finance,j.doe@example.com",
            "meeting_notes.txt": b"Meeting Notes - March 2026\nTopics:\n- Project timeline\n- Budget review\n- Team updates",
            "config.json": b'{"server": "app.example.com", "port": 8080, "environment": "production"}',
            "database_schema.xml": b'<?xml version="1.0"?><schema><table name="users"><column name="id" type="int"/></table></schema>',
            "index.html": b"<html><body><h1>Simulated Internal Portal</h1><p>Company Resources</p></body></html>",
            "project_plan.md": b"# Project Plan\n## Phase 1\n- Requirements gathering\n- Design review\n## Phase 2\n- Implementation",
            "server_access.log": b"2026-03-09 08:00:01 LOGIN admin 192.168.1.100\n2026-03-09 08:15:22 ACCESS /api/users admin",
        }

        created = []
        for name, content in demo_files_data.items():
            path = self.sandbox_path / name
            path.write_bytes(content)
            created.append(path)

        return created

    def _event(self, level, message, details=None):
        return {
            "timestamp": datetime.now().isoformat(),
            "stage": "ransomware",
            "level": level,
            "message": message,
            "details": details or {},
            "session_id": self.session_id,
        }
