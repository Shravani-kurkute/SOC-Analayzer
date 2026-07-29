import ipaddress
import re


class IocNormalizer:
    @staticmethod
    def normalize(ioc_type: str, value: str) -> str:
        normalizers = {
            "ipv4": IocNormalizer._normalize_ipv4,
            "ipv6": IocNormalizer._normalize_ipv6,
            "domain": lambda v: v.lower().strip("."),
            "url": lambda v: v.rstrip("/").lower(),
            "hostname": lambda v: v.lower().strip("."),
            "email": lambda v: v.lower().strip(),
            "username": lambda v: v.strip(),
            "md5": lambda v: v.lower().strip(),
            "sha1": lambda v: v.lower().strip(),
            "sha256": lambda v: v.lower().strip(),
            "registry_key": lambda v: v.upper().strip(),
            "windows_sid": lambda v: v.upper().strip(),
            "process_name": lambda v: v.lower().strip(),
            "executable_path": lambda v: v.strip(),
            "command_line": lambda v: v.strip(),
            "cve": lambda v: v.upper().strip(),
            "mitre_technique": lambda v: v.upper().strip(),
            "port": lambda v: str(int(v.strip())),
            "protocol": lambda v: v.upper().strip(),
        }
        normalizer = normalizers.get(ioc_type, lambda v: v.strip())
        return normalizer(value)

    @staticmethod
    def _normalize_ipv4(value: str) -> str:
        try:
            return str(ipaddress.IPv4Address(value))
        except ValueError:
            return value.strip()

    @staticmethod
    def _normalize_ipv6(value: str) -> str:
        try:
            return str(ipaddress.IPv6Address(value).compressed)
        except ValueError:
            return value.strip()
