from app.detection.registry import DetectionRuleRegistry

SSH_BRUTE_FORCE = {
    "id": "SSH-001",
    "name": "SSH Brute Force Attack",
    "description": "Multiple failed SSH login attempts from the same source IP within a short time window, indicating a brute force attack.",
    "category": "ssh",
    "severity": "high",
    "risk_score": 7.5,
    "mitre_mapping": {"technique_id": "T1110", "tactic": "credential_access"},
    "enabled": True,
    "time_window_minutes": 30,
    "correlation_type": "ssh_session",
    "threshold": {"failed_attempts": 5},
    "conditions": {"sources": ["ssh", "sshd", "linux"], "actions": ["failed_password", "failed"]},
    "recommendation": "Block the source IP at the firewall. Review SSH logs for successful logins after the brute force. Implement rate limiting on SSH. Enforce key-based authentication.",
}

SSH_SUCCESS_AFTER_BRUTE = {
    "id": "SSH-002",
    "name": "SSH Login After Brute Force",
    "description": "A successful SSH login was detected after multiple failed attempts from the same source, suggesting a compromised credential.",
    "category": "ssh",
    "severity": "critical",
    "risk_score": 9.0,
    "mitre_mapping": {"technique_id": "T1078", "tactic": "initial_access"},
    "enabled": True,
    "time_window_minutes": 30,
    "correlation_type": "ssh_session",
    "threshold": {"failed_attempts": 3, "has_success": True},
    "conditions": {"sources": ["ssh", "sshd"], "actions": ["failed_password", "accepted"]},
    "recommendation": "Immediately rotate the compromised credential. Check for lateral movement from the affected host. Review all sessions from the source IP. Enable MFA on the account.",
}

SSH_ROOT_LOGIN = {
    "id": "SSH-003",
    "name": "SSH Root Login Detected",
    "description": "Direct SSH login as root detected. Root login over SSH is a security best practice violation.",
    "category": "ssh",
    "severity": "high",
    "risk_score": 8.0,
    "mitre_mapping": {"technique_id": "T1078", "tactic": "privilege_escalation"},
    "enabled": True,
    "time_window_minutes": 60,
    "correlation_type": "ssh_session",
    "threshold": {"min_events": 1},
    "conditions": {"sources": ["ssh", "sshd"], "usernames": ["root"], "actions": ["accepted"]},
    "recommendation": "Disable direct SSH root login. Ensure all administrative access is via sudo. Review audit logs for unauthorized privilege escalation.",
}

PASSWORD_SPRAY = {
    "id": "AUTH-001",
    "name": "Password Spray Attack",
    "description": "Multiple failed login attempts across different usernames from the same source IP, characteristic of a password spray attack.",
    "category": "authentication",
    "severity": "high",
    "risk_score": 7.0,
    "mitre_mapping": {"technique_id": "T1110.003", "tactic": "credential_access"},
    "enabled": True,
    "time_window_minutes": 30,
    "correlation_type": "credential_stuffing",
    "threshold": {"unique_users": 5},
    "conditions": {"sources": ["ssh", "sshd", "auth", "login"], "actions": ["failed_password", "failed"]},
    "recommendation": "Block the source IP. Review authentication logs for successful logins. Implement account lockout policies. Deploy risk-based authentication.",
}

CREDENTIAL_STUFFING = {
    "id": "AUTH-002",
    "name": "Credential Stuffing Attack",
    "description": "High volume of login attempts from a single source across many accounts, indicating credential stuffing with previously leaked credentials.",
    "category": "authentication",
    "severity": "critical",
    "risk_score": 8.5,
    "mitre_mapping": {"technique_id": "T1110.004", "tactic": "credential_access"},
    "enabled": True,
    "time_window_minutes": 15,
    "correlation_type": "credential_stuffing",
    "threshold": {"min_attempts": 15},
    "conditions": {"sources": ["ssh", "sshd", "auth", "login"], "actions": ["failed_password", "failed"]},
    "recommendation": "Block the source IP immediately. Deploy CAPTCHA on login pages. Implement MFA across all accounts. Force password reset for targeted accounts.",
}

IMPOSSIBLE_TRAVEL = {
    "id": "AUTH-003",
    "name": "Impossible Travel Detected",
    "description": "The same user account was used from geographically distant locations within an impossibly short time period, indicating account compromise.",
    "category": "authentication",
    "severity": "critical",
    "risk_score": 9.5,
    "mitre_mapping": {"technique_id": "T1078", "tactic": "initial_access"},
    "enabled": True,
    "time_window_minutes": 120,
    "correlation_type": "credential_compromise",
    "threshold": {"min_distance_km": 1000, "min_speed_kmh": 800},
    "conditions": {"sources": ["ssh", "sshd", "auth"]},
    "recommendation": "Immediately lock the affected account. Force password reset. Check for additional compromised accounts. Review recent activity from all sessions.",
}

PORT_SCAN = {
    "id": "NET-001",
    "name": "Network Port Scan Detected",
    "description": "Multiple connection attempts to different ports from a single source IP, indicating reconnaissance activity.",
    "category": "network",
    "severity": "medium",
    "risk_score": 5.0,
    "mitre_mapping": {"technique_id": "T1046", "tactic": "discovery"},
    "enabled": True,
    "time_window_minutes": 10,
    "correlation_type": "port_scan",
    "threshold": {"unique_ports": 10},
    "conditions": {"sources": ["firewall", "pfsense", "cisco", "fortinet"], "actions": ["deny", "block", "reject"]},
    "recommendation": "Investigate the source IP. Check for follow-up attack attempts. Add the IP to threat intelligence feeds. Harden exposed services.",
}

INTERNAL_RECON = {
    "id": "NET-002",
    "name": "Internal Network Reconnaissance",
    "description": "Internal IP address scanning multiple hosts, suggesting lateral movement or internal reconnaissance.",
    "category": "network",
    "severity": "high",
    "risk_score": 7.0,
    "mitre_mapping": {"technique_id": "T1595", "tactic": "reconnaissance"},
    "enabled": True,
    "time_window_minutes": 30,
    "correlation_type": "port_scan",
    "threshold": {"unique_destinations": 5},
    "conditions": {"sources": ["firewall", "pfsense", "cisco"], "actions": ["deny", "block"]},
    "recommendation": "Quarantine the internal host. Investigate how the host was compromised. Scan for persistent backdoors. Review network segmentation.",
}

LATERAL_MOVEMENT = {
    "id": "NET-003",
    "name": "Lateral Movement Detected",
    "description": "The same credential or source IP is being used to access multiple internal systems, indicating lateral movement.",
    "category": "network",
    "severity": "critical",
    "risk_score": 9.0,
    "mitre_mapping": {"technique_id": "T1021", "tactic": "lateral_movement"},
    "enabled": True,
    "time_window_minutes": 60,
    "correlation_type": "targeted_attack",
    "threshold": {"unique_destinations": 3},
    "conditions": {"actions": ["connect", "login", "access"], "sources": ["ssh", "windows", "rdp"]},
    "recommendation": "Isolate the affected accounts and systems. Conduct forensic analysis on the initial compromise vector. Review all lateral movement paths. Implement network micro-segmentation.",
}

EXCESSIVE_DENIES = {
    "id": "FW-001",
    "name": "Excessive Firewall Denies",
    "description": "A large number of firewall deny events from a single source IP, indicating either misconfiguration or malicious scanning.",
    "category": "firewall",
    "severity": "medium",
    "risk_score": 4.5,
    "mitre_mapping": {"technique_id": "T1595", "tactic": "reconnaissance"},
    "enabled": True,
    "time_window_minutes": 15,
    "correlation_type": "firewall_block",
    "threshold": {"min_denies": 20},
    "conditions": {"sources": ["firewall", "pfsense", "cisco", "fortinet"], "actions": ["deny", "block", "reject"]},
    "recommendation": "Review firewall rules for any misconfigurations. Check if the source IP is known malicious. Consider adding the IP to blocklist.",
}

BLOCKED_SCANNING = {
    "id": "FW-002",
    "name": "Blocked Port Scanning Activity",
    "description": "Firewall has blocked systematic port scanning from an external IP, indicating pre-attack reconnaissance.",
    "category": "firewall",
    "severity": "medium",
    "risk_score": 5.5,
    "mitre_mapping": {"technique_id": "T1046", "tactic": "discovery"},
    "enabled": True,
    "time_window_minutes": 10,
    "correlation_type": "firewall_block",
    "threshold": {"unique_ports": 15},
    "conditions": {"sources": ["firewall", "pfsense", "cisco"], "actions": ["deny", "reject"]},
    "recommendation": "Add the source IP to automated blocklist. Verify that no services are exposed on unexpected ports. Review IDS/IPS alerts.",
}

SQL_INJECTION = {
    "id": "WEB-001",
    "name": "SQL Injection Attempt",
    "description": "SQL injection patterns detected in HTTP requests, indicating an attempt to manipulate database queries.",
    "category": "web",
    "severity": "critical",
    "risk_score": 9.0,
    "mitre_mapping": {"technique_id": "T1190", "tactic": "initial_access"},
    "enabled": True,
    "time_window_minutes": 30,
    "correlation_type": "web_attack",
    "threshold": {"min_events": 1},
    "conditions": {"sources": ["apache", "nginx", "http", "web"], "actions": ["sql_injection", "sqli", "select", "union", "drop"]},
    "recommendation": "Block the source IP at the WAF. Review the targeted endpoint for SQL injection vulnerabilities. Implement parameterized queries. Deploy Web Application Firewall rules.",
}

XSS_DETECTED = {
    "id": "WEB-002",
    "name": "Cross-Site Scripting (XSS) Attempt",
    "description": "XSS attack patterns detected in HTTP requests, indicating an attempt to inject malicious scripts.",
    "category": "web",
    "severity": "high",
    "risk_score": 7.5,
    "mitre_mapping": {"technique_id": "T1059.007", "tactic": "execution"},
    "enabled": True,
    "time_window_minutes": 30,
    "correlation_type": "web_attack",
    "threshold": {"min_events": 1},
    "conditions": {"sources": ["apache", "nginx", "http", "web"], "actions": ["xss", "cross_site", "script", "alert"]},
    "recommendation": "Block the source IP. Implement Content Security Policy (CSP) headers. Sanitize user input. Deploy XSS protection mechanisms.",
}

RCE_ATTEMPT = {
    "id": "WEB-003",
    "name": "Remote Code Execution Attempt",
    "description": "RCE attack patterns detected in HTTP requests, indicating an attempt to execute arbitrary commands on the server.",
    "category": "web",
    "severity": "critical",
    "risk_score": 9.5,
    "mitre_mapping": {"technique_id": "T1203", "tactic": "execution"},
    "enabled": True,
    "time_window_minutes": 30,
    "correlation_type": "web_attack",
    "threshold": {"min_events": 1},
    "conditions": {"sources": ["apache", "nginx", "http", "web"], "actions": ["rce", "command_execution", "exec", "shell_exec", "system"]},
    "recommendation": "Block the source IP immediately. Patch the vulnerable application. Review server logs for successful exploitation. Conduct forensic analysis.",
}

PATH_TRAVERSAL = {
    "id": "WEB-004",
    "name": "Path Traversal Attempt",
    "description": "Directory traversal patterns detected in HTTP requests, indicating an attempt to access files outside the web root.",
    "category": "web",
    "severity": "high",
    "risk_score": 7.0,
    "mitre_mapping": {"technique_id": "T1005", "tactic": "collection"},
    "enabled": True,
    "time_window_minutes": 30,
    "correlation_type": "web_attack",
    "threshold": {"min_events": 1},
    "conditions": {"sources": ["apache", "nginx", "http", "web"], "actions": ["path_traversal", "directory", "../", "..\\"]},
    "recommendation": "Block the source IP. Review file permissions. Implement proper input validation. Ensure web server is not running with elevated privileges.",
}

PRIVILEGE_ESCALATION = {
    "id": "LIN-001",
    "name": "Linux Privilege Escalation via sudo",
    "description": "Detected sudo usage suggesting privilege escalation, potentially indicating an attacker moving from standard user to root.",
    "category": "linux",
    "severity": "high",
    "risk_score": 8.0,
    "mitre_mapping": {"technique_id": "T1068", "tactic": "privilege_escalation"},
    "enabled": True,
    "time_window_minutes": 30,
    "correlation_type": "ssh_session",
    "threshold": {"min_events": 1},
    "conditions": {"sources": ["linux", "auth", "syslog", "sudo"], "actions": ["sudo", "su"]},
    "recommendation": "Review sudoers configuration. Verify the user's activity is legitimate. Monitor for additional suspicious commands. Implement least privilege principles.",
}

CRON_PERSISTENCE = {
    "id": "LIN-002",
    "name": "Suspicious Cron Job Persistence",
    "description": "Potential cron job modification detected, indicating an attempt to establish persistence on a Linux system.",
    "category": "linux",
    "severity": "high",
    "risk_score": 7.5,
    "mitre_mapping": {"technique_id": "T1053.003", "tactic": "persistence"},
    "enabled": True,
    "time_window_minutes": 60,
    "correlation_type": "ssh_session",
    "threshold": {"min_events": 1},
    "conditions": {"sources": ["linux", "auth", "syslog", "cron"], "actions": ["cron", "crontab", "schtask"]},
    "recommendation": "Review the crontab entries for unauthorized jobs. Check file integrity of system binaries. Investigate how the attacker gained access to modify cron.",
}

WINDOWS_PRIV_ESC = {
    "id": "WIN-001",
    "name": "Windows Privilege Escalation",
    "description": "Potential Windows privilege escalation detected through service installation or registry modification.",
    "category": "windows",
    "severity": "critical",
    "risk_score": 8.5,
    "mitre_mapping": {"technique_id": "T1543", "tactic": "privilege_escalation"},
    "enabled": True,
    "time_window_minutes": 30,
    "correlation_type": "attack_chain",
    "threshold": {"min_events": 1},
    "conditions": {"sources": ["windows", "win", "event"], "actions": ["service", "registry", "schtask"]},
    "recommendation": "Review recently installed services and registry modifications. Verify the account used. Conduct memory analysis on the affected host.",
}


def register_all() -> None:
    rules = [
        SSH_BRUTE_FORCE, SSH_SUCCESS_AFTER_BRUTE, SSH_ROOT_LOGIN,
        PASSWORD_SPRAY, CREDENTIAL_STUFFING, IMPOSSIBLE_TRAVEL,
        PORT_SCAN, INTERNAL_RECON, LATERAL_MOVEMENT,
        EXCESSIVE_DENIES, BLOCKED_SCANNING,
        SQL_INJECTION, XSS_DETECTED, RCE_ATTEMPT, PATH_TRAVERSAL,
        PRIVILEGE_ESCALATION, CRON_PERSISTENCE,
        WINDOWS_PRIV_ESC,
    ]
    for rule in rules:
        DetectionRuleRegistry.register(rule)
