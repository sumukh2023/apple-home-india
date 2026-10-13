#!/usr/bin/env python3
"""Fail if the repo contains personal or secret data.

Generic checks: emails, private IP addresses, MAC addresses, tokens, long hex keys,
Nabu Casa webhook URLs. Personal words (names, house name, etc.) are read from
tools/private_words.local.txt, which is git-ignored so the list itself stays private.

Usage: python3 tools/privacy_scan.py [repo_root]
"""
import pathlib, re, sys

ROOT = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
SKIP_DIRS = {".git"}
SKIP_FILES = {"LICENSE", "privacy_scan.py"}
TEXT_EXT = {".yaml", ".yml", ".md", ".py", ".txt", ".json", ".sh", ""}

PATTERNS = {
    "email address": r"[\w.+-]+@[\w-]+\.[\w.]+",
    "private IP address": r"\b(?:192\.168|10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}\b",
    "MAC address": r"\b(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}\b",
    "JWT / access token": r"eyJ[\w-]{10,}\.[\w-]{10,}",
    "long hex key": r"\b[0-9a-fA-F]{32,}\b",
    "Nabu Casa webhook": r"hooks\.nabu\.casa",
    "Tuya local key": r"(?i)local[_ ]?key\s*[:=]\s*\S{8,}",
    "Tuya device id": r"\b[0-9a-z]{20,22}\b(?=.*(?i:device|dev_id|id))",
}
ALLOWED_LINE = re.compile(r"^\s*author:\s")  # blueprint author credit
# The author's full name is allowed in the README only (About the author, License).
AUTHOR_NAME = {"README.md": "sumukh nayak"}

words_file = ROOT / "tools" / "private_words.local.txt"
private_words = []
if words_file.exists():
    private_words = [w.strip().lower() for w in words_file.read_text().splitlines()
                     if w.strip() and not w.startswith("#")]
else:
    print(f"warning: {words_file.relative_to(ROOT)} not found; personal-word check skipped")

problems = 0
for path in sorted(ROOT.rglob("*")):
    if (not path.is_file() or path.name in SKIP_FILES or path.name.endswith(".local.txt")
            or any(p in SKIP_DIRS for p in path.parts) or path.suffix not in TEXT_EXT):
        continue
    rel = path.relative_to(ROOT)
    for n, line in enumerate(path.read_text(errors="ignore").splitlines(), 1):
        if ALLOWED_LINE.match(line):
            continue
        for label, rx in PATTERNS.items():
            if re.search(rx, line):
                print(f"{rel}:{n}: {label}"); problems += 1
        low = line.lower()
        if str(rel) in AUTHOR_NAME:
            low = low.replace(AUTHOR_NAME[str(rel)], "")
        for w in private_words:
            if w in low:
                print(f"{rel}:{n}: personal word"); problems += 1

print(f"{problems} problem(s) found" if problems else "privacy scan: clean")
sys.exit(1 if problems else 0)
