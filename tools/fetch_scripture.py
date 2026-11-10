#!/usr/bin/env python3
"""Download the full public-domain text of Mark and save it as JSON.

Source: eBible.org (free Bible texts in USFM format).
  en-bsb      Berean Standard Bible (public domain since 2023)   https://ebible.org/Scriptures/engbsb_usfm.zip
  ru-synodal  Russian Synodal Translation (1876, public domain)  https://ebible.org/Scriptures/russyn_usfm.zip

This needs internet access to ebible.org (it is blocked in some cloud
sandboxes; run it on your own computer or allow the host).

Usage:  python3 tools/fetch_scripture.py [en-bsb] [ru-synodal]
Check the zip names on https://ebible.org/download.php if a download fails.
"""
import io
import json
import re
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCES = {
    "en-bsb": ("https://ebible.org/Scriptures/engbsb_usfm.zip", "Berean Standard Bible", "BSB",
               "Public domain (dedicated by Bible Hub, 2023)."),
    "ru-synodal": ("https://ebible.org/Scriptures/russyn_usfm.zip", "Синодальный перевод (1876)", "SYN",
                   "Общественное достояние."),
}


def clean(t):
    t = re.sub(r"\\f .*?\\f\*", "", t)            # footnotes
    t = re.sub(r"\\x .*?\\x\*", "", t)            # cross references
    t = re.sub(r"\\w ([^|\\]*)\|[^\\]*\\w\*", r"\1", t)  # word attributes
    t = re.sub(r"\\\+?[a-z0-9]+\*?", "", t)       # other markers
    return re.sub(r"\s+", " ", t).strip()


def parse_mark(usfm):
    chapters, ch, cur = {}, None, None
    for line in usfm.splitlines():
        m = re.match(r"\\c (\d+)", line)
        if m:
            ch = m.group(1)
            chapters[ch] = {}
            continue
        for vm in re.finditer(r"\\v (\d+)\s+(.*?)(?=\\v \d+|$)", line):
            cur = vm.group(1)
            chapters[ch][cur] = clean(vm.group(2))
        if not line.startswith(("\\v", "\\c", "\\s", "\\id", "\\h", "\\toc", "\\mt", "\\r")) and cur and ch:
            extra = clean(line)
            if extra:
                chapters[ch][cur] = (chapters[ch][cur] + " " + extra).strip()
    return chapters


def fetch(key):
    url, name, abbr, lic = SOURCES[key]
    print("download", url)
    raw = urllib.request.urlopen(url, timeout=60).read()
    z = zipfile.ZipFile(io.BytesIO(raw))
    mark = next(n for n in z.namelist() if re.search(r"MRK", n, re.I))
    chapters = parse_mark(z.read(mark).decode("utf-8-sig"))
    out = ROOT / "data/scripture" / key / "mark.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({"book": "Mark", "translation": name, "abbr": abbr, "license": lic,
                               "source": url, "verify": False, "chapters": chapters}, ensure_ascii=False, indent=1))
    print(key, "->", out, sum(len(v) for v in chapters.values()), "verses")


if __name__ == "__main__":
    for k in sys.argv[1:] or list(SOURCES):
        fetch(k)
