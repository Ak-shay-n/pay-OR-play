"""
Simulation Engine HTTP + WebSocket API Server
Provides REST API and real-time WebSocket events for the frontend.
"""

import os
import sys
import json
import threading
from pathlib import Path
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
# Also allow importing from the same directory using a normalized name
engine_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(engine_dir.parent))

# Import using direct module loading since the directory has a hyphen
import importlib.util

def _import_controller():
    controller_path = engine_dir / "controller.py"
    spec = importlib.util.spec_from_file_location("controller", str(controller_path))
    mod = importlib.util.module_from_spec(spec)
    
    # First, we need to make the sub-modules importable
    modules_to_load = [
        ("initial_access", "initial_access.py"),
        ("persistence", "persistence.py"),
        ("discovery", "discovery.py"),
        ("credentials", "credentials.py"),
        ("privilege_escalation", "privilege_escalation.py"),
        ("lateral_movement", "lateral_movement.py"),
        ("evasion", "evasion.py"),
        ("exfiltration", "exfiltration.py"),
        ("encryption_demo", "encryption_demo.py"),
        ("monitoring", "monitoring.py"),
    ]
    
    # Create a fake package so relative imports work
    import types
    pkg = types.ModuleType("simulation_engine")
    pkg.__path__ = [str(engine_dir)]
    pkg.__package__ = "simulation_engine"
    sys.modules["simulation_engine"] = pkg
    
    for mod_name, filename in modules_to_load:
        mod_path = engine_dir / filename
        mod_spec = importlib.util.spec_from_file_location(
            f"simulation_engine.{mod_name}", str(mod_path),
            submodule_search_locations=[]
        )
        sub_mod = importlib.util.module_from_spec(mod_spec)
        sub_mod.__package__ = "simulation_engine"
        sys.modules[f"simulation_engine.{mod_name}"] = sub_mod
        mod_spec.loader.exec_module(sub_mod)
        setattr(pkg, mod_name, sub_mod)
    
    # Now load the controller
    ctrl_spec = importlib.util.spec_from_file_location(
        "simulation_engine.controller", str(controller_path),
        submodule_search_locations=[]
    )
    ctrl_mod = importlib.util.module_from_spec(ctrl_spec)
    ctrl_mod.__package__ = "simulation_engine"
    sys.modules["simulation_engine.controller"] = ctrl_mod
    ctrl_spec.loader.exec_module(ctrl_mod)
    return ctrl_mod

_ctrl = _import_controller()
AttackSimulationController = _ctrl.AttackSimulationController

app = Flask(__name__)
CORS(app, origins=["http://localhost:3000", "http://127.0.0.1:3000"])
socketio = SocketIO(app, cors_allowed_origins=["http://localhost:3000", "http://127.0.0.1:3000"], async_mode="threading")

# Determine sandbox path
BASE_DIR = Path(__file__).resolve().parent.parent
SANDBOX_PATH = BASE_DIR / "sandbox" / "demo_files"

# Create controller
controller = AttackSimulationController(str(SANDBOX_PATH))


# ── REST API ──────────────────────────────────────────────────────────

@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "timestamp": datetime.now().isoformat()})


@app.route("/api/sessions", methods=["GET"])
def list_sessions():
    return jsonify({"sessions": controller.get_all_sessions()})


@app.route("/api/sessions", methods=["POST"])
def create_session():
    session = controller.create_session()
    socketio.emit("session_created", session)
    return jsonify(session), 201


@app.route("/api/sessions/<session_id>", methods=["GET"])
def get_session(session_id):
    session = controller.get_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(session)


@app.route("/api/sessions/<session_id>/run/<stage>", methods=["POST"])
def run_stage(session_id, stage):
    """Run a specific attack stage."""
    def run_and_emit():
        result = controller.run_stage(session_id, stage)
        if "error" in result:
            socketio.emit("error", result)
        else:
            # Emit events one by one for real-time effect
            for event in result.get("events", []):
                socketio.emit("event", event)
            for alert in result.get("alerts", []):
                socketio.emit("alert", alert)
            socketio.emit("stage_complete", {
                "session_id": session_id,
                "stage": stage,
                "event_count": len(result.get("events", [])),
                "alert_count": len(result.get("alerts", [])),
            })

    thread = threading.Thread(target=run_and_emit)
    thread.start()

    return jsonify({"status": "running", "session_id": session_id, "stage": stage})


@app.route("/api/sessions/<session_id>/run-all", methods=["POST"])
def run_all_stages(session_id):
    """Run all attack stages in sequence."""
    def run_and_emit():
        for stage in controller.STAGES:
            socketio.emit("stage_started", {"session_id": session_id, "stage": stage})
            result = controller.run_stage(session_id, stage)
            for event in result.get("events", []):
                socketio.emit("event", event)
            for alert in result.get("alerts", []):
                socketio.emit("alert", alert)
            socketio.emit("stage_complete", {
                "session_id": session_id,
                "stage": stage,
            })

    thread = threading.Thread(target=run_and_emit)
    thread.start()

    return jsonify({"status": "running", "session_id": session_id, "stages": controller.STAGES})


@app.route("/api/sessions/<session_id>/restore", methods=["POST"])
def restore_sandbox(session_id):
    """Restore sandbox files after encryption demo."""
    events = controller.restore_sandbox(session_id)
    for event in events:
        socketio.emit("event", event)
    return jsonify({"status": "restored", "events": events})


@app.route("/api/monitoring", methods=["GET"])
def get_monitoring():
    """Get current monitoring data."""
    return jsonify(controller.get_monitoring_data())


@app.route("/api/monitoring/files", methods=["GET"])
def get_files():
    return jsonify({"files": controller.file_monitor.get_file_list()})


@app.route("/api/monitoring/processes", methods=["GET"])
def get_processes():
    include_sus = request.args.get("suspicious", "false").lower() == "true"
    return jsonify({"processes": controller.process_monitor.get_process_list(include_sus)})


@app.route("/api/monitoring/alerts", methods=["GET"])
def get_alerts():
    return jsonify({"alerts": controller.detection_engine.get_alerts()})


@app.route("/api/monitoring/rules", methods=["GET"])
def get_rules():
    return jsonify({"rules": controller.detection_engine.get_rules()})


@app.route("/api/stages", methods=["GET"])
def get_stages():
    return jsonify({"stages": controller.STAGES})


# ── WebSocket Events ──────────────────────────────────────────────────

@socketio.on("connect")
def handle_connect():
    emit("connected", {"message": "Connected to simulation server", "timestamp": datetime.now().isoformat()})


@socketio.on("disconnect")
def handle_disconnect():
    pass


@socketio.on("run_command")
def handle_command(data):
    """Handle console commands from the frontend."""
    command = data.get("command", "").strip()
    session_id = data.get("session_id")

    if not session_id:
        # Auto-create session
        session = controller.create_session()
        session_id = session["id"]
        emit("session_created", session)

    # Parse command
    if command.startswith("simulate."):
        stage = command.replace("simulate.", "")
        if stage == "initial_access":
            stage = "initial_access"

        if stage in controller.STAGES:
            emit("command_accepted", {"command": command, "stage": stage, "session_id": session_id})

            def run_and_emit():
                result = controller.run_stage(session_id, stage)
                for event in result.get("events", []):
                    socketio.emit("event", event)
                for alert in result.get("alerts", []):
                    socketio.emit("alert", alert)
                socketio.emit("stage_complete", {
                    "session_id": session_id,
                    "stage": stage,
                })

            thread = threading.Thread(target=run_and_emit)
            thread.start()
        else:
            emit("error", {"message": f"Unknown stage: {stage}"})

    elif command == "sessions":
        emit("sessions_list", {"sessions": controller.get_all_sessions()})

    elif command == "help":
        emit("help", {
            "commands": [
                "simulate.initial_access    - Simulate phishing/initial access",
                "simulate.persistence        - Simulate persistence mechanisms",
                "simulate.discovery          - Simulate system reconnaissance",
                "simulate.credentials        - Simulate credential access",
                "simulate.privilege_escalation - Simulate privilege escalation",
                "simulate.lateral_movement   - Simulate lateral movement",
                "simulate.evasion            - Simulate security evasion",
                "simulate.exfiltration       - Simulate data exfiltration",
                "simulate.ransomware         - Run encryption demonstration",
                "sessions                    - List active sessions",
                "status                      - Show current session status",
                "restore                     - Restore sandbox files",
                "clear                       - Clear console",
                "help                        - Show this help",
            ]
        })

    elif command == "status":
        session = controller.get_session(session_id)
        emit("status", session)

    elif command == "restore":
        events = controller.restore_sandbox(session_id)
        for event in events:
            socketio.emit("event", event)

    elif command == "clear":
        emit("clear", {})

    else:
        emit("error", {"message": f"Unknown command: {command}. Type 'help' for available commands."})


# ── Main ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 60)
    print("  Ransomware Simulation Platform — API Server")
    print(f"  Sandbox: {SANDBOX_PATH}")
    print("  API: http://localhost:5000")
    print("  WebSocket: ws://localhost:5000")
    print("=" * 60)
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
