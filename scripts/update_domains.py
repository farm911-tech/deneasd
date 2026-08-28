#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Automated Dynamic Domain Resolver for Cloudstream Addons
Scans and validates active domains for:
- RekorTV
- SelcukSports
- Hdfilmcehennemi
- Dizimom

Outputs results to `providers_domains.json`.
"""

import json
import os
import re
import socket
import ssl
import time
import urllib.request
import concurrent.futures
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(BASE_DIR, "providers_domains.json")

# SSL Context for bypassing self-signed or CDN intermediate certificate errors
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
}

def fetch_url(url, timeout=7, headers=None):
    req_headers = HEADERS.copy()
    if headers:
        req_headers.update(headers)
    req = urllib.request.Request(url, headers=req_headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as resp:
            content = resp.read().decode("utf-8", errors="ignore")
            final_url = resp.geturl().rstrip("/")
            return final_url, content, resp.status
    except Exception as e:
        return None, None, None

# -------------------------------------------------------------
# 1. RekorTV Domain Resolver
# -------------------------------------------------------------
def resolve_rekortv(current_known_num=942):
    print("[*] Scanning RekorTV domains...")
    
    # 1. Test current known
    known_url = f"https://rekortv{current_known_num}.com"
    final_url, content, status = fetch_url(known_url, timeout=5)
    if status == 200 and ("single-channel" in content or "real-matches" in content or "data-stream" in content):
        print(f"  [+] RekorTV confirmed at: {final_url}")
        return final_url

    # 2. Parallel scan around known range (+/- 40)
    candidates = list(range(current_known_num - 20, current_known_num + 50))
    
    def check_num(num):
        url = f"https://rekortv{num}.com"
        f_url, c, st = fetch_url(url, timeout=4)
        if st == 200 and c and ("single-channel" in c or "real-matches" in c or "data-stream" in c):
            return f_url or url
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=25) as executor:
        futures = {executor.submit(check_num, n): n for n in candidates}
        for f in concurrent.futures.as_completed(futures):
            res = f.result()
            if res:
                print(f"  [+] RekorTV found: {res}")
                return res

    return known_url

# -------------------------------------------------------------
# 2. SelcukSports Domain Resolver
# -------------------------------------------------------------
def resolve_selcuksports():
    print("[*] Resolving SelcukSports domain...")
    gate_url = "https://www.selcuksportshd.is"
    final_url, content, status = fetch_url(gate_url, timeout=10)
    
    if content:
        # Search for landing link with alt="Site Giriş" or href containing selcuksportshd
        match = re.search(r'href="([^"]+)"[^>]*>[^<]*<img[^>]*alt="[^"]*Site Giriş', content, re.IGNORECASE)
        if not match:
            match = re.search(r'href="([^"]*selcuksportshd[^"]*)"', content, re.IGNORECASE)
            
        if match:
            extracted = match.group(1).rstrip("/")
            if extracted.startswith("http") and not extracted.endswith(".is"):
                print(f"  [+] SelcukSports found: {extracted}")
                return extracted
                
    if final_url and not final_url.endswith(".is") and "selcuksportshd" in final_url:
        print(f"  [+] SelcukSports resolved via redirect: {final_url}")
        return final_url

    default_fallback = "https://www.selcuksportshd0f9c045ffb.xyz"
    print(f"  [-] SelcukSports using fallback: {default_fallback}")
    return default_fallback

# -------------------------------------------------------------
# 3. Hdfilmcehennemi Domain Resolver
# -------------------------------------------------------------
def resolve_hdfilmcehennemi():
    print("[*] Resolving Hdfilmcehennemi domain...")
    gate_candidates = [
        "https://www.hdfilmcehennemi.nl",
        "https://www.hdfilmcehennemi.com",
        "https://www.hdfilmcehennemi.net",
        "https://www.hdfilmcehennemi.life",
        "https://www.hdfilmcehennemi.lat",
        "https://www.hdfilmcehennemi.ws"
    ]
    
    for candidate in gate_candidates:
        final_url, content, status = fetch_url(candidate, timeout=6)
        if status == 200 and content and ("hdfilmcehennemi" in content.lower() or "cehennem" in content.lower()):
            clean = final_url.rstrip("/")
            print(f"  [+] Hdfilmcehennemi active: {clean}")
            return clean

    fallback = "https://www.hdfilmcehennemi.nl"
    print(f"  [-] Hdfilmcehennemi fallback: {fallback}")
    return fallback

# -------------------------------------------------------------
# 4. Dizimom Domain Resolver
# -------------------------------------------------------------
def resolve_dizimom():
    print("[*] Resolving Dizimom domain...")
    candidates = [
        "https://dizimom.com",
        "https://www.dizimom.food",
        "https://www.dizimom.art",
        "https://www.dizimom.site",
        "https://www.dizimom.tv"
    ]
    
    for candidate in candidates:
        final_url, content, status = fetch_url(candidate, timeout=6)
        if status == 200 and content and ("dizimom" in content.lower() or "diziler" in content.lower()):
            clean = final_url.rstrip("/")
            print(f"  [+] Dizimom active: {clean}")
            return clean

    fallback = "https://www.dizimom.food"
    print(f"  [-] Dizimom fallback: {fallback}")
    return fallback

# -------------------------------------------------------------
# 5. Kralbozguncu Domain Resolver
# -------------------------------------------------------------
def resolve_kralbozguncu():
    print("[*] Resolving Kralbozguncu domain...")
    candidates = [
        "https://kralbozguncu.xyz",
        "https://bozguncutv.org",
        "https://kralbozguncutv.com"
    ]
    for c in candidates:
        final_url, content, status = fetch_url(c, timeout=6)
        if status == 200 and content and ("kralbozguncu" in content.lower() or "script2.js" in content):
            clean = final_url.rstrip("/")
            print(f"  [+] Kralbozguncu active: {clean}")
            return clean

    fallback = "https://kralbozguncu.xyz"
    print(f"  [-] Kralbozguncu fallback: {fallback}")
    return fallback

# -------------------------------------------------------------
# Main Execution
# -------------------------------------------------------------
def main():
    print(f"Starting Domain Resolver at {datetime.now(timezone.utc).isoformat()}...")
    
    # Read previous data if exists to get last known numbers/domains
    prev_data = {}
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
                prev_data = json.load(f)
        except Exception:
            pass

    # Extract last known rekortv number if available
    last_rekor_num = 942
    if "domains" in prev_data and "rekortv" in prev_data["domains"]:
        match = re.search(r'rekortv(\d+)\.com', prev_data["domains"]["rekortv"])
        if match:
            last_rekor_num = int(match.group(1))

    # Resolve all concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        f_rekor = executor.submit(resolve_rekortv, last_rekor_num)
        f_selcuk = executor.submit(resolve_selcuksports)
        f_hdfilm = executor.submit(resolve_hdfilmcehennemi)
        f_dizimom = executor.submit(resolve_dizimom)
        f_kral = executor.submit(resolve_kralbozguncu)

        rekortv_url = f_rekor.result()
        selcuk_url = f_selcuk.result()
        hdfilm_url = f_hdfilm.result()
        dizimom_url = f_dizimom.result()
        kral_url = f_kral.result()

    result = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "domains": {
            "rekortv": rekortv_url,
            "selcuksports": selcuk_url,
            "hdfilmcehennemi": hdfilm_url,
            "dizimom": dizimom_url,
            "kralbozguncu": kral_url
        }
    }

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=4, ensure_ascii=False)

    print(f"\nSuccessfully saved domains to: {OUTPUT_FILE}")
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
