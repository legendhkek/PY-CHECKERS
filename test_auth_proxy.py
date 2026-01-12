#!/usr/bin/env python3
"""Test authenticated proxy against all 11 sites and analyze responses"""
import requests
import warnings
from colorama import init, Fore

warnings.filterwarnings("ignore")
init(autoreset=True)

print(f"{Fore.CYAN}{'='*70}")
print(f"{Fore.GREEN}{'TESTING AUTHENTICATED PROXY ON ALL 11 SITES'.center(70)}")
print(f"{Fore.CYAN}{'='*70}\n")

# Your proxy: host:port:user:pass
PROXY_STR = "202.28.17.8:8080:s6003026810028:1720800122226"
parts = PROXY_STR.split(":")
host, port, user, pwd = parts[0], parts[1], parts[2], parts[3]

# Format proxy for requests
proxy_url = f"http://{user}:{pwd}@{host}:{port}"
proxies = {"http": proxy_url, "https": proxy_url}

print(f"{Fore.YELLOW}Proxy: {host}:{port} (with auth)")
print(f"{Fore.YELLOW}Testing connectivity...\n")

# Test proxy connectivity first
try:
    r = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=10)
    print(f"{Fore.GREEN}✓ Proxy is working! IP: {r.json().get('origin', 'Unknown')}\n")
except Exception as e:
    print(f"{Fore.RED}✗ Proxy connection failed: {e}\n")
    print(f"{Fore.YELLOW}Trying without auth...")
    proxy_url = f"http://{host}:{port}"
    proxies = {"http": proxy_url, "https": proxy_url}
    try:
        r = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=10)
        print(f"{Fore.GREEN}✓ Proxy works without auth! IP: {r.json().get('origin', 'Unknown')}\n")
    except Exception as e2:
        print(f"{Fore.RED}✗ Proxy not working: {e2}\n")

# Test credentials
email = "testuser@gmail.com"
password = "TestPass123"
ua = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

sites = [
    {
        "name": "1. Azyrah",
        "base_url": "https://shop.azyrah.to",
        "login_url": "https://shop.azyrah.to/auth/signin", 
        "method": "json",
        "payload": {"username": email, "password": password}
    },
    {
        "name": "2. Blstash",
        "base_url": "https://blstash.ws",
        "login_url": "https://blstash.ws/api/auth/login",
        "method": "json",
        "payload": {"username": email, "password": password}
    },
    {
        "name": "3. DHL",
        "base_url": "https://www.dhl.com",
        "login_url": "https://www.dhl.com/en/express/mydhl.html",
        "method": "form",
        "payload": {"username": email, "password": password}
    },
    {
        "name": "4. Easydeals",
        "base_url": "https://easydeals.gs",
        "login_url": "https://easydeals.gs/api/auth/login",
        "method": "json",
        "payload": {"username": email, "password": password}
    },
    {
        "name": "5. Everymail",
        "base_url": "https://everymail.com",
        "login_url": "https://everymail.com/login",
        "method": "form",
        "payload": {"email": email, "password": password}
    },
    {
        "name": "6. Meetic",
        "base_url": "https://www.meetic.fr",
        "login_url": "https://www.meetic.fr/api/authentication/login",
        "method": "json",
        "payload": {"email": email, "password": password}
    },
    {
        "name": "7. RoyalMail",
        "base_url": "https://www.royalmail.com",
        "login_url": "https://www.royalmail.com/track-your-item",
        "method": "form",
        "payload": {"email": email, "password": password}
    },
    {
        "name": "8. Savastan0",
        "base_url": "https://savastan0.tools",
        "login_url": "https://savastan0.tools/api/auth/login",
        "method": "json",
        "payload": {"username": email, "password": password}
    },
    {
        "name": "9. Sky",
        "base_url": "https://www.sky.com",
        "login_url": "https://www.sky.com/signin",
        "method": "json",
        "payload": {"username": email, "password": password}
    },
    {
        "name": "10. Unitedshop",
        "base_url": "https://unitedshop.su",
        "login_url": "https://unitedshop.su/login",
        "method": "form",
        "payload": {"username": email, "password": password}
    },
    {
        "name": "11. UPS",
        "base_url": "https://www.ups.com",
        "login_url": "https://www.ups.com/lasso/login",
        "method": "form",
        "payload": {"userid": email, "password": password}
    }
]

results = {}

for site in sites:
    print(f"{Fore.YELLOW}{site['name']} - {site['base_url']}")
    
    try:
        s = requests.Session()
        headers = {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        }
        
        # First get base page
        r1 = s.get(site["base_url"], headers=headers, proxies=proxies, timeout=15, verify=False)
        print(f"  {Fore.CYAN}Base: Status {r1.status_code}")
        
        # Then try login
        if site["method"] == "json":
            headers["Content-Type"] = "application/json"
            headers["Accept"] = "application/json"
            r2 = s.post(site["login_url"], json=site["payload"], headers=headers, proxies=proxies, timeout=15, verify=False)
        else:
            headers["Content-Type"] = "application/x-www-form-urlencoded"
            r2 = s.post(site["login_url"], data=site["payload"], headers=headers, proxies=proxies, timeout=15, verify=False, allow_redirects=True)
        
        status = r2.status_code
        response = r2.text[:100].replace('\n', ' ').replace('\r', '')
        
        print(f"  {Fore.GREEN}Login: Status {status}")
        print(f"  {Fore.WHITE}Response: {response}...")
        
        # Analyze response
        txt = r2.text.lower()
        if status == 200:
            if any(x in txt for x in ["invalid", "incorrect", "wrong", "error", "fail"]):
                results[site["name"]] = ("OK-INVALID", "Site works, returns invalid creds response")
            elif any(x in txt for x in ["cloudflare", "captcha", "challenge"]):
                results[site["name"]] = ("CLOUDFLARE", "Protected by Cloudflare")
            else:
                results[site["name"]] = ("OK", "Site responding")
        elif status in [301, 302]:
            results[site["name"]] = ("OK-REDIRECT", "Site works with redirect")
        elif status == 401:
            results[site["name"]] = ("OK-AUTH", "Site works, auth required")
        elif status == 403:
            results[site["name"]] = ("BLOCKED", "Access blocked")
        elif status == 404:
            results[site["name"]] = ("API-CHANGED", "Endpoint not found")
        else:
            results[site["name"]] = (f"STATUS-{status}", f"HTTP {status}")
            
    except requests.exceptions.Timeout:
        print(f"  {Fore.RED}TIMEOUT")
        results[site["name"]] = ("TIMEOUT", "Site too slow")
    except requests.exceptions.ProxyError as e:
        print(f"  {Fore.RED}PROXY ERROR: {str(e)[:50]}")
        results[site["name"]] = ("PROXY-ERROR", str(e)[:30])
    except Exception as e:
        print(f"  {Fore.RED}ERROR: {str(e)[:50]}")
        results[site["name"]] = ("ERROR", str(e)[:30])
    
    print()

# Summary
print(f"{Fore.CYAN}{'='*70}")
print(f"{Fore.GREEN}{'ANALYSIS SUMMARY'.center(70)}")
print(f"{Fore.CYAN}{'='*70}\n")

for name, (status, desc) in results.items():
    if status.startswith("OK"):
        color = Fore.GREEN
        symbol = "✓"
    elif status in ["CLOUDFLARE", "BLOCKED"]:
        color = Fore.YELLOW
        symbol = "⚠"
    else:
        color = Fore.RED
        symbol = "✗"
    print(f"{color}{symbol} {name}: {status} - {desc}")
