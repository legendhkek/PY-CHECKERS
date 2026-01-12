#!/usr/bin/env python3
"""Get best working proxies - test against multiple sites"""
import requests
import threading
import random
import re
import time
from colorama import init, Fore

init(autoreset=True)
print(f"{Fore.CYAN}Getting Best Proxies...\n")

# Scrape from multiple sources
all_proxies = set()
sources = [
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/txt/proxies-http.txt",
    "https://raw.githubusercontent.com/MuRongPIG/Proxy-Master/main/http.txt",
]

for url in sources:
    try:
        r = requests.get(url, timeout=8)
        found = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}', r.text)
        all_proxies.update(found)
    except:
        pass

print(f"{Fore.GREEN}Scraped {len(all_proxies)} proxies")

# Test proxies
working = []
lock = threading.Lock()

proxy_list = list(all_proxies)
random.shuffle(proxy_list)

def test_proxy(proxy):
    if len(working) >= 30:
        return
    try:
        proxy_dict = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        # Test against simple endpoint
        r = requests.get("http://ip-api.com/json", proxies=proxy_dict, timeout=4)
        if r.status_code == 200 and "query" in r.text:
            with lock:
                if len(working) < 30:
                    working.append(proxy)
                    print(f"{Fore.GREEN}[{len(working)}] ✓ {proxy}")
    except:
        pass

# Test in parallel batches
batch_size = 100
for i in range(0, min(2000, len(proxy_list)), batch_size):
    if len(working) >= 30:
        break
    
    batch = proxy_list[i:i+batch_size]
    threads = []
    for proxy in batch:
        t = threading.Thread(target=test_proxy, args=(proxy,), daemon=True)
        t.start()
        threads.append(t)
    
    # Wait for batch
    for t in threads:
        t.join(timeout=5)
    
    print(f"{Fore.YELLOW}Tested {min(i+batch_size, len(proxy_list))}, Found: {len(working)}")

print(f"\n{Fore.CYAN}Found {len(working)} working proxies")

if working:
    with open("proxy.txt", "w") as f:
        for p in working:
            f.write(p + "\n")
    print(f"{Fore.GREEN}Saved to proxy.txt")
