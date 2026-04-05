#!/usr/bin/env python3
"""
NETWORK SCANNER - Scan All Devices in Your Network
Day 2 Advanced - Find all live hosts
"""

import subprocess
import socket
from concurrent.futures import ThreadPoolExecutor
import sys

def ping_host(ip):
    """Check if host is alive using ping"""
    try:
        # Windows: ping -n 1, Linux/Mac: ping -c 1
        param = '-n' if sys.platform == 'win32' else '-c'
        result = subprocess.run(
            ['ping', param, '1', '-w', '1000', ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=2
        )
        return result.returncode == 0
    except:
        return False

def get_hostname(ip):
    """Try to get hostname from IP"""
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return "Unknown"

def scan_network(network_base):
    """
    Scan entire network range
    Example: network_base = "192.168.1"
    """
    print(f"\n🔍 Scanning network: {network_base}.0/24")
    print("="*70)
    print(f"{'IP ADDRESS':<20} {'STATUS':<15} {'HOSTNAME':<30}")
    print("="*70)
    
    live_hosts = []
    
    # Use ThreadPool for faster scanning
    with ThreadPoolExecutor(max_workers=50) as executor:
        futures = []
        for i in range(1, 255):
            ip = f"{network_base}.{i}"
            futures.append(executor.submit(ping_host, ip))
        
        # Check results
        for i, future in enumerate(futures, start=1):
            ip = f"{network_base}.{i}"
            if future.result():
                hostname = get_hostname(ip)
                print(f"{ip:<20} {'✅ ALIVE':<15} {hostname:<30}")
                live_hosts.append((ip, hostname))
    
    print("="*70)
    print(f"\n✅ Found {len(live_hosts)} live hosts!\n")
    
    return live_hosts

def main():
    print("""
    ╔═══════════════════════════════════════════════╗
    ║      NETWORK SCANNER - Find All Devices       ║
    ║          Day 2 - Advanced Project             ║
    ╚═══════════════════════════════════════════════╝
    """)
    
    # Get network base from user
    network_base = input("Enter network base (e.g., 192.168.1): ").strip()
    
    if not network_base:
        print("❌ Network base required!")
        return
    
    # Scan network
    live_hosts = scan_network(network_base)
    
    if live_hosts:
        # Ask if user wants to scan each host
        scan_ports = input("\n🔍 Scan ports on all live hosts? (yes/no): ").lower()
        
        if scan_ports == 'yes':
            print("\n" + "="*70)
            print("Starting port scans on each host...")
            print("="*70 + "\n")
            
            for ip, hostname in live_hosts:
                print(f"\n>>> Scanning {ip} ({hostname})...")
                # Import from your port scanner
                # scan_with_service_detection(ip, 1, 100)
                print(f"    Use: python port_scanner_v2_fixed.py")
                print(f"    Target: {ip}\n")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Scan interrupted!")
        sys.exit()