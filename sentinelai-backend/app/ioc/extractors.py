import ipaddress
import re
from typing import Any

from app.ioc.normalizer import IocNormalizer

IPV4_RE = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\b")
IPV6_RE = re.compile(r"\b(?:[A-Fa-f0-9]{1,4}:){7}[A-Fa-f0-9]{1,4}\b|\b(?:[A-Fa-f0-9]{1,4}:){1,6}:(?:[A-Fa-f0-9]{1,4})?\b|\b::(?:[A-Fa-f0-9]{1,4}:){0,6}[A-Fa-f0-9]{1,4}\b")
DOMAIN_RE = re.compile(r"\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}\b")
URL_RE = re.compile(r"https?://[^\s<>\"']+|ftp://[^\s<>\"']+")
HOSTNAME_RE = re.compile(r"\b(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+[a-zA-Z]{2,}(?::\d+)?\b")
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
USERNAME_RE = re.compile(r"\buser[=:]\s*(\w+)\b|\busername[=:]\s*(\w+)\b|\buid[=:]\s*(\w+)\b|\blogin[=:]\s*(\w+)\b", re.IGNORECASE)
MD5_RE = re.compile(r"\b[a-fA-F0-9]{32}\b")
SHA1_RE = re.compile(r"\b[a-fA-F0-9]{40}\b")
SHA256_RE = re.compile(r"\b[a-fA-F0-9]{64}\b")
REGISTRY_KEY_RE = re.compile(r"[A-Z]+\\[A-Za-z0-9_\\]+(?:\\[A-Za-z0-9_]+)+")
WINDOWS_SID_RE = re.compile(r"\bS-\d-\d+(?:-\d+){1,}\b")
PROCESS_NAME_RE = re.compile(r"\b(?:[a-zA-Z0-9_]+\.exe|[a-zA-Z0-9_]+\.dll|[a-zA-Z0-9_]+\.ps1|python[23]?\b|bash\b|sh\b|powershell\.exe|cmd\.exe|ssh[d]?|nginx|apache2?|httpd|mysqld|dockerd|kubelet)\b")
EXECUTABLE_PATH_RE = re.compile(r"(?:/usr|/etc|/var|/opt|/home|/tmp|C:\\|/bin|/sbin|/lib)[^\s<>\"'|;]+")
COMMAND_LINE_RE = re.compile(r"(?:wget|curl|nc\s|bash\s-i|python\s-c|perl\s-e|ruby\s-e|chmod\s\+x|chown\s|useradd\s|adduser\s|usermod\s)[^\n\r]+", re.IGNORECASE)
CVE_RE = re.compile(r"\bCVE-\d{4}-\d{4,7}\b", re.IGNORECASE)
MITRE_TECHNIQUE_RE = re.compile(r"\bT\d{4}(?:\.\d{3})?\b")
PORT_RE = re.compile(r"(?:port|PORT|dst_port|src_port)[=:]\s*(\d{1,5})\b")
PROTOCOL_RE = re.compile(r"\b(TCP|UDP|ICMP|HTTP|HTTPS|FTP|SSH|SMTP|DNS|DHCP|ARP|SMB|RDP|TLS|SSL)\b")


class IocExtractor:
    def extract_all(self, text: str, event: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        iocs: list[dict[str, Any]] = []
        seen: set[str] = set()
        extractors = [
            ("ipv4", self._extract_ipv4),
            ("ipv6", self._extract_ipv6),
            ("domain", self._extract_domain),
            ("url", self._extract_url),
            ("hostname", self._extract_hostname),
            ("email", self._extract_email),
            ("username", self._extract_username),
            ("md5", self._extract_md5),
            ("sha1", self._extract_sha1),
            ("sha256", self._extract_sha256),
            ("registry_key", self._extract_registry_key),
            ("windows_sid", self._extract_windows_sid),
            ("process_name", self._extract_process_name),
            ("executable_path", self._extract_executable_path),
            ("command_line", self._extract_command_line),
            ("cve", self._extract_cve),
            ("mitre_technique", self._extract_mitre_technique),
            ("port", self._extract_port),
            ("protocol", self._extract_protocol),
        ]
        for ioc_type, extractor in extractors:
            for value in extractor(text):
                key = f"{ioc_type}:{value}"
                if key not in seen:
                    seen.add(key)
                    iocs.append({
                        "ioc_type": ioc_type,
                        "ioc_value": value,
                        "normalized_value": IocNormalizer.normalize(ioc_type, value),
                    })
        return iocs

    def _extract_ipv4(self, text: str) -> list[str]:
        matches = IPV4_RE.findall(text)
        return [m for m in matches if not self._is_private_or_reserved(m)]

    def _extract_ipv6(self, text: str) -> list[str]:
        matches = IPV6_RE.findall(text)
        valid = []
        for m in matches:
            try:
                ipaddress.IPv6Address(m)
                valid.append(m)
            except ValueError:
                pass
        return valid

    def _extract_domain(self, text: str) -> list[str]:
        matches = DOMAIN_RE.findall(text)
        return [m.lower() for m in matches if not self._is_ip(m) and "." in m and not m.startswith(".") and not m.endswith(".")]

    def _extract_url(self, text: str) -> list[str]:
        return list(set(URL_RE.findall(text)))

    def _extract_hostname(self, text: str) -> list[str]:
        matches = HOSTNAME_RE.findall(text)
        return [m.split(":")[0].lower() for m in matches if not self._is_ip(m) and "." in m]

    def _extract_email(self, text: str) -> list[str]:
        return list(set(EMAIL_RE.findall(text)))

    def _extract_username(self, text: str) -> list[str]:
        matches = USERNAME_RE.findall(text)
        users = []
        for group in matches:
            for g in group:
                if g:
                    users.append(g)
        return list(set(users))

    def _extract_md5(self, text: str) -> list[str]:
        return list(set(MD5_RE.findall(text)))

    def _extract_sha1(self, text: str) -> list[str]:
        return list(set(SHA1_RE.findall(text)))

    def _extract_sha256(self, text: str) -> list[str]:
        return list(set(SHA256_RE.findall(text)))

    def _extract_registry_key(self, text: str) -> list[str]:
        return list(set(REGISTRY_KEY_RE.findall(text)))

    def _extract_windows_sid(self, text: str) -> list[str]:
        return list(set(WINDOWS_SID_RE.findall(text)))

    def _extract_process_name(self, text: str) -> list[str]:
        return list(set(PROCESS_NAME_RE.findall(text)))

    def _extract_executable_path(self, text: str) -> list[str]:
        return list(set(EXECUTABLE_PATH_RE.findall(text)))

    def _extract_command_line(self, text: str) -> list[str]:
        return list(set(COMMAND_LINE_RE.findall(text)))

    def _extract_cve(self, text: str) -> list[str]:
        return list(set(m.upper() for m in CVE_RE.findall(text)))

    def _extract_mitre_technique(self, text: str) -> list[str]:
        return list(set(MITRE_TECHNIQUE_RE.findall(text)))

    def _extract_port(self, text: str) -> list[str]:
        matches = PORT_RE.findall(text)
        return [m for m in matches if 1 <= int(m) <= 65535]

    def _extract_protocol(self, text: str) -> list[str]:
        return list(set(PROTOCOL_RE.findall(text)))

    def _is_ip(self, value: str) -> bool:
        try:
            ipaddress.ip_address(value)
            return True
        except ValueError:
            return False

    def _is_private_or_reserved(self, ip: str) -> bool:
        try:
            addr = ipaddress.ip_address(ip)
            return addr.is_private or addr.is_loopback or addr.is_link_local or addr.is_multicast or addr.is_reserved
        except ValueError:
            return False
