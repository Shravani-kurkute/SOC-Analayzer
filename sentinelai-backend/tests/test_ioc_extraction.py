"""Test IOC extraction from various log sources."""

from app.ioc.extractors import IocExtractor


def test_all_ioc_types():
    e = IocExtractor()

    tests = [
        ("ipv4", "Connection from 8.8.8.8 to 1.1.1.1", ["8.8.8.8", "1.1.1.1"]),
        ("ipv6", "IPv6 address 2001:db8::1 detected", ["2001:db8::1"]),
        ("domain", "Connection to malicious.example.com", ["malicious.example.com"]),
        ("url", "Download from http://evil.com/payload.exe", ["http://evil.com/payload.exe"]),
        ("email", "Alert sent to admin@example.com", ["admin@example.com"]),
        ("username", "Login attempt user=root from 10.0.0.1", ["root"]),
        ("md5", "File hash d41d8cd98f00b204e9800998ecf8427e", ["d41d8cd98f00b204e9800998ecf8427e"]),
        ("sha1", "SHA1 a9993e364706816aba3e25717850c26c9cd0d89d", ["a9993e364706816aba3e25717850c26c9cd0d89d"]),
        ("sha256", "SHA256 " + "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", ["e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"]),
        ("windows_sid", "User SID S-1-5-21-3623811015-3361044348-30300820-1013", ["S-1-5-21-3623811015-3361044348-30300820-1013"]),
        ("cve", "Vulnerability CVE-2024-3094 detected", ["CVE-2024-3094"]),
        ("mitre_technique", "Technique T1059.001 detected", ["T1059.001"]),
        ("protocol", "Protocol: SSH, DNS, HTTP", ["SSH", "DNS", "HTTP"]),
    ]

    all_pass = True
    for ioc_type, text, expected in tests:
        iocs = e.extract_all(text)
        extracted = [i["ioc_value"] for i in iocs if i["ioc_type"] == ioc_type]
        extracted_set = set(extracted)
        expected_set = set(expected)

        if expected_set - extracted_set:
            print(f"FAIL [{ioc_type}]: Missing {expected_set - extracted_set}")
            print(f"  Text: {text}")
            print(f"  Got: {extracted}")
            all_pass = False
        elif extracted_set - expected_set:
            print(f"WARN [{ioc_type}]: Extra {extracted_set - expected_set}")
        else:
            print(f"PASS [{ioc_type}]: {extracted}")

    assert all_pass
    print(f"\nAll type tests passed: {all_pass}")


def test_auth_log():
    e = IocExtractor()
    auth_log = (
        "Jul 28 12:34:56 server sshd[1234]: Failed password for root from 192.168.1.100 port 22 ssh2\n"
        "Jul 28 12:35:10 server sshd[1234]: Connection from 10.0.0.50 port 54321\n"
        "User admin logged in from host management.example.com\n"
        "CVE-2024-1234 detected in /usr/bin/sshd\n"
        "Running chmod +x /tmp/exploit.sh"
    )
    iocs = e.extract_all(auth_log)
    types = {i["ioc_type"] for i in iocs}
    print(f"Auth log: Extracted {len(iocs)} IOCs: {types}")
    for i in iocs:
        print(f"  [{i['ioc_type']}] {i['ioc_value']}")
    assert len(iocs) > 0


def test_apache_log():
    e = IocExtractor()
    apache_log = (
        '192.168.1.100 - - [28/Jul/2024:12:34:56 +0000] "GET /wp-admin/admin-ajax.php HTTP/1.1" 404 1234 "-" "Mozilla/5.0"\n'
        '10.0.0.50 - admin [28/Jul/2024:12:35:10 +0000] "POST /login.php HTTP/1.1" 200 5678 "http://evil.com" "curl/7.68.0"'
    )
    iocs = e.extract_all(apache_log)
    print(f"Apache log: Extracted {len(iocs)} IOCs:")
    for i in iocs:
        print(f"  [{i['ioc_type']}] {i['ioc_value']}")
    assert len(iocs) > 0


def test_firewall_log():
    e = IocExtractor()
    fw_log = (
        "2024-07-28T12:34:56Z firewall: BLOCK src=192.168.1.100 dst=10.0.0.1 port=443 proto=TCP\n"
        "2024-07-28T12:35:10Z firewall: ALERT src=10.0.0.50 dst=203.0.113.5 port=80 proto=UDP"
    )
    iocs = e.extract_all(fw_log)
    print(f"Firewall log: Extracted {len(iocs)} IOCs:")
    for i in iocs:
        print(f"  [{i['ioc_type']}] {i['ioc_value']}")
    assert len(iocs) > 0


def test_windows_event():
    e = IocExtractor()
    win_log = (
        "Security Event 4625: Logon Failure\n"
        "Account: Administrator\n"
        "Source IP: 192.168.1.100\n"
        "Process: C:\\Windows\\System32\\svchost.exe\n"
        "Hash: d41d8cd98f00b204e9800998ecf8427e\n"
        "SID: S-1-5-21-3623811015-3361044348-30300820-500"
    )
    iocs = e.extract_all(win_log)
    print(f"Windows log: Extracted {len(iocs)} IOCs:")
    for i in iocs:
        print(f"  [{i['ioc_type']}] {i['ioc_value']}")
    assert len(iocs) > 0


def test_duplicate_handling():
    e = IocExtractor()
    text = "Connecting to 8.8.8.8 and 8.8.8.8 and 8.8.8.8"
    iocs = e.extract_all(text)
    ipv4_iocs = [i for i in iocs if i["ioc_type"] == "ipv4"]
    assert len(ipv4_iocs) == 1, f"Expected 1 unique IPv4, got {len(ipv4_iocs)}"
    print(f"Duplicate handling: {len(ipv4_iocs)} unique (expected 1)")


if __name__ == "__main__":
    test_all_ioc_types()
    test_auth_log()
    test_apache_log()
    test_firewall_log()
    test_windows_event()
    test_duplicate_handling()
    print("\nAll IOC extraction tests passed!")
