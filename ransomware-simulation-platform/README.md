# Ransomware Attack Lifecycle Simulation and Detection Platform

A cybersecurity training platform that simulates the complete lifecycle of a ransomware attack inside a controlled virtual lab. Designed for educational and research purposes.

## Architecture

```
Frontend Dashboard (Next.js + React + TailwindCSS)
    │
    │ WebSocket / REST API
    ▼
Simulation Engine (Python + Flask + SocketIO)
    │
    ├── Initial Access Simulator
    ├── Persistence Simulator
    ├── Discovery Simulator
    ├── Credential Simulator
    ├── Privilege Escalation Simulator
    ├── Lateral Movement Simulator
    ├── Security Evasion Simulator
    ├── Data Exfiltration Simulator
    ├── File Encryption Demonstrator
    └── Monitoring & Detection Engine
```

## Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- npm

### 1. Start the Simulation Server (Backend)

```bash
cd simulation-engine
pip install -r requirements.txt
python server.py
```

The API server will start at `http://localhost:5000`.

### 2. Start the Frontend Dashboard

```bash
cd frontend
npm install
npm run dev
```

The dashboard will open at `http://localhost:3000`.

### 3. Using the Platform

1. Open the dashboard at `http://localhost:3000`
2. Click **"+ NEW SESSION"** to create a target session
3. Use the **command console** or the **Attack Timeline** buttons to run simulations
4. Watch events stream into the Event Log in real-time
5. Monitor detection alerts in the right panel

## Console Commands

| Command | Description |
|---|---|
| `simulate.initial_access` | Simulate phishing / initial access vector |
| `simulate.persistence` | Simulate persistence mechanisms |
| `simulate.discovery` | Simulate system reconnaissance |
| `simulate.credentials` | Simulate credential access |
| `simulate.privilege_escalation` | Simulate privilege escalation |
| `simulate.lateral_movement` | Simulate network lateral movement |
| `simulate.evasion` | Simulate security evasion techniques |
| `simulate.exfiltration` | Simulate data exfiltration |
| `simulate.ransomware` | Run file encryption demonstration |
| `restore` | Restore sandbox files after encryption demo |
| `status` | Show current session status |
| `sessions` | List all sessions |
| `help` | Show available commands |
| `clear` | Clear the event log |

## Simulated Attack Stages

### 1. Initial Access
Simulates phishing emails with malicious attachments or exploit-based delivery.

### 2. Persistence
Demonstrates registry run keys, scheduled tasks, startup folder, WMI subscriptions, and service installation.

### 3. System Discovery
Collects simulated OS info, user accounts, network configuration, shares, and installed software.

### 4. Credential Access
Simulates LSASS dumps, SAM extraction, cached credentials, and browser password access.

### 5. Privilege Escalation
Shows token impersonation, UAC bypass, service exploit, and DLL side-loading scenarios.

### 6. Lateral Movement
Simulates network scanning and movement via SMB, RDP, WMI, PsExec, and PowerShell Remoting.

### 7. Security Evasion
Demonstrates disabling defenders, clearing logs, timestomping, process injection, and AMSI bypass.

### 8. Data Exfiltration
Shows file discovery, data staging, and simulated data transfer via HTTPS, DNS tunneling, or cloud storage.

### 9. Ransomware Encryption
Encrypts demo files in the sandbox directory with reversible encoding. Creates a simulated ransom note.

## Detection Engine

The built-in detection engine monitors for:
- Mass file modification
- High file entropy (encryption indicators)
- Rapid file renaming
- Suspicious process activity
- Shadow copy deletion attempts
- Ransom note creation
- Unusual network activity
- Security tool tampering

## Project Structure

```
ransomware-simulation-platform/
├── frontend/               # Next.js dashboard
│   └── src/
│       ├── app/            # App router pages
│       ├── components/     # React components
│       ├── hooks/          # Custom hooks (WebSocket)
│       └── types/          # TypeScript types
├── simulation-engine/      # Python simulation engine
│   ├── server.py           # Flask API + WebSocket server
│   ├── controller.py       # Main orchestration controller
│   ├── initial_access.py   # Initial access simulation
│   ├── persistence.py      # Persistence simulation
│   ├── discovery.py        # System discovery simulation
│   ├── credentials.py      # Credential access simulation
│   ├── privilege_escalation.py
│   ├── lateral_movement.py
│   ├── evasion.py          # Security evasion simulation
│   ├── exfiltration.py     # Data exfiltration simulation
│   ├── encryption_demo.py  # Ransomware encryption demo
│   └── monitoring.py       # File/process monitoring + detection
├── sandbox/                # Sandboxed demo files
│   └── demo_files/         # Files for encryption demo
├── database/               # SQLite database module
│   └── db.py
└── README.md
```

## Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js, React, TailwindCSS, socket.io-client |
| Backend | Python, Flask, Flask-SocketIO |
| Simulation | Python (custom modules) |
| Monitoring | Python watchdog, psutil |
| Database | SQLite |
| Real-time | WebSocket (Socket.IO) |

## Safety Notice

⚠️ **This platform is for educational and research purposes only.**

- All attack behaviors are **simulated** — no real harm is performed
- No actual malware is created or executed
- Credential data is **fabricated** — no real credentials are accessed
- File encryption only operates on **demo files** in the sandbox directory
- All encrypted files are **reversible** with the restore function
- Network activity is **simulated** — no real connections are made

## License

Educational use only. Not for malicious purposes.
