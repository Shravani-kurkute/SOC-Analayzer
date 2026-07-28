from dataclasses import dataclass, field
from datetime import timedelta
from typing import Any


@dataclass
class CorrelationRule:
    name: str
    description: str
    group_type: str
    time_window: timedelta
    match_fields: list[str]
    min_events: int = 2
    require_sequence: bool = False
    sequence_fields: list[str] | None = None
    risk_weights: dict[str, float] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


SSH_BRUTE_FORCE = CorrelationRule(
    name="ssh_brute_force",
    description="Failed SSH logins followed by successful login from same source IP",
    group_type="ssh_session",
    time_window=timedelta(minutes=30),
    match_fields=["source_ip"],
    min_events=3,
    require_sequence=True,
    sequence_fields=["action"],
    risk_weights={"failed_password": 0.3, "accepted": 0.6},
    metadata={"attack_chain": ["reconnaissance", "credential_access", "initial_access"]},
)

PORT_SCAN = CorrelationRule(
    name="port_scan",
    description="Multiple connection attempts to different ports from same source IP",
    group_type="port_scan",
    time_window=timedelta(minutes=10),
    match_fields=["source_ip", "destination_ip"],
    min_events=5,
    metadata={"attack_chain": ["reconnaissance"]},
)

FIREWALL_EVENTS = CorrelationRule(
    name="firewall_denies",
    description="Multiple firewall deny events from same source",
    group_type="firewall_block",
    time_window=timedelta(minutes=15),
    match_fields=["source_ip"],
    min_events=3,
    metadata={"attack_chain": ["reconnaissance", "defense_evasion"]},
)

WEB_ATTACK = CorrelationRule(
    name="web_attack",
    description="Multiple web attack patterns from same source IP",
    group_type="web_attack",
    time_window=timedelta(minutes=30),
    match_fields=["source_ip"],
    min_events=2,
    require_sequence=True,
    sequence_fields=["action"],
    risk_weights={"sql_injection": 0.8, "path_traversal": 0.7, "xss": 0.6, "command_execution": 0.9},
    metadata={"attack_chain": ["initial_access", "execution"]},
)

APACHE_ERROR_CHAIN = CorrelationRule(
    name="apache_error_chain",
    description="Apache errors followed by access attempts from same source",
    group_type="web_error_chain",
    time_window=timedelta(minutes=15),
    match_fields=["source_ip"],
    min_events=2,
    require_sequence=True,
    sequence_fields=["action", "event_source"],
    metadata={"attack_chain": ["reconnaissance", "initial_access"]},
)

MIXED_ATTACK = CorrelationRule(
    name="mixed_attack",
    description="Events across different sources with same IP forming an attack chain",
    group_type="attack_chain",
    time_window=timedelta(minutes=60),
    match_fields=["source_ip", "username"],
    min_events=3,
    metadata={"attack_chain": ["multiple_tactics"]},
)

LOGIN_SPIKE = CorrelationRule(
    name="login_spike",
    description="Rapid login attempts across different usernames from same IP",
    group_type="credential_stuffing",
    time_window=timedelta(minutes=5),
    match_fields=["source_ip"],
    min_events=10,
    metadata={"attack_chain": ["credential_access"]},
)

SAME_USER_ANOMALY = CorrelationRule(
    name="same_user_anomaly",
    description="Same user appearing from multiple source IPs in short time",
    group_type="credential_compromise",
    time_window=timedelta(minutes=30),
    match_fields=["username"],
    min_events=2,
    metadata={"attack_chain": ["credential_access", "lateral_movement"]},
)

HOSTNAME_BASED = CorrelationRule(
    name="hostname_based",
    description="Events targeting the same hostname from different sources",
    group_type="targeted_attack",
    time_window=timedelta(minutes=60),
    match_fields=["hostname", "destination_ip"],
    min_events=3,
    metadata={"attack_chain": ["multiple_tactics"]},
)


class CorrelationRuleRegistry:
    _rules: dict[str, CorrelationRule] = {}

    @classmethod
    def register(cls, rule: CorrelationRule) -> None:
        cls._rules[rule.name] = rule

    @classmethod
    def get(cls, name: str) -> CorrelationRule | None:
        return cls._rules.get(name)

    @classmethod
    def get_all(cls) -> list[CorrelationRule]:
        return list(cls._rules.values())

    @classmethod
    def get_by_group_type(cls, group_type: str) -> list[CorrelationRule]:
        return [r for r in cls._rules.values() if r.group_type == group_type]


CorrelationRuleRegistry.register(SSH_BRUTE_FORCE)
CorrelationRuleRegistry.register(PORT_SCAN)
CorrelationRuleRegistry.register(FIREWALL_EVENTS)
CorrelationRuleRegistry.register(WEB_ATTACK)
CorrelationRuleRegistry.register(APACHE_ERROR_CHAIN)
CorrelationRuleRegistry.register(MIXED_ATTACK)
CorrelationRuleRegistry.register(LOGIN_SPIKE)
CorrelationRuleRegistry.register(SAME_USER_ANOMALY)
CorrelationRuleRegistry.register(HOSTNAME_BASED)
