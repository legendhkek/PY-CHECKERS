#!/usr/bin/env python3
"""
Proxy Scraper - Scrapes free HTTP/HTTPS proxies from multiple sources
"""
import requests
import re
import warnings
from colorama import init, Fore

warnings.filterwarnings("ignore")
init(autoreset=True)

print(f"{Fore.CYAN}{'='*60}")
print(f"{Fore.GREEN}{'PROXY SCRAPER - Getting Free Proxies'.center(60)}")
print(f"{Fore.CYAN}{'='*60}\n")

proxies = set()

# Proxy sources
sources = [
    ("ProxyScrape HTTP", "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all"),
    ("ProxyScrape HTTPS", "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=https&timeout=10000&country=all"),
    ("ProxyList Download HTTP", "https://www.proxy-list.download/api/v1/get?type=http"),
    ("ProxyList Download HTTPS", "https://www.proxy-list.download/api/v1/get?type=https"),
    ("OpenProxyList", "https://openproxylist.xyz/http.txt"),
    ("TheSpeedX HTTP", "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"),
    ("ShiftyTR HTTP", "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt"),
    ("MorZi Proxy", "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt"),
    ("Clarketm Proxy", "https://raw.githubusercontent.com/clarketm/proxy-list/master/proxy-list-raw.txt"),
    ("JetKai HTTP", "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt"),
    ("JetKai HTTPS", "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-https.txt"),
    ("Sunny9577", "https://raw.githubusercontent.com/sunny9577/proxy-scraper/master/proxies.txt"),
    ("RoostKid", "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt"),
    ("MuRongPIG", "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt"),
    ("Proxy4All", "https://raw.githubusercontent.com/proxy4parsing/proxy-list/main/http.txt"),
]

for name, url in sources:
    try:
        print(f"{Fore.YELLOW}Scraping: {name}...", end=" ")
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            # Extract IP:PORT patterns
            found = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}', r.text)
            before = len(proxies)
            proxies.update(found)
            added = len(proxies) - before
            print(f"{Fore.GREEN}+{added} proxies")
        else:
            print(f"{Fore.RED}Failed ({r.status_code})")
    except Exception as e:
        print(f"{Fore.RED}Error")

print(f"\n{Fore.CYAN}Total unique proxies scraped: {Fore.GREEN}{len(proxies)}")

# Save to file
with open("proxy.txt", "w") as f:
    for p in proxies:
        f.write(p + "\n")

print(f"{Fore.GREEN}Saved to proxy.txt")

# Now test some proxies
print(f"\n{Fore.CYAN}{'='*60}")
print(f"{Fore.YELLOW}Testing proxies for connectivity...")
print(f"{Fore.CYAN}{'='*60}\n")

working = []
tested = 0
max_test = min(50, len(proxies))  # Test up to 50 proxies

for proxy in list(proxies)[:max_test]:
    tested += 1
    try:
        proxy_dict = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        r = requests.get("http://httpbin.org/ip", proxies=proxy_dict, timeout=5)
        if r.status_code == 200:
            working.append(proxy)
            print(f"{Fore.GREEN}[{tested}/{max_test}] ✓ {proxy} - Working")
            if len(working) >= 20:  # Stop after finding 20 working proxies
                break
        else:
            print(f"{Fore.RED}[{tested}/{max_test}] ✗ {proxy} - Status {r.status_code}")
    except:
        print(f"{Fore.RED}[{tested}/{max_test}] ✗ {proxy} - Dead")

print(f"\n{Fore.CYAN}{'='*60}")
print(f"{Fore.GREEN}Found {len(working)} working proxies out of {tested} tested")
print(f"{Fore.CYAN}{'='*60}")

# Save working proxies
if working:
    with open("proxy.txt", "w") as f:
        for p in working:
            f.write(p + "\n")
    print(f"{Fore.GREEN}Saved {len(working)} working proxies to proxy.txt")
else:
    print(f"{Fore.YELLOW}No working proxies found in quick test, keeping all scraped proxies")
    print(f"{Fore.YELLOW}The checkers will test proxies automatically")
