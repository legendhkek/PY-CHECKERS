#!/usr/bin/env python3
"""Fast parallel proxy tester"""
import requests
import threading
import time
from queue import Queue
from colorama import init, Fore

init(autoreset=True)
print(f"{Fore.CYAN}Fast Proxy Tester - Finding Working Proxies\n")

# Load proxies
with open("proxy.txt") as f:
    all_proxies = [l.strip() for l in f if l.strip()]

print(f"Loaded {len(all_proxies)} proxies, testing...")

working = []
lock = threading.Lock()
tested = [0]
q = Queue()

# Add proxies to queue (test first 500)
for p in all_proxies[:500]:
    q.put(p)

def test_proxy():
    while True:
        try:
            proxy = q.get_nowait()
        except:
            break
        
        try:
            proxy_dict = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
            r = requests.get("http://httpbin.org/ip", proxies=proxy_dict, timeout=4)
            if r.status_code == 200:
                with lock:
                    working.append(proxy)
                    print(f"{Fore.GREEN}✓ {proxy}")
        except:
            pass
        
        with lock:
            tested[0] += 1
            if tested[0] % 50 == 0:
                print(f"{Fore.YELLOW}Tested: {tested[0]}, Working: {len(working)}")
        
        q.task_done()
        
        if len(working) >= 30:  # Stop when we have 30 working
            break

# Run 30 threads
threads = []
for _ in range(30):
    t = threading.Thread(target=test_proxy, daemon=True)
    t.start()
    threads.append(t)

# Wait for completion or enough working proxies
start = time.time()
while len(working) < 30 and time.time() - start < 60:
    time.sleep(1)
    if q.empty():
        break

print(f"\n{Fore.CYAN}Found {len(working)} working proxies")

# Save working proxies
if working:
    with open("proxy.txt", "w") as f:
        for p in working:
            f.write(p + "\n")
    print(f"{Fore.GREEN}Saved to proxy.txt")
