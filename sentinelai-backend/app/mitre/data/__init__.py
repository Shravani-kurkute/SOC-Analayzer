MITRE_TECHNIQUES = [
    # === Initial Access ===
    {"technique_id": "T1078", "name": "Valid Accounts", "tactic": "Initial Access", "tactic_id": "TA0001", "severity": "high", "score": 8.0, "kill_chain_phase": "initial-access", "detection_rules": ["brute_force", "credential_stuffing"], "ioc_indicators": ["username", "ipv4", "ipv6"]},
    {"technique_id": "T1078.001", "name": "Default Accounts", "tactic": "Initial Access", "tactic_id": "TA0001", "is_subtechnique": True, "parent_technique_id": "T1078", "severity": "high", "score": 7.0, "kill_chain_phase": "initial-access"},
    {"technique_id": "T1078.002", "name": "Domain Accounts", "tactic": "Initial Access", "tactic_id": "TA0001", "is_subtechnique": True, "parent_technique_id": "T1078", "severity": "high", "score": 7.5, "kill_chain_phase": "initial-access"},
    {"technique_id": "T1190", "name": "Exploit Public-Facing Application", "tactic": "Initial Access", "tactic_id": "TA0001", "severity": "critical", "score": 9.0, "kill_chain_phase": "initial-access", "detection_rules": ["web_attack", "sql_injection"], "ioc_indicators": ["url", "ipv4", "cve"]},
    {"technique_id": "T1133", "name": "External Remote Services", "tactic": "Initial Access", "tactic_id": "TA0001", "severity": "high", "score": 7.5, "kill_chain_phase": "initial-access", "detection_rules": ["ssh_brute_force", "rdp_brute_force"]},
    {"technique_id": "T1566", "name": "Phishing", "tactic": "Initial Access", "tactic_id": "TA0001", "severity": "high", "score": 8.0, "kill_chain_phase": "initial-access", "ioc_indicators": ["email", "url", "domain"]},
    {"technique_id": "T1566.001", "name": "Spearphishing Attachment", "tactic": "Initial Access", "tactic_id": "TA0001", "is_subtechnique": True, "parent_technique_id": "T1566", "severity": "high", "score": 8.0, "kill_chain_phase": "initial-access"},
    {"technique_id": "T1566.002", "name": "Spearphishing Link", "tactic": "Initial Access", "tactic_id": "TA0001", "is_subtechnique": True, "parent_technique_id": "T1566", "severity": "high", "score": 7.5, "kill_chain_phase": "initial-access"},
    {"technique_id": "T1189", "name": "Drive-by Compromise", "tactic": "Initial Access", "tactic_id": "TA0001", "severity": "high", "score": 7.0, "kill_chain_phase": "initial-access", "ioc_indicators": ["url", "domain"]},
    {"technique_id": "T1091", "name": "Replication Through Removable Media", "tactic": "Initial Access", "tactic_id": "TA0001", "severity": "medium", "score": 5.0, "kill_chain_phase": "initial-access"},

    # === Execution ===
    {"technique_id": "T1059", "name": "Command and Scripting Interpreter", "tactic": "Execution", "tactic_id": "TA0002", "severity": "high", "score": 8.0, "kill_chain_phase": "execution", "detection_rules": ["command_line_detection"], "ioc_indicators": ["command_line", "process_name"]},
    {"technique_id": "T1059.001", "name": "PowerShell", "tactic": "Execution", "tactic_id": "TA0002", "is_subtechnique": True, "parent_technique_id": "T1059", "severity": "critical", "score": 9.0, "kill_chain_phase": "execution"},
    {"technique_id": "T1059.003", "name": "Windows Command Shell", "tactic": "Execution", "tactic_id": "TA0002", "is_subtechnique": True, "parent_technique_id": "T1059", "severity": "high", "score": 7.5, "kill_chain_phase": "execution"},
    {"technique_id": "T1059.004", "name": "Unix Shell", "tactic": "Execution", "tactic_id": "TA0002", "is_subtechnique": True, "parent_technique_id": "T1059", "severity": "high", "score": 7.5, "kill_chain_phase": "execution"},
    {"technique_id": "T1059.006", "name": "Python", "tactic": "Execution", "tactic_id": "TA0002", "is_subtechnique": True, "parent_technique_id": "T1059", "severity": "high", "score": 7.0, "kill_chain_phase": "execution"},
    {"technique_id": "T1204", "name": "User Execution", "tactic": "Execution", "tactic_id": "TA0002", "severity": "medium", "score": 6.0, "kill_chain_phase": "execution"},
    {"technique_id": "T1204.002", "name": "Malicious File", "tactic": "Execution", "tactic_id": "TA0002", "is_subtechnique": True, "parent_technique_id": "T1204", "severity": "high", "score": 7.0, "kill_chain_phase": "execution", "ioc_indicators": ["md5", "sha1", "sha256", "executable_path"]},
    {"technique_id": "T1559", "name": "Inter-Process Communication", "tactic": "Execution", "tactic_id": "TA0002", "severity": "medium", "score": 5.0, "kill_chain_phase": "execution"},

    # === Persistence ===
    {"technique_id": "T1547", "name": "Boot or Logon Autostart Execution", "tactic": "Persistence", "tactic_id": "TA0003", "severity": "high", "score": 7.5, "kill_chain_phase": "persistence"},
    {"technique_id": "T1547.001", "name": "Registry Run Keys / Startup Folder", "tactic": "Persistence", "tactic_id": "TA0003", "is_subtechnique": True, "parent_technique_id": "T1547", "severity": "high", "score": 8.0, "kill_chain_phase": "persistence", "ioc_indicators": ["registry_key"]},
    {"technique_id": "T1098", "name": "Account Manipulation", "tactic": "Persistence", "tactic_id": "TA0003", "severity": "high", "score": 7.0, "kill_chain_phase": "persistence", "detection_rules": ["account_manipulation"], "ioc_indicators": ["username"]},
    {"technique_id": "T1136", "name": "Create Account", "tactic": "Persistence", "tactic_id": "TA0003", "severity": "high", "score": 7.0, "kill_chain_phase": "persistence", "ioc_indicators": ["username"]},
    {"technique_id": "T1136.001", "name": "Local Account", "tactic": "Persistence", "tactic_id": "TA0003", "is_subtechnique": True, "parent_technique_id": "T1136", "severity": "high", "score": 7.0, "kill_chain_phase": "persistence"},
    {"technique_id": "T1505", "name": "Server Software Component", "tactic": "Persistence", "tactic_id": "TA0003", "severity": "high", "score": 7.5, "kill_chain_phase": "persistence"},

    # === Privilege Escalation ===
    {"technique_id": "T1548", "name": "Abuse Elevation Control Mechanism", "tactic": "Privilege Escalation", "tactic_id": "TA0004", "severity": "high", "score": 8.0, "kill_chain_phase": "privilege-escalation"},
    {"technique_id": "T1548.002", "name": "Bypass User Account Control", "tactic": "Privilege Escalation", "tactic_id": "TA0004", "is_subtechnique": True, "parent_technique_id": "T1548", "severity": "high", "score": 8.0, "kill_chain_phase": "privilege-escalation"},
    {"technique_id": "T1548.003", "name": "Sudo and Sudo Caching", "tactic": "Privilege Escalation", "tactic_id": "TA0004", "is_subtechnique": True, "parent_technique_id": "T1548", "severity": "high", "score": 7.0, "kill_chain_phase": "privilege-escalation"},
    {"technique_id": "T1055", "name": "Process Injection", "tactic": "Privilege Escalation", "tactic_id": "TA0004", "severity": "critical", "score": 9.0, "kill_chain_phase": "privilege-escalation", "ioc_indicators": ["process_name", "executable_path"]},
    {"technique_id": "T1068", "name": "Exploitation for Privilege Escalation", "tactic": "Privilege Escalation", "tactic_id": "TA0004", "severity": "critical", "score": 9.5, "kill_chain_phase": "privilege-escalation", "ioc_indicators": ["cve"]},
    {"technique_id": "T1078.003", "name": "Local Accounts", "tactic": "Privilege Escalation", "tactic_id": "TA0004", "is_subtechnique": True, "parent_technique_id": "T1078", "severity": "high", "score": 7.0, "kill_chain_phase": "privilege-escalation"},

    # === Defense Evasion ===
    {"technique_id": "T1562", "name": "Impair Defenses", "tactic": "Defense Evasion", "tactic_id": "TA0005", "severity": "critical", "score": 9.0, "kill_chain_phase": "defense-evasion"},
    {"technique_id": "T1562.001", "name": "Disable or Modify Tools", "tactic": "Defense Evasion", "tactic_id": "TA0005", "is_subtechnique": True, "parent_technique_id": "T1562", "severity": "critical", "score": 9.0, "kill_chain_phase": "defense-evasion"},
    {"technique_id": "T1070", "name": "Indicator Removal", "tactic": "Defense Evasion", "tactic_id": "TA0005", "severity": "high", "score": 8.0, "kill_chain_phase": "defense-evasion"},
    {"technique_id": "T1070.004", "name": "File Deletion", "tactic": "Defense Evasion", "tactic_id": "TA0005", "is_subtechnique": True, "parent_technique_id": "T1070", "severity": "high", "score": 7.0, "kill_chain_phase": "defense-evasion"},
    {"technique_id": "T1036", "name": "Masquerading", "tactic": "Defense Evasion", "tactic_id": "TA0005", "severity": "high", "score": 7.5, "kill_chain_phase": "defense-evasion"},
    {"technique_id": "T1036.005", "name": "Match Legitimate Name or Location", "tactic": "Defense Evasion", "tactic_id": "TA0005", "is_subtechnique": True, "parent_technique_id": "T1036", "severity": "high", "score": 7.0, "kill_chain_phase": "defense-evasion"},
    {"technique_id": "T1027", "name": "Obfuscated Files or Information", "tactic": "Defense Evasion", "tactic_id": "TA0005", "severity": "high", "score": 7.5, "kill_chain_phase": "defense-evasion", "ioc_indicators": ["md5", "sha1", "sha256"]},
    {"technique_id": "T1140", "name": "Deobfuscate/Decode Files or Information", "tactic": "Defense Evasion", "tactic_id": "TA0005", "severity": "medium", "score": 6.0, "kill_chain_phase": "defense-evasion"},

    # === Credential Access ===
    {"technique_id": "T1110", "name": "Brute Force", "tactic": "Credential Access", "tactic_id": "TA0006", "severity": "high", "score": 8.0, "kill_chain_phase": "credential-access", "detection_rules": ["brute_force", "ssh_brute_force"], "ioc_indicators": ["ipv4", "username"]},
    {"technique_id": "T1110.001", "name": "Password Guessing", "tactic": "Credential Access", "tactic_id": "TA0006", "is_subtechnique": True, "parent_technique_id": "T1110", "severity": "high", "score": 7.0, "kill_chain_phase": "credential-access"},
    {"technique_id": "T1110.002", "name": "Password Cracking", "tactic": "Credential Access", "tactic_id": "TA0006", "is_subtechnique": True, "parent_technique_id": "T1110", "severity": "high", "score": 7.0, "kill_chain_phase": "credential-access"},
    {"technique_id": "T1110.003", "name": "Password Spraying", "tactic": "Credential Access", "tactic_id": "TA0006", "is_subtechnique": True, "parent_technique_id": "T1110", "severity": "high", "score": 7.5, "kill_chain_phase": "credential-access", "detection_rules": ["credential_stuffing"]},
    {"technique_id": "T1552", "name": "Unsecured Credentials", "tactic": "Credential Access", "tactic_id": "TA0006", "severity": "high", "score": 7.5, "kill_chain_phase": "credential-access"},
    {"technique_id": "T1552.001", "name": "Credentials In Files", "tactic": "Credential Access", "tactic_id": "TA0006", "is_subtechnique": True, "parent_technique_id": "T1552", "severity": "high", "score": 7.0, "kill_chain_phase": "credential-access"},
    {"technique_id": "T1555", "name": "Credentials from Password Stores", "tactic": "Credential Access", "tactic_id": "TA0006", "severity": "critical", "score": 9.0, "kill_chain_phase": "credential-access"},

    # === Discovery ===
    {"technique_id": "T1082", "name": "System Information Discovery", "tactic": "Discovery", "tactic_id": "TA0007", "severity": "medium", "score": 5.0, "kill_chain_phase": "discovery"},
    {"technique_id": "T1083", "name": "File and Directory Discovery", "tactic": "Discovery", "tactic_id": "TA0007", "severity": "medium", "score": 5.0, "kill_chain_phase": "discovery"},
    {"technique_id": "T1046", "name": "Network Service Discovery", "tactic": "Discovery", "tactic_id": "TA0007", "severity": "medium", "score": 5.5, "kill_chain_phase": "discovery", "detection_rules": ["port_scan"]},
    {"technique_id": "T1049", "name": "System Network Connections Discovery", "tactic": "Discovery", "tactic_id": "TA0007", "severity": "medium", "score": 5.0, "kill_chain_phase": "discovery"},
    {"technique_id": "T1033", "name": "System Owner/User Discovery", "tactic": "Discovery", "tactic_id": "TA0007", "severity": "low", "score": 4.0, "kill_chain_phase": "discovery"},
    {"technique_id": "T1057", "name": "Process Discovery", "tactic": "Discovery", "tactic_id": "TA0007", "severity": "medium", "score": 5.0, "kill_chain_phase": "discovery", "ioc_indicators": ["process_name"]},
    {"technique_id": "T1018", "name": "Remote System Discovery", "tactic": "Discovery", "tactic_id": "TA0007", "severity": "medium", "score": 5.5, "kill_chain_phase": "discovery"},
    {"technique_id": "T1087", "name": "Account Discovery", "tactic": "Discovery", "tactic_id": "TA0007", "severity": "medium", "score": 5.0, "kill_chain_phase": "discovery", "ioc_indicators": ["username"]},
    {"technique_id": "T1518", "name": "Software Discovery", "tactic": "Discovery", "tactic_id": "TA0007", "severity": "low", "score": 4.0, "kill_chain_phase": "discovery"},
    {"technique_id": "T1069", "name": "Permission Groups Discovery", "tactic": "Discovery", "tactic_id": "TA0007", "severity": "medium", "score": 5.0, "kill_chain_phase": "discovery"},

    # === Lateral Movement ===
    {"technique_id": "T1021", "name": "Remote Services", "tactic": "Lateral Movement", "tactic_id": "TA0008", "severity": "high", "score": 8.0, "kill_chain_phase": "lateral-movement"},
    {"technique_id": "T1021.001", "name": "Remote Desktop Protocol", "tactic": "Lateral Movement", "tactic_id": "TA0008", "is_subtechnique": True, "parent_technique_id": "T1021", "severity": "high", "score": 8.0, "kill_chain_phase": "lateral-movement", "detection_rules": ["rdp_brute_force"]},
    {"technique_id": "T1021.002", "name": "SMB/Windows Admin Shares", "tactic": "Lateral Movement", "tactic_id": "TA0008", "is_subtechnique": True, "parent_technique_id": "T1021", "severity": "high", "score": 7.5, "kill_chain_phase": "lateral-movement"},
    {"technique_id": "T1021.004", "name": "SSH", "tactic": "Lateral Movement", "tactic_id": "TA0008", "is_subtechnique": True, "parent_technique_id": "T1021", "severity": "high", "score": 7.5, "kill_chain_phase": "lateral-movement", "detection_rules": ["ssh_brute_force", "ssh_session"]},
    {"technique_id": "T1021.006", "name": "Windows Remote Management", "tactic": "Lateral Movement", "tactic_id": "TA0008", "is_subtechnique": True, "parent_technique_id": "T1021", "severity": "high", "score": 7.0, "kill_chain_phase": "lateral-movement"},
    {"technique_id": "T1570", "name": "Lateral Tool Transfer", "tactic": "Lateral Movement", "tactic_id": "TA0008", "severity": "high", "score": 7.5, "kill_chain_phase": "lateral-movement"},

    # === Collection ===
    {"technique_id": "T1005", "name": "Data from Local System", "tactic": "Collection", "tactic_id": "TA0009", "severity": "medium", "score": 6.0, "kill_chain_phase": "collection"},
    {"technique_id": "T1074", "name": "Data Staged", "tactic": "Collection", "tactic_id": "TA0009", "severity": "medium", "score": 6.0, "kill_chain_phase": "collection"},
    {"technique_id": "T1114", "name": "Email Collection", "tactic": "Collection", "tactic_id": "TA0009", "severity": "high", "score": 7.0, "kill_chain_phase": "collection"},
    {"technique_id": "T1115", "name": "Clipboard Data", "tactic": "Collection", "tactic_id": "TA0009", "severity": "low", "score": 4.0, "kill_chain_phase": "collection"},
    {"technique_id": "T1119", "name": "Automated Collection", "tactic": "Collection", "tactic_id": "TA0009", "severity": "medium", "score": 5.5, "kill_chain_phase": "collection"},
    {"technique_id": "T1056", "name": "Input Capture", "tactic": "Collection", "tactic_id": "TA0009", "severity": "high", "score": 7.0, "kill_chain_phase": "collection"},

    # === Command and Control ===
    {"technique_id": "T1071", "name": "Application Layer Protocol", "tactic": "Command and Control", "tactic_id": "TA0011", "severity": "high", "score": 8.0, "kill_chain_phase": "command-and-control", "ioc_indicators": ["domain", "url", "ipv4"]},
    {"technique_id": "T1071.001", "name": "Web Protocols", "tactic": "Command and Control", "tactic_id": "TA0011", "is_subtechnique": True, "parent_technique_id": "T1071", "severity": "high", "score": 8.0, "kill_chain_phase": "command-and-control", "ioc_indicators": ["url", "domain"]},
    {"technique_id": "T1071.004", "name": "DNS", "tactic": "Command and Control", "tactic_id": "TA0011", "is_subtechnique": True, "parent_technique_id": "T1071", "severity": "high", "score": 7.5, "kill_chain_phase": "command-and-control", "ioc_indicators": ["domain"]},
    {"technique_id": "T1573", "name": "Encrypted Channel", "tactic": "Command and Control", "tactic_id": "TA0011", "severity": "high", "score": 7.5, "kill_chain_phase": "command-and-control"},
    {"technique_id": "T1573.001", "name": "Symmetric Cryptography", "tactic": "Command and Control", "tactic_id": "TA0011", "is_subtechnique": True, "parent_technique_id": "T1573", "severity": "high", "score": 7.0, "kill_chain_phase": "command-and-control"},
    {"technique_id": "T1102", "name": "Web Service", "tactic": "Command and Control", "tactic_id": "TA0011", "severity": "medium", "score": 6.5, "kill_chain_phase": "command-and-control"},
    {"technique_id": "T1095", "name": "Non-Application Layer Protocol", "tactic": "Command and Control", "tactic_id": "TA0011", "severity": "medium", "score": 6.0, "kill_chain_phase": "command-and-control"},
    {"technique_id": "T1105", "name": "Ingress Tool Transfer", "tactic": "Command and Control", "tactic_id": "TA0011", "severity": "high", "score": 8.0, "kill_chain_phase": "command-and-control", "ioc_indicators": ["md5", "sha1", "sha256", "executable_path"]},
    {"technique_id": "T1568", "name": "Dynamic Resolution", "tactic": "Command and Control", "tactic_id": "TA0011", "severity": "medium", "score": 6.5, "kill_chain_phase": "command-and-control", "ioc_indicators": ["domain"]},

    # === Exfiltration ===
    {"technique_id": "T1048", "name": "Exfiltration Over Alternative Protocol", "tactic": "Exfiltration", "tactic_id": "TA0010", "severity": "high", "score": 8.0, "kill_chain_phase": "exfiltration"},
    {"technique_id": "T1041", "name": "Exfiltration Over C2 Channel", "tactic": "Exfiltration", "tactic_id": "TA0010", "severity": "high", "score": 7.5, "kill_chain_phase": "exfiltration"},
    {"technique_id": "T1567", "name": "Exfiltration Over Web Service", "tactic": "Exfiltration", "tactic_id": "TA0010", "severity": "high", "score": 7.5, "kill_chain_phase": "exfiltration"},
    {"technique_id": "T1537", "name": "Transfer Data to Cloud Account", "tactic": "Exfiltration", "tactic_id": "TA0010", "severity": "high", "score": 7.0, "kill_chain_phase": "exfiltration"},
    {"technique_id": "T1052", "name": "Exfiltration Over Physical Medium", "tactic": "Exfiltration", "tactic_id": "TA0010", "severity": "medium", "score": 5.0, "kill_chain_phase": "exfiltration"},

    # === Impact ===
    {"technique_id": "T1485", "name": "Data Destruction", "tactic": "Impact", "tactic_id": "TA0040", "severity": "critical", "score": 9.5, "kill_chain_phase": "impact"},
    {"technique_id": "T1486", "name": "Data Encrypted for Impact", "tactic": "Impact", "tactic_id": "TA0040", "severity": "critical", "score": 10.0, "kill_chain_phase": "impact"},
    {"technique_id": "T1490", "name": "Inhibit System Recovery", "tactic": "Impact", "tactic_id": "TA0040", "severity": "critical", "score": 9.0, "kill_chain_phase": "impact"},
    {"technique_id": "T1499", "name": "Endpoint Denial of Service", "tactic": "Impact", "tactic_id": "TA0040", "severity": "high", "score": 8.0, "kill_chain_phase": "impact"},
    {"technique_id": "T1499.001", "name": "OS Exhaustion Flood", "tactic": "Impact", "tactic_id": "TA0040", "is_subtechnique": True, "parent_technique_id": "T1499", "severity": "high", "score": 7.5, "kill_chain_phase": "impact"},
    {"technique_id": "T1499.002", "name": "Service Exhaustion Flood", "tactic": "Impact", "tactic_id": "TA0040", "is_subtechnique": True, "parent_technique_id": "T1499", "severity": "high", "score": 7.5, "kill_chain_phase": "impact", "detection_rules": ["port_scan", "firewall_block"]},
    {"technique_id": "T1565", "name": "Data Manipulation", "tactic": "Impact", "tactic_id": "TA0040", "severity": "high", "score": 8.0, "kill_chain_phase": "impact"},
    {"technique_id": "T1491", "name": "Defacement", "tactic": "Impact", "tactic_id": "TA0040", "severity": "medium", "score": 5.0, "kill_chain_phase": "impact"},
]
