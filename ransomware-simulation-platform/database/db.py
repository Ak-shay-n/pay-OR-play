"""
Database module for persisting simulation sessions, events, and alerts.
Uses SQLite for simplicity.
"""

import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path


DB_PATH = Path(__file__).resolve().parent / "ransomware_sim.db"


def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    """Initialize the database schema."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS sessions (
            id TEXT PRIMARY KEY,
            created TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            current_stage TEXT,
            completed_stages TEXT DEFAULT '[]',
            target_ip TEXT,
            target_hostname TEXT,
            target_user TEXT,
            target_os TEXT,
            discovery_data TEXT,
            updated_at TEXT
        );

        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            timestamp TEXT NOT NULL,
            stage TEXT,
            level TEXT NOT NULL,
            message TEXT NOT NULL,
            details TEXT DEFAULT '{}',
            source TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );

        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT,
            timestamp TEXT NOT NULL,
            rule_id TEXT,
            name TEXT NOT NULL,
            severity TEXT NOT NULL,
            description TEXT,
            triggering_event TEXT,
            recommendation TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES sessions(id)
        );

        CREATE INDEX IF NOT EXISTS idx_events_session ON events(session_id);
        CREATE INDEX IF NOT EXISTS idx_events_stage ON events(stage);
        CREATE INDEX IF NOT EXISTS idx_alerts_session ON alerts(session_id);
        CREATE INDEX IF NOT EXISTS idx_alerts_severity ON alerts(severity);
    """)

    conn.commit()
    conn.close()


def save_session(session: dict):
    """Save or update a session."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO sessions
        (id, created, status, current_stage, completed_stages,
         target_ip, target_hostname, target_user, target_os,
         discovery_data, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        session["id"],
        session["created"],
        session["status"],
        session.get("current_stage"),
        json.dumps(session.get("completed_stages", [])),
        session.get("target", {}).get("ip"),
        session.get("target", {}).get("hostname"),
        session.get("target", {}).get("user"),
        session.get("target", {}).get("os"),
        json.dumps(session.get("discovery_data")) if session.get("discovery_data") else None,
        datetime.now().isoformat(),
    ))

    conn.commit()
    conn.close()


def save_events(session_id: str, events: list):
    """Save events to the database."""
    conn = get_connection()
    cursor = conn.cursor()

    for event in events:
        cursor.execute("""
            INSERT INTO events (session_id, timestamp, stage, level, message, details, source)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            event.get("timestamp"),
            event.get("stage"),
            event.get("level"),
            event.get("message"),
            json.dumps(event.get("details", {})),
            event.get("source"),
        ))

    conn.commit()
    conn.close()


def save_alerts(session_id: str, alerts: list):
    """Save alerts to the database."""
    conn = get_connection()
    cursor = conn.cursor()

    for alert in alerts:
        cursor.execute("""
            INSERT INTO alerts
            (session_id, timestamp, rule_id, name, severity, description, triggering_event, recommendation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            session_id,
            alert.get("timestamp"),
            alert.get("rule_id"),
            alert.get("name"),
            alert.get("severity"),
            alert.get("description"),
            alert.get("triggering_event"),
            alert.get("recommendation"),
        ))

    conn.commit()
    conn.close()


def get_sessions():
    """Get all sessions."""
    conn = get_connection()
    cursor = conn.cursor()
    rows = cursor.execute("SELECT * FROM sessions ORDER BY created DESC").fetchall()
    conn.close()

    sessions = []
    for row in rows:
        sessions.append({
            "id": row["id"],
            "created": row["created"],
            "status": row["status"],
            "current_stage": row["current_stage"],
            "completed_stages": json.loads(row["completed_stages"]),
            "target": {
                "ip": row["target_ip"],
                "hostname": row["target_hostname"],
                "user": row["target_user"],
                "os": row["target_os"],
            },
            "discovery_data": json.loads(row["discovery_data"]) if row["discovery_data"] else None,
        })

    return sessions


def get_session_events(session_id: str):
    """Get events for a session."""
    conn = get_connection()
    cursor = conn.cursor()
    rows = cursor.execute(
        "SELECT * FROM events WHERE session_id = ? ORDER BY id ASC",
        (session_id,)
    ).fetchall()
    conn.close()

    return [
        {
            "timestamp": row["timestamp"],
            "stage": row["stage"],
            "level": row["level"],
            "message": row["message"],
            "details": json.loads(row["details"]),
            "session_id": row["session_id"],
        }
        for row in rows
    ]


def get_session_alerts(session_id: str):
    """Get alerts for a session."""
    conn = get_connection()
    cursor = conn.cursor()
    rows = cursor.execute(
        "SELECT * FROM alerts WHERE session_id = ? ORDER BY id ASC",
        (session_id,)
    ).fetchall()
    conn.close()

    return [
        {
            "timestamp": row["timestamp"],
            "rule_id": row["rule_id"],
            "name": row["name"],
            "severity": row["severity"],
            "description": row["description"],
            "triggering_event": row["triggering_event"],
            "recommendation": row["recommendation"],
        }
        for row in rows
    ]


# Initialize the database on import
init_db()
