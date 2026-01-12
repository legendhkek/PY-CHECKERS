#!/usr/bin/env python3
"""Get more working proxies by testing in batches"""
import requests
import threading
import time
import random
from queue import Queue
from colorama import init, Fore

init(autoreset=True)

# Load all proxies back
print(f"{Fore.CYAN}Scraping fresh proxies...")

all_proxies = set()
sources = [
    "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all",
    "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
    "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
    "https://raw.githubusercontent.com/ShiftyTR/Proxy-List/master/http.txt",
]

for url in sources:
    try:
        r = requests.get(url, timeout=10)
        import re
        found = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{2,5}', r.text)
        all_proxies.update(found)
        print(f"{Fore.GREEN}Got {len(found)} from source")
    except:
        pass

print(f"{Fore.CYAN}Total: {len(all_proxies)} proxies")
print(f"{Fore.YELLOW}Testing 1000 random proxies...")

proxy_list = list(all_proxies)
random.shuffle(proxy_list)
test_proxies = proxy_list[:1000]

working = []
lock = threading.Lock()
q = Queue()

for p in test_proxies:
    q.put(p)

def test_proxy():
    while True:
        try:
            proxy = q.get_nowait()
        except:
            break
        
        if len(working) >= 25:
            q.task_done()
            break
            
        try:
            proxy_dict = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
            r = requests.get("http://ip-api.com/json", proxies=proxy_dict, timeout=3)
            if r.status_code == 200:
                with lock:
                    if len(working) < 25:
                        working.append(proxy)
                        print(f"{Fore.GREEN}[{len(working)}] ✓ {proxy}")
        except:
            pass
        
        q.task_done()

# Run 50 threads for speed
for _ in range(50):
    threading.Thread(target=test_proxy, daemon=True).start()

# Wait
start = time.time()
while len(working) < 25 and time.time() - start < 45:
    time.sleep(0.5)

print(f"\n{Fore.CYAN}Found {len(working)} working proxies")

if working:
    with open("proxy.txt", "w") as f:
        for p in working:
            f.write(p + "\n")
    print(f"{Fore.GREEN}Saved to proxy.txt")
