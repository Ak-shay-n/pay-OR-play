"""
Initial Access Simulator
Simulates phishing and initial payload delivery scenarios.
No real payloads are executed.

All phishing scenarios and exploit vectors are procedurally assembled
from component pools at runtime — no two runs are identical.
"""

import time
import random
import uuid
from datetime import datetime


# ── Component pools for procedural generation ─────────────────────────

_SUBJECT_PATTERNS = [
    "Invoice #{inv_id}",
    "Urgent: {action} Required",
    "Shared Document - {doc_name}",
    "Job Application - {role}",
    "Delivery Notification #{inv_id}",
    "RE: {doc_name} — Review Needed",
    "Security Alert: {action} Immediately",
    "Meeting Update: {doc_name}",
    "Payment Confirmation #{inv_id}",
    "Action Required: {action} by EOD",
    "Confidential: {doc_name}",
    "Your {service} Subscription",
]

_ACTIONS = ["Password Reset", "Account Verification", "Approve Payment",
            "Update Credentials", "Confirm Identity", "Review Access",
            "Renew License", "Validate Settings"]

_DOC_NAMES = ["Q1 Report", "Budget Review", "Project Status", "Annual Plan",
              "Performance Review", "Client Brief", "Compliance Audit",
              "Strategy Deck", "Board Minutes", "Sales Forecast"]

_ROLES = ["Senior Developer", "Data Analyst", "Project Manager",
          "HR Specialist", "Marketing Lead", "Finance Analyst"]

_SERVICES = ["Microsoft 365", "Google Workspace", "Slack", "Zoom",
             "AWS Console", "Adobe Creative Cloud"]

_ATTACHMENT_TEMPLATES = [
    "{stem}.pdf.exe",
    "{stem}.docm",
    "{stem}.doc",
    "{stem}.xlsm",
    "{stem}.js",
    "{stem}.hta",
    "{stem}.iso",
    "{stem}.img",
    "{stem}.lnk",
]

_SENDER_PATTERNS = [
    "{name}@{org}.com",
    "{dept}@{org}-{suffix}.com",
    "noreply@{org}-{suffix}.com",
    "{dept}-{name}@{org}.com",
]

_NAMES = ["james", "sarah", "michael", "linda", "robert", "maria",
          "david", "jennifer", "william", "elizabeth"]
_DEPTS = ["accounts", "it-support", "hr", "cfo", "finance", "admin", "helpdesk"]
_ORGS = ["legitimatecorp", "partner-firm", "company-help", "globalservices",
         "trusteddomain", "secure-portal", "corp-services"]
_SUFFIXES = ["portal", "secure", "services", "online", "updates", "global"]

_EXPLOIT_FAMILIES = [
    ("RCE via document macro", "Office"),
    ("browser exploit chain", "Browser"),
    ("PDF reader vulnerability", "PDF"),
    ("archive handler exploit", "Archive"),
    ("font parsing vulnerability", "GDI"),
    ("OLE object exploit", "Office"),
    ("scripting engine flaw", "Browser"),
]

_DELIVERY_METHODS = [
    "Malicious email attachment",
    "Drive-by download",
    "USB drop attack",
    "Watering hole compromise",
    "Supply-chain package injection",
    "SEO poisoning redirect",
    "Malvertising payload",
]


def _random_inv_id():
    year = random.randint(2025, 2027)
    seq = random.randint(1000, 9999)
    return f"INV-{year}-{seq}"


def _build_subject():
    pattern = random.choice(_SUBJECT_PATTERNS)
    return pattern.format(
        inv_id=_random_inv_id(),
        action=random.choice(_ACTIONS),
        doc_name=random.choice(_DOC_NAMES),
        role=random.choice(_ROLES),
        service=random.choice(_SERVICES),
    )


def _build_attachment(subject: str):
    # Derive a plausible stem from the subject
    stem = subject.split(":")[-1].strip().replace(" ", "_")[:30]
    stem = "".join(c for c in stem if c.isalnum() or c == "_") or "document"
    template = random.choice(_ATTACHMENT_TEMPLATES)
    return template.format(stem=stem)


def _build_sender():
    pattern = random.choice(_SENDER_PATTERNS)
    return pattern.format(
        name=random.choice(_NAMES),
        dept=random.choice(_DEPTS),
        org=random.choice(_ORGS),
        suffix=random.choice(_SUFFIXES),
    )


def _build_exploit():
    desc, family = random.choice(_EXPLOIT_FAMILIES)
    year = random.randint(2024, 2026)
    seq = random.randint(10000, 99999)
    return {
        "cve": f"CVE-{year}-{seq}",
        "description": f"Simulated {desc}",
        "family": family,
    }


class InitialAccessSimulator:
    """Simulates initial access vectors used in ransomware campaigns."""

    def __init__(self):
        self.session_id = str(uuid.uuid4())[:8]
        self.events = []

    def simulate_phishing_email(self):
        """Simulate a phishing email delivery with procedurally generated content."""
        subject = _build_subject()
        attachment = _build_attachment(subject)
        sender = _build_sender()

        events = []

        events.append(self._create_event(
            "INFO",
            f"Phishing email received from: {sender}",
            {"subject": subject, "attachment": attachment}
        ))
        time.sleep(random.uniform(0.15, 0.40))

        events.append(self._create_event(
            "INFO",
            f"User opened suspicious email: '{subject}'",
            {"action": "email_opened"}
        ))
        time.sleep(random.uniform(0.10, 0.30))

        events.append(self._create_event(
            "WARNING",
            f"User opened attachment: {attachment}",
            {"action": "attachment_opened", "file": attachment}
        ))
        time.sleep(random.uniform(0.15, 0.40))

        events.append(self._create_event(
            "INFO",
            "Simulated payload execution triggered",
            {"action": "payload_executed", "vector": "phishing"}
        ))

        events.append(self._create_event(
            "INFO",
            f"Initial access established — Session: {self.session_id}",
            {"session_id": self.session_id}
        ))

        self.events.extend(events)
        return events

    def simulate_exploit_delivery(self):
        """Simulate exploit-based initial access with generated CVE + delivery."""
        exploit = _build_exploit()
        delivery = random.choice(_DELIVERY_METHODS)
        events = []

        events.append(self._create_event(
            "INFO",
            f"Exploit vector identified: {exploit['cve']} — {exploit['description']}",
            {"exploit": exploit, "delivery": delivery}
        ))
        time.sleep(random.uniform(0.15, 0.30))

        events.append(self._create_event(
            "INFO",
            f"Delivery method: {delivery} (simulated)",
            {"action": "exploit_delivered", "method": delivery}
        ))
        time.sleep(random.uniform(0.20, 0.40))

        events.append(self._create_event(
            "INFO",
            "Simulated payload execution triggered",
            {"action": "payload_executed", "vector": "exploit"}
        ))

        events.append(self._create_event(
            "INFO",
            f"Initial access established — Session: {self.session_id}",
            {"session_id": self.session_id}
        ))

        self.events.extend(events)
        return events

    def _create_event(self, level, message, details=None):
        return {
            "timestamp": datetime.now().isoformat(),
            "stage": "initial_access",
            "level": level,
            "message": message,
            "details": details or {},
            "session_id": self.session_id,
        }
