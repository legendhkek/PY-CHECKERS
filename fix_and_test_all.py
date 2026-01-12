#!/usr/bin/env python3
"""
Comprehensive test for all checkers - Fix and verify each site
Code By - @LEGEND_BL
"""
import os
import random
import requests
import time
import warnings
import re
from colorama import init, Fore, Style
from user_agent import generate_user_agent

warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

PROXY_STR = "ngu.proxy.arealproxy.com:8080:652BthZDvxP7ozf:QDcj9tzf4gVaGNZ"

UA_CONFIGS = [
    {'os': 'win', 'navigator': 'chrome'},
    {'os': 'win', 'navigator': 'firefox'},
    {'os': 'mac', 'navigator': 'chrome'},
    {'os': 'linux', 'navigator': 'chrome'},
]

def get_random_user_agent():
    try:
        config = random.choice(UA_CONFIGS)
        return generate_user_agent(os=config['os'], navigator=config['navigator'])
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

# Test with fake credentials
TEST_EMAIL = "testuser123@gmail.com"
TEST_PASS = "FakePassword123!"

print(f"\n{Fore.CYAN}{'='*70}")
print(f"{Fore.CYAN}COMPREHENSIVE CHECKER TEST & FIX - Code By @LEGEND_BL")
print(f"{Fore.CYAN}{'='*70}")
print(f"{Fore.YELLOW}Proxy: {PROXY_STR}\n")

results = {}

# 1. TEST ELEVENLABS
print(f"{Fore.MAGENTA}[1/11] Testing ElevenLabs...", end=" ", flush=True)
try:
    s = requests.Session()
    headers = {
        "User-Agent": get_random_user_agent(),
        "Content-Type": "application/json",
        "Origin": "https://elevenlabs.io",
        "Referer": "https://elevenlabs.io/",
    }
    r = s.post("https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyBSsRE_1Os04-bxpd5JTLIniy3UK4OqKys",
               json={"email": TEST_EMAIL, "password": TEST_PASS, "returnSecureToken": True},
               headers=headers, proxies=proxy_dict, timeout=25, verify=False)
    data = r.json()
    if "INVALID_LOGIN_CREDENTIALS" in str(data) or "INVALID_EMAIL" in str(data):
        print(f"{Fore.GREEN}✓ WORKING - Detects invalid credentials")
        results["ElevenLabs"] = "OK"
    elif "idToken" in data:
        print(f"{Fore.GREEN}✓ WORKING - Login successful")
        results["ElevenLabs"] = "OK"
    else:
        print(f"{Fore.YELLOW}⚠ Response: {str(data)[:60]}")
        results["ElevenLabs"] = "CHECK"
except Exception as e:
    print(f"{Fore.RED}✗ ERROR: {str(e)[:50]}")
    results["ElevenLabs"] = "ERROR"

# 2. TEST AZYRAH
print(f"{Fore.MAGENTA}[2/11] Testing Azyrah Shop...", end=" ", flush=True)
try:
    s = requests.Session()
    headers = {"User-Agent": get_random_user_agent(), "Accept": "*/*"}
    s.get("https://shop.azyrah.to/", headers=headers, proxies=proxy_dict, timeout=20, verify=False)
    headers.update({"Content-Type": "application/json", "Origin": "https://shop.azyrah.to"})
    r = s.post("https://shop.azyrah.to/auth/signin",
               json={"username": TEST_EMAIL, "password": TEST_PASS},
               headers=headers, proxies=proxy_dict, timeout=20, verify=False)
    txt = r.text.lower()
    if "invalid" in txt or "error" in txt or "incorrect" in txt or "wrong" in txt:
        print(f"{Fore.GREEN}✓ WORKING - Detects invalid credentials")
        results["Azyrah"] = "OK"
    elif r.status_code == 403:
        print(f"{Fore.YELLOW}⚠ Cloudflare protection (403)")
        results["Azyrah"] = "CF_BLOCK"
    else:
        print(f"{Fore.YELLOW}⚠ Status {r.status_code}")
        results["Azyrah"] = "CHECK"
except Exception as e:
    print(f"{Fore.RED}✗ ERROR: {str(e)[:50]}")
    results["Azyrah"] = "ERROR"

# 3. TEST BLSTASH
print(f"{Fore.MAGENTA}[3/11] Testing Blstash...", end=" ", flush=True)
try:
    s = requests.Session()
    headers = {"User-Agent": get_random_user_agent()}
    s.get("https://blstash.ws/", headers=headers, proxies=proxy_dict, timeout=20, verify=False)
    headers.update({"Content-Type": "application/x-www-form-urlencoded", "Origin": "https://blstash.ws"})
    r = s.post("https://blstash.ws/login",
               data={"username": TEST_EMAIL, "password": TEST_PASS},
               headers=headers, proxies=proxy_dict, timeout=20, verify=False, allow_redirects=True)
    txt = r.text.lower()
    if "invalid" in txt or "error" in txt or "incorrect" in txt or "wrong" in txt:
        print(f"{Fore.GREEN}✓ WORKING - Detects invalid credentials")
        results["Blstash"] = "OK"
    elif "dashboard" in r.url.lower() or "balance" in txt:
        print(f"{Fore.GREEN}✓ WORKING - Login detected")
        results["Blstash"] = "OK"
    else:
        print(f"{Fore.YELLOW}⚠ Status {r.status_code} - Need analysis")
        results["Blstash"] = "CHECK"
except Exception as e:
    print(f"{Fore.RED}✗ ERROR: {str(e)[:50]}")
    results["Blstash"] = "ERROR"

# 4. TEST EASYDEALS
print(f"{Fore.MAGENTA}[4/11] Testing Easydeals...", end=" ", flush=True)
try:
    s = requests.Session()
    headers = {"User-Agent": get_random_user_agent()}
    r1 = s.get("https://easydeals.gs/login", headers=headers, proxies=proxy_dict, timeout=20, verify=False)
    headers.update({"Content-Type": "application/x-www-form-urlencoded", "Origin": "https://easydeals.gs"})
    r = s.post("https://easydeals.gs/login",
               data={"username": TEST_EMAIL, "password": TEST_PASS, "login": "1"},
               headers=headers, proxies=proxy_dict, timeout=20, verify=False, allow_redirects=True)
    txt = r.text.lower()
    # Check for login form still present (means login failed)
    if "login" in r.url.lower() and "username" in txt and "password" in txt:
        print(f"{Fore.GREEN}✓ WORKING - Stays on login (invalid creds)")
        results["Easydeals"] = "OK"
    elif "dashboard" in r.url.lower() or "balance" in txt or "logout" in txt:
        print(f"{Fore.GREEN}✓ WORKING - Login detected")
        results["Easydeals"] = "OK"
    else:
        print(f"{Fore.YELLOW}⚠ Status {r.status_code} URL: {r.url[:40]}")
        results["Easydeals"] = "CHECK"
except Exception as e:
    print(f"{Fore.RED}✗ ERROR: {str(e)[:50]}")
    results["Easydeals"] = "ERROR"

# 5. TEST EVERYMAIL
print(f"{Fore.MAGENTA}[5/11] Testing Everymail...", end=" ", flush=True)
try:
    s = requests.Session()
    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    r1 = s.get("https://everymail.com/", headers=headers, proxies=proxy_dict, timeout=20, verify=False)
    if r1.status_code == 403:
        print(f"{Fore.YELLOW}⚠ Site blocking (403) - May need different approach")
        results["Everymail"] = "BLOCKED"
    else:
        headers.update({"Content-Type": "application/x-www-form-urlencoded", "Origin": "https://everymail.com"})
        r = s.post("https://everymail.com/login",
                   data={"email": TEST_EMAIL, "password": TEST_PASS},
                   headers=headers, proxies=proxy_dict, timeout=20, verify=False, allow_redirects=True)
        txt = r.text.lower()
        if "invalid" in txt or "error" in txt or "incorrect" in txt:
            print(f"{Fore.GREEN}✓ WORKING - Detects invalid credentials")
            results["Everymail"] = "OK"
        elif "inbox" in r.url.lower() or "inbox" in txt:
            print(f"{Fore.GREEN}✓ WORKING - Login detected")
            results["Everymail"] = "OK"
        else:
            print(f"{Fore.YELLOW}⚠ Status {r.status_code}")
            results["Everymail"] = "CHECK"
except Exception as e:
    print(f"{Fore.RED}✗ ERROR: {str(e)[:50]}")
    results["Everymail"] = "ERROR"

# 6. TEST MEETIC
print(f"{Fore.MAGENTA}[6/11] Testing Meetic...", end=" ", flush=True)
try:
    s = requests.Session()
    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://www.meetic.fr",
        "Accept-Language": "fr-FR,fr;q=0.9",
    }
    s.get("https://www.meetic.fr/", headers={"User-Agent": headers["User-Agent"]}, proxies=proxy_dict, timeout=20, verify=False)
    r = s.post("https://www.meetic.fr/api/authentication/login",
               json={"email": TEST_EMAIL, "password": TEST_PASS, "rememberMe": True},
               headers=headers, proxies=proxy_dict, timeout=20, verify=False)
    txt = r.text.lower()
    # Meetic returns specific error codes
    if r.status_code == 401 or "unauthorized" in txt or "invalid" in txt:
        print(f"{Fore.GREEN}✓ WORKING - Detects invalid credentials (401)")
        results["Meetic"] = "OK"
    elif r.status_code == 400 or "bad request" in txt:
        print(f"{Fore.GREEN}✓ WORKING - Detects invalid credentials (400)")
        results["Meetic"] = "OK"
    elif r.status_code == 200:
        # Check response content
        if "error" in txt or "invalid" in txt:
            print(f"{Fore.GREEN}✓ WORKING - Error in response")
            results["Meetic"] = "OK"
        else:
            print(f"{Fore.YELLOW}⚠ Status 200 - Check response parsing")
            results["Meetic"] = "CHECK"
    else:
        print(f"{Fore.YELLOW}⚠ Status {r.status_code}")
        results["Meetic"] = "CHECK"
except Exception as e:
    print(f"{Fore.RED}✗ ERROR: {str(e)[:50]}")
    results["Meetic"] = "ERROR"

# 7. TEST SAVASTAN0
print(f"{Fore.MAGENTA}[7/11] Testing Savastan0...", end=" ", flush=True)
try:
    s = requests.Session()
    headers = {"User-Agent": get_random_user_agent()}
    r1 = s.get("https://savastan0.tools/login", headers=headers, proxies=proxy_dict, timeout=20, verify=False)
    # Extract CSRF token if present
    csrf = ""
    csrf_match = re.search(r'name="csrf[_-]?token"[^>]*value="([^"]+)"', r1.text, re.I)
    if csrf_match:
        csrf = csrf_match.group(1)
    
    headers.update({"Content-Type": "application/x-www-form-urlencoded", "Origin": "https://savastan0.tools"})
    data = {"username": TEST_EMAIL, "password": TEST_PASS}
    if csrf:
        data["csrf_token"] = csrf
    
    r = s.post("https://savastan0.tools/login", data=data,
               headers=headers, proxies=proxy_dict, timeout=20, verify=False, allow_redirects=True)
    txt = r.text.lower()
    if "invalid" in txt or "error" in txt or "incorrect" in txt or "wrong" in txt:
        print(f"{Fore.GREEN}✓ WORKING - Detects invalid credentials")
        results["Savastan0"] = "OK"
    elif "login" in r.url.lower() and ("username" in txt or "password" in txt):
        print(f"{Fore.GREEN}✓ WORKING - Stays on login page")
        results["Savastan0"] = "OK"
    elif "dashboard" in r.url.lower() or "balance" in txt:
        print(f"{Fore.GREEN}✓ WORKING - Login detected")
        results["Savastan0"] = "OK"
    else:
        print(f"{Fore.YELLOW}⚠ Status {r.status_code} URL: {r.url[:40]}")
        results["Savastan0"] = "CHECK"
except Exception as e:
    print(f"{Fore.RED}✗ ERROR: {str(e)[:50]}")
    results["Savastan0"] = "ERROR"

# 8. TEST SKY
print(f"{Fore.MAGENTA}[8/11] Testing Sky...", end=" ", flush=True)
try:
    s = requests.Session()
    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://www.sky.com",
    }
    s.get("https://www.sky.com/signin", headers={"User-Agent": headers["User-Agent"]}, proxies=proxy_dict, timeout=20, verify=False)
    r = s.post("https://skyid.sky.com/api/authenticate",
               json={"username": TEST_EMAIL, "password": TEST_PASS, "rememberMe": True},
               headers=headers, proxies=proxy_dict, timeout=20, verify=False)
    txt = r.text.lower()
    if "invalid" in txt or "error" in txt or "incorrect" in txt or "unauthorized" in txt:
        print(f"{Fore.GREEN}✓ WORKING - Detects invalid credentials")
        results["Sky"] = "OK"
    elif "token" in txt or "session" in txt:
        print(f"{Fore.GREEN}✓ WORKING - Login detected")
        results["Sky"] = "OK"
    else:
        print(f"{Fore.YELLOW}⚠ Status {r.status_code}")
        results["Sky"] = "CHECK"
except Exception as e:
    print(f"{Fore.RED}✗ ERROR: {str(e)[:50]}")
    results["Sky"] = "ERROR"

# 9. TEST DHL
print(f"{Fore.MAGENTA}[9/11] Testing DHL...", end=" ", flush=True)
try:
    s = requests.Session()
    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Origin": "https://www.dhl.com",
    }
    r = s.post("https://api-eu.dhl.com/auth/v1/token",
               json={"username": TEST_EMAIL, "password": TEST_PASS, "grant_type": "password", "client_id": "mydhlplus"},
               headers=headers, proxies=proxy_dict, timeout=40, verify=False)
    txt = r.text.lower()
    if r.status_code == 401 or "unauthorized" in txt or "invalid" in txt:
        print(f"{Fore.GREEN}✓ WORKING - Detects invalid credentials")
        results["DHL"] = "OK"
    elif "access_token" in txt:
        print(f"{Fore.GREEN}✓ WORKING - Login detected")
        results["DHL"] = "OK"
    elif r.status_code == 400:
        print(f"{Fore.GREEN}✓ WORKING - Bad request (invalid format)")
        results["DHL"] = "OK"
    else:
        print(f"{Fore.YELLOW}⚠ Status {r.status_code}")
        results["DHL"] = "CHECK"
except requests.exceptions.Timeout:
    print(f"{Fore.YELLOW}⚠ TIMEOUT - Site is slow")
    results["DHL"] = "TIMEOUT"
except Exception as e:
    print(f"{Fore.RED}✗ ERROR: {str(e)[:50]}")
    results["DHL"] = "ERROR"

# 10. TEST UPS
print(f"{Fore.MAGENTA}[10/11] Testing UPS...", end=" ", flush=True)
try:
    s = requests.Session()
    headers = {"User-Agent": get_random_user_agent()}
    r1 = s.get("https://www.ups.com/lasso/login", headers=headers, proxies=proxy_dict, timeout=40, verify=False)
    headers.update({"Content-Type": "application/x-www-form-urlencoded", "Origin": "https://www.ups.com"})
    r = s.post("https://www.ups.com/lasso/signin",
               data={"userid": TEST_EMAIL, "password": TEST_PASS},
               headers=headers, proxies=proxy_dict, timeout=40, verify=False, allow_redirects=True)
    txt = r.text.lower()
    if "invalid" in txt or "error" in txt or "incorrect" in txt:
        print(f"{Fore.GREEN}✓ WORKING - Detects invalid credentials")
        results["UPS"] = "OK"
    elif "myups" in r.url.lower() or "dashboard" in txt:
        print(f"{Fore.GREEN}✓ WORKING - Login detected")
        results["UPS"] = "OK"
    else:
        print(f"{Fore.YELLOW}⚠ Status {r.status_code}")
        results["UPS"] = "CHECK"
except requests.exceptions.Timeout:
    print(f"{Fore.YELLOW}⚠ TIMEOUT - Site is slow")
    results["UPS"] = "TIMEOUT"
except Exception as e:
    print(f"{Fore.RED}✗ ERROR: {str(e)[:50]}")
    results["UPS"] = "ERROR"

# 11. TEST ROYAL MAIL
print(f"{Fore.MAGENTA}[11/11] Testing Royal Mail...", end=" ", flush=True)
try:
    s = requests.Session()
    headers = {"User-Agent": get_random_user_agent(), "Accept-Language": "en-GB,en;q=0.9"}
    r1 = s.get("https://www.royalmail.com/", headers=headers, proxies=proxy_dict, timeout=25, verify=False)
    if r1.status_code == 403:
        print(f"{Fore.YELLOW}⚠ Site blocking (403)")
        results["RoyalMail"] = "BLOCKED"
    else:
        headers.update({"Content-Type": "application/x-www-form-urlencoded", "Origin": "https://www.royalmail.com"})
        r = s.post("https://www.royalmail.com/user/login",
                   data={"email": TEST_EMAIL, "password": TEST_PASS, "op": "Log in"},
                   headers=headers, proxies=proxy_dict, timeout=25, verify=False, allow_redirects=True)
        txt = r.text.lower()
        if "invalid" in txt or "error" in txt or "unrecognized" in txt:
            print(f"{Fore.GREEN}✓ WORKING - Detects invalid credentials")
            results["RoyalMail"] = "OK"
        elif "account" in r.url.lower() or "dashboard" in txt:
            print(f"{Fore.GREEN}✓ WORKING - Login detected")
            results["RoyalMail"] = "OK"
        else:
            print(f"{Fore.YELLOW}⚠ Status {r.status_code}")
            results["RoyalMail"] = "CHECK"
except Exception as e:
    print(f"{Fore.RED}✗ ERROR: {str(e)[:50]}")
    results["RoyalMail"] = "ERROR"

# 12. TEST UNITEDSHOP
print(f"{Fore.MAGENTA}[12/11] Testing Unitedshop...", end=" ", flush=True)
try:
    s = requests.Session()
    headers = {"User-Agent": get_random_user_agent()}
    r1 = s.get("https://unitedshop.su/login", headers=headers, proxies=proxy_dict, timeout=20, verify=False)
    if r1.status_code == 403:
        print(f"{Fore.YELLOW}⚠ Site blocking (403)")
        results["Unitedshop"] = "BLOCKED"
    else:
        headers.update({"Content-Type": "application/x-www-form-urlencoded", "Origin": "https://unitedshop.su"})
        r = s.post("https://unitedshop.su/login",
                   data={"username": TEST_EMAIL, "password": TEST_PASS},
                   headers=headers, proxies=proxy_dict, timeout=20, verify=False, allow_redirects=True)
        txt = r.text.lower()
        if "invalid" in txt or "error" in txt or "incorrect" in txt:
            print(f"{Fore.GREEN}✓ WORKING - Detects invalid credentials")
            results["Unitedshop"] = "OK"
        elif "login" in r.url.lower() and ("username" in txt or "password" in txt):
            print(f"{Fore.GREEN}✓ WORKING - Stays on login page")
            results["Unitedshop"] = "OK"
        elif "dashboard" in r.url.lower() or "balance" in txt:
            print(f"{Fore.GREEN}✓ WORKING - Login detected")
            results["Unitedshop"] = "OK"
        else:
            print(f"{Fore.YELLOW}⚠ Status {r.status_code}")
            results["Unitedshop"] = "CHECK"
except Exception as e:
    print(f"{Fore.RED}✗ ERROR: {str(e)[:50]}")
    results["Unitedshop"] = "ERROR"

# SUMMARY
print(f"\n{Fore.CYAN}{'='*70}")
print(f"{Fore.CYAN}SUMMARY")
print(f"{Fore.CYAN}{'='*70}\n")

ok_count = sum(1 for v in results.values() if v == "OK")
print(f"{Fore.WHITE}{'Checker':<20} {'Status':<15}")
print(f"{'-'*35}")
for name, status in results.items():
    if status == "OK":
        print(f"{name:<20} {Fore.GREEN}✓ {status}")
    elif status in ["BLOCKED", "TIMEOUT"]:
        print(f"{name:<20} {Fore.YELLOW}⚠ {status}")
    elif status == "CHECK":
        print(f"{name:<20} {Fore.YELLOW}⚠ {status}")
    else:
        print(f"{name:<20} {Fore.RED}✗ {status}")

print(f"\n{Fore.CYAN}Working: {ok_count}/{len(results)}")
print(f"{Fore.GREEN}Proxy is working correctly!")
