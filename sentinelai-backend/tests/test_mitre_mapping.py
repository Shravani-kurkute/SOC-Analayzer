"""Test MITRE ATT&CK mapping engine."""

from app.mitre.data import MITRE_TECHNIQUES
from app.mitre.mapping_engine import (
    DETECTION_RULE_MAP,
    IOC_TYPE_MAP,
    CORRELATION_TYPE_MAP,
    MappingEngine,
)


def test_all_tactics_present():
    tactics = {t["tactic"] for t in MITRE_TECHNIQUES}
    expected = {
        "Initial Access", "Execution", "Persistence",
        "Privilege Escalation", "Defense Evasion",
        "Credential Access", "Discovery", "Lateral Movement",
        "Collection", "Command and Control", "Exfiltration", "Impact",
    }
    assert tactics == expected, f"Missing tactics: {expected - tactics}"
    print(f"[PASS] All 12 tactics present: {len(tactics)}")


def test_all_technique_ids_unique():
    ids = [t["technique_id"] for t in MITRE_TECHNIQUES]
    assert len(ids) == len(set(ids)), "Duplicate technique IDs found"
    print(f"[PASS] All {len(ids)} technique IDs unique")


def test_detection_rule_mappings():
    assert "ssh_brute_force" in DETECTION_RULE_MAP
    assert "port_scan" in DETECTION_RULE_MAP
    assert "web_attack" in DETECTION_RULE_MAP
    assert "brute_force" in DETECTION_RULE_MAP
    assert "credential_stuffing" in DETECTION_RULE_MAP
    for rule, techniques in DETECTION_RULE_MAP.items():
        assert len(techniques) > 0, f"No techniques for {rule}"
    print(f"[PASS] {len(DETECTION_RULE_MAP)} detection rule mappings")


def test_ioc_type_mappings():
    assert "ipv4" in IOC_TYPE_MAP
    assert "domain" in IOC_TYPE_MAP
    assert "url" in IOC_TYPE_MAP
    assert "cve" in IOC_TYPE_MAP
    assert "email" in IOC_TYPE_MAP
    assert "username" in IOC_TYPE_MAP
    for ioc_type, techniques in IOC_TYPE_MAP.items():
        assert len(techniques) > 0, f"No techniques for {ioc_type}"
    print(f"[PASS] {len(IOC_TYPE_MAP)} IOC type mappings")


def test_correlation_type_mappings():
    assert "ssh_session" in CORRELATION_TYPE_MAP
    assert "port_scan" in CORRELATION_TYPE_MAP
    assert "web_attack" in CORRELATION_TYPE_MAP
    assert "credential_stuffing" in CORRELATION_TYPE_MAP
    for group_type, techniques in CORRELATION_TYPE_MAP.items():
        assert len(techniques) > 0, f"No techniques for {group_type}"
    print(f"[PASS] {len(CORRELATION_TYPE_MAP)} correlation group mappings")


def test_context_detection():
    engine = MappingEngine()
    contexts = {
        "ssh brute force attack detected": ["T1021.004", "T1133", "T1110", "T1078"],
        "port scan from external IP": ["T1046"],
        "SQL injection on login page": ["T1190"],
        "powershell -enc command executed": ["T1059.001"],
        "malware detected with ransomware behavior": ["T1204.002", "T1105", "T1486", "T1485"],
        "registry key modification detected": ["T1547.001"],
    }
    for context, expected_techniques in contexts.items():
        result = engine._detect_from_context(context)
        for t in expected_techniques:
            assert t in result, f"Missing {t} for context: {context}"
    print(f"[PASS] Context detection: {len(contexts)} scenarios")


def test_kill_chain_phases():
    expected_phases = {
        "initial-access", "execution", "persistence",
        "privilege-escalation", "defense-evasion", "credential-access",
        "discovery", "lateral-movement", "collection",
        "command-and-control", "exfiltration", "impact",
    }
    phases = {t.get("kill_chain_phase") for t in MITRE_TECHNIQUES if t.get("kill_chain_phase")}
    assert phases == expected_phases, f"Missing phases: {expected_phases - phases}"
    print(f"[PASS] Kill chain phases: {len(phases)}")


if __name__ == "__main__":
    test_all_tactics_present()
    test_all_technique_ids_unique()
    test_detection_rule_mappings()
    test_ioc_type_mappings()
    test_correlation_type_mappings()
    test_context_detection()
    test_kill_chain_phases()
    print("\nAll MITRE mapping tests passed!")
