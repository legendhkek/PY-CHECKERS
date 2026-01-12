#!/usr/bin/env python3
"""
Test proxy connectivity for all checker sites
Proxy: ngu.proxy.arealproxy.com:8080:652BthZDvxP7ozf:QDcj9tzf4gVaGNZ
"""
import os
import requests
import warnings
from colorama import init, Fore, Style

warnings.filterwarnings("ignore", category=requests.packages.urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

# Proxy configuration
PROXY_STR = "ngu.proxy.arealproxy.com:8080:652BthZDvxP7ozf:QDcj9tzf4gVaGNZ"

def format_proxy(p):
    """Format proxy string to dict for requests"""
    if not p:
        return None
    p = p.strip()
    
    # Handle host:port:username:password format
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

# Sites to test
SITES = [
    ("Google (Test)", "https://www.google.com", "text/html"),
    ("HTTPBin IP", "https://httpbin.org/ip", "application/json"),
    ("Azyrah Shop", "https://shop.azyrah.to/", "text/html"),
    ("Blstash", "https://blstash.ws/", "text/html"),
    ("DHL", "https://www.dhl.com/", "text/html"),
    ("Easydeals", "https://easydeals.gs/", "text/html"),
    ("Everymail", "https://everymail.com/", "text/html"),
    ("Meetic", "https://www.meetic.fr/", "text/html"),
    ("Royal Mail", "https://www.royalmail.com/", "text/html"),
    ("Savastan0", "https://savastan0.tools/", "text/html"),
    ("Sky", "https://www.sky.com/", "text/html"),
    ("Unitedshop", "https://unitedshop.su/", "text/html"),
    ("UPS", "https://www.ups.com/", "text/html"),
    ("ElevenLabs", "https://elevenlabs.io/", "text/html"),
]

def test_site(name, url, expected_type, proxy_dict, timeout=20):
    """Test connectivity to a site through proxy"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
        
        r = requests.get(url, headers=headers, proxies=proxy_dict, timeout=timeout, verify=False)
        
        return {
            "success": True,
            "status": r.status_code,
            "size": len(r.content),
            "reason": f"OK ({r.status_code})"
        }
    except requests.exceptions.Timeout:
        return {"success": False, "status": 0, "size": 0, "reason": "Timeout"}
    except requests.exceptions.ProxyError as e:
        return {"success": False, "status": 0, "size": 0, "reason": f"Proxy Error: {str(e)[:50]}"}
    except requests.exceptions.ConnectionError as e:
        return {"success": False, "status": 0, "size": 0, "reason": f"Connection Error: {str(e)[:50]}"}
    except Exception as e:
        return {"success": False, "status": 0, "size": 0, "reason": f"Error: {str(e)[:50]}"}

def main():
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}PROXY CONNECTIVITY TEST FOR ALL CHECKER SITES")
    print(f"{Fore.CYAN}{'='*60}")
    
    proxy_dict = format_proxy(PROXY_STR)
    print(f"\n{Fore.YELLOW}Proxy: {PROXY_STR}")
    print(f"{Fore.YELLOW}Formatted: {proxy_dict['http'][:50]}...")
    print(f"\n{Fore.CYAN}Testing {len(SITES)} sites...\n")
    
    results = []
    
    for name, url, expected in SITES:
        print(f"{Fore.WHITE}Testing {name}...", end=" ", flush=True)
        result = test_site(name, url, expected, proxy_dict)
        results.append((name, url, result))
        
        if result["success"]:
            print(f"{Fore.GREEN}✓ {result['reason']} - {result['size']} bytes")
        else:
            print(f"{Fore.RED}✗ {result['reason']}")
    
    # Summary
    success_count = sum(1 for _, _, r in results if r["success"])
    print(f"\n{Fore.CYAN}{'='*60}")
    print(f"{Fore.CYAN}SUMMARY")
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.GREEN}Success: {success_count}/{len(results)}")
    print(f"{Fore.RED}Failed: {len(results) - success_count}/{len(results)}")
    
    # List failures
    failures = [(n, u, r) for n, u, r in results if not r["success"]]
    if failures:
        print(f"\n{Fore.RED}Failed sites:")
        for name, url, result in failures:
            print(f"  - {name}: {result['reason']}")
    
    return success_count > 0

if __name__ == "__main__":
    main()
