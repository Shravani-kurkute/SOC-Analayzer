"""
Seed script: generates realistic SOC dashboard data.
Alerts, Incidents, LogEntries, Assets.
Run: python -m scripts.seed_dashboard
"""

import asyncio
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import async_session_factory
from app.models.alert import Alert
from app.models.asset import Asset
from app.models.incident import Incident
from app.models.log_entry import LogEntry
from app.models.user import User

SEVERITIES = ["critical", "high", "medium", "low", "informational"]
ALERT_STATUSES = ["new", "acknowledged", "investigating", "resolved", "false_positive"]
INCIDENT_STATUSES = ["open", "investigating", "contained", "eradiated", "recovered", "closed"]
ASSET_TYPES = ["server", "workstation", "network", "cloud", "container", "iot"]
ASSET_CRITICALITIES = ["critical", "high", "medium", "low"]
ASSET_STATUSES = ["online", "offline", "maintenance", "unknown"]
LOG_ACTIONS = ["allow", "deny", "drop", "alert"]
PROTOCOLS = ["TCP", "UDP", "ICMP", "HTTP", "HTTPS", "DNS", "SSH", "SMTP", "SMB"]

MITRE_TACTICS = [
    ("T1078", "Valid Accounts"),
    ("T1190", "Exploit Public-Facing Application"),
    ("T1133", "External Remote Services"),
    ("T1566", "Phishing"),
    ("T1059", "Command and Scripting Interpreter"),
    ("T1055", "Process Injection"),
    ("T1547", "Boot or Logon Autostart Execution"),
    ("T1098", "Account Manipulation"),
    ("T1136", "Create Account"),
    ("T1070", "Indicator Removal"),
    ("T1562", "Impair Defenses"),
    ("T1003", "OS Credential Dumping"),
    ("T1552", "Unsecured Credentials"),
    ("T1110", "Brute Force"),
    ("T1040", "Network Sniffing"),
    ("T1046", "Network Service Scanning"),
    ("T1204", "User Execution"),
    ("T1548", "Abuse Elevation Control Mechanism"),
    ("T1218", "System Binary Proxy Execution"),
    ("T1560", "Archive Collected Data"),
    ("T1041", "Exfiltration Over C2 Channel"),
    ("T1568", "Dynamic Resolution"),
    ("T1573", "Encrypted Channel"),
    ("T1205", "Traffic Signaling"),
]

ALERT_TITLES = [
    "Brute Force Attack Detected",
    "Malware Quarantine Alert",
    "Unusual Outbound Traffic",
    "Phishing Email Reported",
    "USB Device Blocked",
    "Ransomware Detection",
    "Port Scan Activity",
    "DNS Tunneling Detection",
    "Data Exfiltration Attempt",
    "Privilege Escalation Detected",
    "Suspicious PowerShell Execution",
    "Credential Dumping Attempt",
    "Lateral Movement Detected",
    "C2 Communication Detected",
    "Web Shell Upload Attempt",
    "SQL Injection Attempt",
    "XSS Attack Detected",
    "API Abuse Detected",
    "Insider Threat Alert",
    "Zero-Day Exploit Attempt",
    "Misconfigured S3 Bucket",
    "SSH Brute Force",
    "RDP Brute Force",
    "Abnormal Login Pattern",
    "New Service Installation",
    "Registry Modification Alert",
    "WMI Persistence Detected",
    "Scheduled Task Created",
    "Driver Loaded Alert",
    "Firewall Rule Modified",
]

INCIDENT_TITLES = [
    "Ransomware Outbreak - Department A",
    "Advanced Persistent Threat Campaign",
    "Internal Data Breach Investigation",
    "Supply Chain Compromise",
    "DDoS Attack Mitigation",
    "Insider Data Exfiltration",
    "Zero-Day Exploit Response",
    "Phishing Campaign Takedown",
    "Credential Theft Investigation",
    "Network Infrastructure Compromise",
]

LOG_SOURCES = [
    "firewall-01", "firewall-02", "ids-01", "ids-02",
    "edr-endpoint-01", "edr-endpoint-02", "edr-server-01",
    "dns-server-01", "dns-server-02",
    "web-proxy-01", "web-proxy-02",
    "vpn-gateway-01", "vpn-gateway-02",
    "email-gateway-01",
    "windows-events-01", "syslog-01",
]

MALICIOUS_IPS = [
    ("45.33.32.156", "US"), ("185.220.101.1", "DE"), ("91.121.87.34", "FR"),
    ("103.235.46.1", "CN"), ("5.188.62.1", "RU"), ("194.26.29.1", "NL"),
    ("45.155.205.1", "NL"), ("89.248.165.1", "NL"), ("141.98.10.1", "LT"),
    ("104.244.72.1", "LU"), ("162.247.74.1", "US"), ("185.165.29.1", "RU"),
    ("80.82.77.1", "NL"), ("185.234.72.1", "RU"), ("192.42.116.1", "NL"),
    ("107.189.28.1", "LU"), ("185.100.85.1", "NL"), ("45.61.185.1", "US"),
    ("37.49.230.1", "NL"), ("212.80.212.1", "RU"),
]

INTERNAL_IPS = [
    ("10.0.1.10", "US"), ("10.0.1.11", "US"), ("10.0.1.12", "US"),
    ("10.0.2.10", "US"), ("10.0.2.11", "US"), ("10.0.3.10", "US"),
    ("172.16.0.10", "US"), ("172.16.0.20", "US"), ("172.16.1.10", "US"),
    ("192.168.1.10", "US"), ("192.168.1.20", "US"), ("192.168.2.10", "US"),
]

COUNTRIES = ["US", "CN", "RU", "DE", "FR", "NL", "GB", "BR", "IN", "KR", "SG", "UA", "LT", "LU", "IR", "KP"]

HOSTNAMES = [
    "web-01", "web-02", "db-01", "db-02", "app-01", "app-02",
    "dc-01", "dc-02", "mail-01", "proxy-01", "dns-01", "dns-02",
    "nas-01", "backup-01", "monitoring-01", "siem-01",
    "ws-001", "ws-002", "ws-003", "ws-004", "ws-005",
    "ws-006", "ws-007", "ws-008", "ws-009", "ws-010",
    "cloud-vm-01", "cloud-vm-02", "cloud-vm-03",
    "container-host-01", "container-host-02",
]

DOMAINS = [
    "malicious-site.com", "evil-c2.net", "phishing-attempt.org",
    "ransomware-payload.xyz", "data-exfil.io", "malware-host.net",
    "driveby-download.com", "exploit-kit.org", "c2-panel.net",
    "credential-stealer.xyz",
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Python/3.13 aiohttp/3.9",
    "curl/8.12.0",
    "Wget/1.24.5",
    "Go-http-client/2.0",
    "Java/17.0.12",
    "Nmap Scripting Engine",
    "Masscan/1.3.2",
]


def random_ip(is_malicious: bool = False):
    if is_malicious:
        ip, country = random.choice(MALICIOUS_IPS)
        return ip, country
    ip, country = random.choice(INTERNAL_IPS)
    return ip, country


async def seed_database():
    async with async_session_factory() as db:
        existing = await db.scalar(select(func.count(Alert.id)))
        if existing and existing > 100:
            print(f"Database already has {existing} alerts, skipping seed.")
            return

        admin = (await db.execute(select(User).where(User.email == "admin@sentinelai.dev"))).scalar_one_or_none()
        users = (await db.execute(select(User).limit(5))).scalars().all()
        if not users:
            print("No users found. Run scripts/seed.py first.")
            return

        now = datetime.now(timezone.utc)

        print("Seeding alerts...")
        alerts = []
        for i in range(500):
            severity = random.choices(
                SEVERITIES, weights=[8, 15, 25, 35, 17], k=1
            )[0]
            mitre_id, mitre_tactic = random.choice(MITRE_TACTICS)
            hours_ago = random.uniform(0, 168)
            created = now - timedelta(hours=hours_ago)
            is_malicious = random.random() < 0.7
            src_ip, country = random_ip(is_malicious)

            status = random.choices(
                ALERT_STATUSES,
                weights=[30, 20, 15, 25, 10] if severity in ("critical", "high") else [20, 20, 10, 35, 15],
                k=1,
            )[0]

            score = {
                "critical": random.randint(80, 100),
                "high": random.randint(60, 89),
                "medium": random.randint(30, 59),
                "low": random.randint(5, 29),
                "informational": random.randint(0, 4),
            }[severity]

            alert = Alert(
                title=random.choice(ALERT_TITLES),
                description=f"Alert generated from {random.choice(LOG_SOURCES)} indicating potential security threat.",
                severity=severity,
                status=status,
                source=random.choice(LOG_SOURCES),
                source_ip=src_ip,
                destination_ip=random.choice(INTERNAL_IPS)[0],
                source_port=random.randint(1024, 65535),
                destination_port=random.choice([22, 80, 443, 3389, 445, 1433, 3306, 8080, 8443, 53]),
                protocol=random.choice(PROTOCOLS),
                mitre_technique_id=mitre_id,
                mitre_tactic=mitre_tactic,
                rule_id=f"RULE-{random.randint(1000, 9999)}",
                rule_name=f"Detection Rule {random.choice(['Brute Force', 'Malware', 'Network Anomaly', 'Web Attack', 'Credential Theft'])}",
                score=score,
                tags=random.sample(["network", "malware", "phishing", "ransomware", "insider", "apt", "ddos"], k=random.randint(1, 3)),
                country=country,
                created_at=created,
                updated_at=created,
            )
            alerts.append(alert)
            db.add(alert)
        await db.flush()

        print("Seeding incidents...")
        alert_ids = [a.id for a in alerts]
        for i in range(30):
            severity = random.choices(["critical", "high", "medium", "low"], weights=[15, 30, 35, 20], k=1)[0]
            status = random.choices(INCIDENT_STATUSES, weights=[10, 25, 20, 15, 15, 15], k=1)[0]
            hours_ago = random.uniform(0, 336)
            created = now - timedelta(hours=hours_ago)
            assigned = random.choice(users)
            related = random.sample(alert_ids, k=random.randint(2, 8))

            timeline = [
                {"id": str(i), "timestamp": (created + timedelta(minutes=random.randint(0, 60))).isoformat(),
                 "action": "Alert triggered", "actor": "system", "details": "Initial detection by SIEM"},
                {"id": str(i + 1), "timestamp": (created + timedelta(minutes=random.randint(30, 180))).isoformat(),
                 "action": "Incident created", "actor": assigned.full_name, "details": "Manual escalation"},
            ]

            incident = Incident(
                title=random.choice(INCIDENT_TITLES),
                description=f"Security incident involving {len(related)} alerts. Severity: {severity}.",
                severity=severity,
                status=status,
                category=random.choice(["ransomware", "phishing", "apt", "insider-threat", "ddos", "data-breach", "malware", "unauthorized-access"]),
                alert_ids=related,
                asset_ids=random.sample([a.id for a in alerts[:100]], k=min(len(alerts[:100]), random.randint(1, 5))) if len(alerts) >= 100 else related[:3],
                assignee_id=assigned.id if random.random() < 0.8 else None,
                closed_at=created + timedelta(hours=random.randint(4, 72)) if status in ("closed", "recovered") else None,
                timeline=timeline,
                created_at=created,
                updated_at=created,
            )
            db.add(incident)
        await db.flush()

        print("Seeding log entries...")
        for i in range(2000):
            hours_ago = random.uniform(0, 72)
            log_time = now - timedelta(hours=hours_ago)
            is_malicious = random.random() < 0.15
            src_ip, country = random_ip(is_malicious)
            dst_ip, _ = random_ip(False)

            log = LogEntry(
                timestamp=log_time,
                source_ip=src_ip,
                destination_ip=dst_ip,
                source_port=random.randint(1024, 65535),
                destination_port=random.choice([22, 80, 443, 3389, 445, 53, 8080, 8443, 25, 993]),
                protocol=random.choice(PROTOCOLS),
                action=random.choices(LOG_ACTIONS, weights=[40, 30, 20, 10], k=1)[0],
                log_source=random.choice(LOG_SOURCES),
                raw_message=f"Log entry from {random.choice(LOG_SOURCES)} at {log_time.isoformat()}",
                user_agent=random.choice(USER_AGENTS),
                bytes_sent=random.randint(64, 10485760),
                bytes_received=random.randint(64, 10485760),
                threat_score=random.randint(0, 100) if is_malicious else random.randint(0, 20),
                country=country,
                created_at=log_time,
                updated_at=log_time,
            )
            db.add(log)
        await db.flush()

        print("Seeding assets...")
        for hostname in HOSTNAMES:
            asset_type = "server" if hostname.startswith(("web", "db", "app", "dc", "mail", "proxy", "dns", "nas", "backup", "monitoring", "siem")) else \
                "workstation" if hostname.startswith("ws") else \
                "cloud" if hostname.startswith("cloud") else \
                "container" if hostname.startswith("container") else "network"

            internal_ip = random.choice(INTERNAL_IPS)[0]
            asset = Asset(
                hostname=f"{hostname}.sentinelai.internal",
                ip_address=internal_ip,
                mac_address=":".join(f"{random.randint(0,255):02x}" for _ in range(6)),
                os=random.choice(["Windows Server 2025", "Windows 11 Pro", "Ubuntu 24.04 LTS", "RHEL 9.4", "Debian 12", "macOS Sequoia"]),
                os_version=random.choice(["24.04", "9.4", "12.0", "25.0"]),
                asset_type=asset_type,
                criticality=random.choices(ASSET_CRITICALITIES, weights=[10, 30, 40, 20], k=1)[0],
                status=random.choices(ASSET_STATUSES, weights=[70, 15, 10, 5], k=1)[0],
                vulnerability_count=random.randint(0, 25),
                open_ports=random.randint(1, 20),
                last_seen=now - timedelta(minutes=random.randint(0, 1440)),
                location=random.choice(["Data Center A", "Data Center B", "HQ Floor 1", "HQ Floor 2", "Remote Office NY", "Remote Office LA", "AWS us-east-1", "Azure us-west-2"]),
                department=random.choice(["Engineering", "Finance", "HR", "IT", "Security", "Marketing", "Sales", "Operations"]),
                owner=random.choice([u.full_name for u in users]),
            )
            db.add(asset)
        await db.flush()

        await db.commit()
        print("Seeding complete!")
        print(f"  - {len(alerts)} alerts created")
        print(f"  - 30 incidents created")
        print(f"  - 2000 log entries created")
        print(f"  - {len(HOSTNAMES)} assets created")


if __name__ == "__main__":
    asyncio.run(seed_database())
