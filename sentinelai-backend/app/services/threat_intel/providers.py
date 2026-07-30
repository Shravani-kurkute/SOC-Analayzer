import abc
import structlog
from datetime import datetime, timezone
from typing import Any

logger = structlog.get_logger(__name__)


class BaseProvider(abc.ABC):
    name: str = ""
    enabled: bool = True

    @abc.abstractmethod
    async def lookup(self, ioc_type: str, ioc_value: str) -> dict[str, Any] | None:
        ...

    def is_enabled(self) -> bool:
        return self.enabled and self._check_credentials()

    def _check_credentials(self) -> bool:
        return True

    def _parse_result(self, raw: dict[str, Any] | None) -> dict[str, Any]:
        return {
            "reputation": None,
            "confidence": 0.0,
            "malicious": False,
            "categories": None,
            "raw_response": raw,
        }


class MockProvider(BaseProvider):
    name = "mock"

    async def lookup(self, ioc_type: str, ioc_value: str) -> dict[str, Any] | None:
        import random
        is_malicious = random.random() < 0.3
        return {
            "reputation": "malicious" if is_malicious else "harmless",
            "confidence": round(random.uniform(0.5, 1.0) if is_malicious else random.uniform(0.0, 0.3), 2),
            "malicious": is_malicious,
            "categories": ["malware"] if is_malicious else [],
            "country": random.choice(["US", "CN", "RU", "DE", "NL", None]),
            "asn": f"AS{random.randint(1000, 65000)}",
            "asn_org": random.choice(["Cloudflare", "Google", "Amazon", "Microsoft", "DigitalOcean"]),
            "last_analysis": datetime.now(timezone.utc).isoformat(),
            "tags": ["suspicious", "recent"] if is_malicious else [],
            "raw_response": {"source": "mock", "ioc": ioc_value, "type": ioc_type},
        }


class VirusTotalProvider(BaseProvider):
    name = "virustotal"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    def _check_credentials(self) -> bool:
        if not self.api_key:
            logger.warning("VirusTotal API key not configured")
            return False
        return True

    async def lookup(self, ioc_type: str, ioc_value: str) -> dict[str, Any] | None:
        import httpx
        endpoint_map = {
            "ip": f"https://www.virustotal.com/api/v3/ip_addresses/{ioc_value}",
            "domain": f"https://www.virustotal.com/api/v3/domains/{ioc_value}",
            "url": f"https://www.virustotal.com/api/v3/urls/{_encode_url(ioc_value)}",
            "md5": f"https://www.virustotal.com/api/v3/files/{ioc_value}",
            "sha1": f"https://www.virustotal.com/api/v3/files/{ioc_value}",
            "sha256": f"https://www.virustotal.com/api/v3/files/{ioc_value}",
        }
        url = endpoint_map.get(ioc_type)
        if not url:
            return None
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(url, headers={"x-apikey": self.api_key})
                if resp.status_code == 200:
                    data = resp.json().get("data", {}).get("attributes", {})
                    stats = data.get("last_analysis_stats", {})
                    return {
                        "reputation": "malicious" if stats.get("malicious", 0) > 0 else "harmless",
                        "confidence": stats.get("malicious", 0) / max(sum(stats.values()), 1),
                        "malicious": stats.get("malicious", 0) > 0,
                        "malicious_count": stats.get("malicious", 0),
                        "harmless_count": stats.get("harmless", 0),
                        "suspicious_count": stats.get("suspicious", 0),
                        "categories": data.get("categories"),
                        "country": data.get("country"),
                        "asn": f"AS{data.get('asn')}" if data.get("asn") else None,
                        "asn_org": data.get("as_owner"),
                        "last_analysis": data.get("last_analysis_date"),
                        "tags": data.get("tags"),
                        "raw_response": data,
                    }
                elif resp.status_code == 404:
                    return {"reputation": "not_found", "confidence": 0.0, "malicious": False}
                else:
                    logger.error("VirusTotal API error", status=resp.status_code)
                    return None
        except Exception as e:
            logger.error("VirusTotal request failed", error=str(e))
            return None


class AbuseIPDBProvider(BaseProvider):
    name = "abuseipdb"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    def _check_credentials(self) -> bool:
        if not self.api_key:
            logger.warning("AbuseIPDB API key not configured")
            return False
        return True

    async def lookup(self, ioc_type: str, ioc_value: str) -> dict[str, Any] | None:
        if ioc_type not in ("ip", "ipv4", "ipv6"):
            return None
        try:
            import httpx
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(
                    "https://api.abuseipdb.com/api/v2/check",
                    headers={"Key": self.api_key, "Accept": "application/json"},
                    params={"ipAddress": ioc_value, "maxAgeInDays": 90},
                )
                if resp.status_code == 200:
                    data = resp.json().get("data", {})
                    return {
                        "reputation": "malicious" if data.get("abuseConfidenceScore", 0) > 50 else "harmless",
                        "confidence": data.get("abuseConfidenceScore", 0) / 100.0,
                        "malicious": data.get("abuseConfidenceScore", 0) > 50,
                        "malicious_count": data.get("totalReports", 0),
                        "country": data.get("countryCode"),
                        "asn": f"AS{data.get('asn')}" if data.get("asn") else None,
                        "asn_org": data.get("isp"),
                        "last_analysis": data.get("lastReportedAt"),
                        "tags": data.get("categories", []),
                        "raw_response": data,
                    }
                else:
                    logger.error("AbuseIPDB API error", status=resp.status_code)
                    return None
        except Exception as e:
            logger.error("AbuseIPDB request failed", error=str(e))
            return None


class AlienVaultProvider(BaseProvider):
    name = "alienvault"

    def __init__(self, api_key: str | None = None):
        self.api_key = api_key

    def _check_credentials(self) -> bool:
        if not self.api_key:
            logger.warning("AlienVault OTX API key not configured")
            return False
        return True

    async def lookup(self, ioc_type: str, ioc_value: str) -> dict[str, Any] | None:
        type_map = {
            "ip": "IPv4", "ipv4": "IPv4", "ipv6": "IPv6",
            "domain": "domain", "hostname": "domain",
            "md5": "file", "sha1": "file", "sha256": "file",
            "url": "url",
        }
        otx_type = type_map.get(ioc_type)
        if not otx_type:
            return None
        url_map = {
            "IPv4": f"https://otx.alienvault.com/api/v1/indicators/IPv4/{ioc_value}/general",
            "IPv6": f"https://otx.alienvault.com/api/v1/indicators/IPv6/{ioc_value}/general",
            "domain": f"https://otx.alienvault.com/api/v1/indicators/domain/{ioc_value}/general",
            "hostname": f"https://otx.alienvault.com/api/v1/indicators/hostname/{ioc_value}/general",
            "file": f"https://otx.alienvault.com/api/v1/indicators/file/{ioc_value}/general",
            "url": f"https://otx.alienvault.com/api/v1/indicators/url/{ioc_value}/general",
        }
        url = url_map.get(otx_type)
        if not url:
            return None
        try:
            import httpx
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(url, headers={"X-OTX-API-KEY": self.api_key})
                if resp.status_code == 200:
                    data = resp.json()
                    pulse_count = data.get("pulse_info", {}).get("count", 0)
                    return {
                        "reputation": "malicious" if pulse_count > 0 else "harmless",
                        "confidence": min(pulse_count / 10.0, 1.0),
                        "malicious": pulse_count > 0,
                        "malicious_count": pulse_count,
                        "country": data.get("country_code") or data.get("country"),
                        "asn": data.get("asn"),
                        "tags": [p.get("name", "") for p in data.get("pulse_info", {}).get("pulses", [])],
                        "raw_response": data,
                    }
                else:
                    logger.error("AlienVault API error", status=resp.status_code)
                    return None
        except Exception as e:
            logger.error("AlienVault request failed", error=str(e))
            return None


def _encode_url(url: str) -> str:
    import base64
    return base64.urlsafe_b64encode(url.encode()).decode().strip("=")
