#!/usr/bin/env python3
"""
ADVANCED PORT SCANNER V2.1 (With CLI Arguments)
Day 2 - Cybersecurity Learning Project

Usage:
  Interactive mode:
    python port_scanner_v2_cli.py
  
  Command line mode:
    python port_scanner_v2_cli.py --target 192.168.1.87
    python port_scanner_v2_cli.py --target scanme.nmap.org --quick
    python port_scanner_v2_cli.py --target 192.168.1.1 --range 1 1000
    python port_scanner_v2_cli.py -t 192.168.1.87 -p 1-100 --banner
"""

import socket
import sys
from datetime import datetime
import threading
from queue import Queue
import argparse

# ===== COLOR CODES =====
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# ===== PORT DATABASE =====
COMMON_PORTS = {
    20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "Telnet",
    25: "SMTP", 53: "DNS", 80: "HTTP", 110: "POP3",
    143: "IMAP", 443: "HTTPS", 445: "SMB", 3306: "MySQL",
    3389: "RDP", 5432: "PostgreSQL", 5900: "VNC",
    8080: "HTTP-Proxy", 8443: "HTTPS-Alt"
}

# ===== GLOBAL VARIABLES =====
print_lock = threading.Lock()
open_ports = []
scanned_count = 0
total_ports = 0

# ===== HELPER FUNCTIONS =====

def get_service_name(port):
    return COMMON_PORTS.get(port, "Unknown")

def grab_banner(target, port):
    try:
        sock = socket.socket()
        sock.settimeout(2)
        sock.connect((target, port))
        banner = sock.recv(1024).decode().strip()
        sock.close()
        return banner
    except:
        return None

def resolve_hostname(target):
    try:
        ip = socket.gethostbyname(target)
        return ip
    except socket.gaierror:
        print(f"{Colors.RED}❌ Cannot resolve hostname: {target}{Colors.RESET}")
        sys.exit()

def save_to_txt(target, ip, open_ports, filename=None):
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"scan_{target.replace('.', '_')}_{timestamp}.txt"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("="*70 + "\n")
            f.write("           PORT SCAN RESULTS\n")
            f.write("="*70 + "\n\n")
            f.write(f"Target Hostname: {target}\n")
            f.write(f"Target IP: {ip}\n")
            f.write(f"Scan Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total Open Ports: {len(open_ports)}\n\n")
            f.write("="*70 + "\n")
            f.write(f"{'PORT':<8} {'SERVICE':<20} {'BANNER/VERSION':<40}\n")
            f.write("="*70 + "\n\n")
            
            for port_info in open_ports:
                port = port_info['port']
                service = port_info['service']
                banner = port_info['banner'] if port_info['banner'] else '-'
                f.write(f"{port:<8} {service:<20} {banner[:40]:<40}\n")
            
            f.write("\n" + "="*70 + "\n")
        
        print(f"\n{Colors.GREEN}📁 Results saved to: {filename}{Colors.RESET}")
        return filename
    except Exception as e:
        print(f"{Colors.RED}❌ Error saving file: {e}{Colors.RESET}")
        return None

def save_to_csv(target, ip, open_ports, filename=None):
    if filename is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"scan_{target.replace('.', '_')}_{timestamp}.csv"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("Port,Service,Banner,Target,IP,Scan_Date\n")
            
            scan_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            for port_info in open_ports:
                port = port_info['port']
                service = port_info['service']
                banner = port_info['banner'].replace(',', ';') if port_info['banner'] else ''
                f.write(f"{port},{service},{banner},{target},{ip},{scan_date}\n")
        
        print(f"{Colors.GREEN}📊 CSV saved to: {filename}{Colors.RESET}")
        return filename
    except Exception as e:
        print(f"{Colors.RED}❌ Error saving CSV: {e}{Colors.RESET}")
        return None

# ===== SCANNING FUNCTIONS =====

def scan_port(target, port, grab_banners=False):
    global scanned_count
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((target, port))
        sock.close()
        
        with print_lock:
            scanned_count += 1
            if total_ports > 0:
                progress = (scanned_count / total_ports) * 100
                print(f"{Colors.CYAN}Progress: {progress:.1f}% ({scanned_count}/{total_ports}){Colors.RESET}", end='\r')
        
        if result == 0:
            service = get_service_name(port)
            banner = None
            
            if grab_banners:
                banner = grab_banner(target, port)
            
            with print_lock:
                if banner:
                    print(f"{Colors.GREEN}✅ Port {port:<6} OPEN    {service:<15} [{banner[:40]}]{Colors.RESET}")
                else:
                    print(f"{Colors.GREEN}✅ Port {port:<6} OPEN    {service:<15}{Colors.RESET}")
                
                open_ports.append({
                    'port': port,
                    'service': service,
                    'banner': banner,
                    'timestamp': datetime.now()
                })
    except:
        pass

def quick_scan(target, grab_banners=False, auto_save=False):
    global scanned_count, total_ports, open_ports
    
    scanned_count = 0
    open_ports = []
    
    common = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 
              3306, 3389, 5432, 5900, 8080, 8443]
    
    total_ports = len(common)
    ip = resolve_hostname(target)
    
    print("\n" + Colors.BOLD + "="*80)
    print(f"           QUICK PORT SCAN")
    print("="*80 + Colors.RESET)
    print(f"{Colors.CYAN}🎯 Target: {target} ({ip}){Colors.RESET}")
    print(f"{Colors.CYAN}📊 Scanning {total_ports} common ports{Colors.RESET}")
    print(f"{Colors.CYAN}🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
    print(Colors.BOLD + "="*80 + Colors.RESET + "\n")
    
    start_time = datetime.now()
    
    for port in common:
        scan_port(ip, port, grab_banners)
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + Colors.BOLD + "="*80)
    print(f"                    QUICK SCAN COMPLETE!")
    print("="*80 + Colors.RESET)
    print(f"{Colors.GREEN}✅ Total Ports Scanned: {total_ports}{Colors.RESET}")
    print(f"{Colors.GREEN}✅ Open Ports Found: {len(open_ports)}{Colors.RESET}")
    print(f"{Colors.GREEN}✅ Duration: {duration:.2f} seconds{Colors.RESET}")
    print(Colors.BOLD + "="*80 + Colors.RESET + "\n")
    
    if open_ports:
        print(Colors.BOLD + "📋 OPEN PORTS:" + Colors.RESET)
        print("-"*80)
        print(f"{'PORT':<8} {'SERVICE':<20} {'BANNER/VERSION':<50}")
        print("-"*80)
        for p in open_ports:
            banner = p['banner'][:47] + "..." if p['banner'] and len(p['banner']) > 50 else (p['banner'] or '-')
            print(f"{p['port']:<8} {p['service']:<20} {banner:<50}")
        print("-"*80 + "\n")
        
        if auto_save:
            save_to_txt(target, ip, open_ports)
            save_to_csv(target, ip, open_ports)
        else:
            save = input(f"{Colors.YELLOW}💾 Save results? (yes/no): {Colors.RESET}").lower()
            if save == 'yes':
                save_to_txt(target, ip, open_ports)
                save_to_csv(target, ip, open_ports)
    
    return open_ports

def threaded_scan(target, port_range, threads=100, grab_banners=False, auto_save=False):
    global scanned_count, total_ports, open_ports
    
    scanned_count = 0
    open_ports = []
    total_ports = port_range[1] - port_range[0] + 1
    
    ip = resolve_hostname(target)
    
    print("\n" + Colors.BOLD + "="*80)
    print(f"           PORT SCANNER")
    print("="*80 + Colors.RESET)
    print(f"{Colors.CYAN}🎯 Target: {target} ({ip}){Colors.RESET}")
    print(f"{Colors.CYAN}📊 Range: {port_range[0]}-{port_range[1]} ({total_ports} ports){Colors.RESET}")
    print(f"{Colors.CYAN}🧵 Threads: {threads}{Colors.RESET}")
    print(f"{Colors.CYAN}🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
    print(Colors.BOLD + "="*80 + Colors.RESET + "\n")
    
    port_queue = Queue()
    for port in range(port_range[0], port_range[1] + 1):
        port_queue.put(port)
    
    def worker():
        while not port_queue.empty():
            try:
                port = port_queue.get(timeout=1)
                scan_port(ip, port, grab_banners)
                port_queue.task_done()
            except:
                break
    
    start_time = datetime.now()
    
    thread_list = []
    for _ in range(threads):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
        thread_list.append(t)
    
    try:
        port_queue.join()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️ Scan interrupted!{Colors.RESET}")
        sys.exit()
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    print("\n" + Colors.BOLD + "="*80)
    print(f"                    SCAN COMPLETE!")
    print("="*80 + Colors.RESET)
    print(f"{Colors.GREEN}✅ Scanned: {total_ports} ports{Colors.RESET}")
    print(f"{Colors.GREEN}✅ Open: {len(open_ports)} ports{Colors.RESET}")
    print(f"{Colors.GREEN}✅ Duration: {duration:.2f}s ({total_ports/duration:.1f} ports/s){Colors.RESET}")
    print(Colors.BOLD + "="*80 + Colors.RESET + "\n")
    
    if open_ports:
        print(Colors.BOLD + "📋 OPEN PORTS:" + Colors.RESET)
        print("-"*80)
        print(f"{'PORT':<8} {'SERVICE':<20} {'BANNER/VERSION':<50}")
        print("-"*80)
        for p in open_ports:
            banner = p['banner'][:47] + "..." if p['banner'] and len(p['banner']) > 50 else (p['banner'] or '-')
            print(f"{p['port']:<8} {p['service']:<20} {banner:<50}")
        print("-"*80 + "\n")
        
        if auto_save:
            save_to_txt(target, ip, open_ports)
            save_to_csv(target, ip, open_ports)
        else:
            save = input(f"{Colors.YELLOW}💾 Save results? (yes/no): {Colors.RESET}").lower()
            if save == 'yes':
                save_to_txt(target, ip, open_ports)
                save_to_csv(target, ip, open_ports)
    
    return open_ports

# ===== MAIN PROGRAM =====

def print_banner():
    print(f"""
{Colors.CYAN}{Colors.BOLD}
    ╔═══════════════════════════════════════════════════════════╗
    ║          ADVANCED PORT SCANNER V2.1                       ║
    ║          With Command Line Arguments Support              ║
    ╚═══════════════════════════════════════════════════════════╝
{Colors.RESET}
    """)

def main():
    print_banner()
    
    # Setup argument parser
    parser = argparse.ArgumentParser(
        description='Advanced Port Scanner V2.1',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Quick scan:
    python %(prog)s --target scanme.nmap.org --quick
    
  Range scan:
    python %(prog)s -t 192.168.1.1 -p 1-1000
    python %(prog)s --target 192.168.1.87 --range 1 100
    
  With banner grabbing:
    python %(prog)s -t 192.168.1.1 -p 1-100 --banner
    
  Auto-save results:
    python %(prog)s -t scanme.nmap.org --quick --save
        """
    )
    
    parser.add_argument('-t', '--target', help='Target IP or hostname')
    parser.add_argument('-p', '--ports', help='Port range (e.g., 1-1000 or 80,443,8080)')
    parser.add_argument('-r', '--range', nargs=2, type=int, metavar=('START', 'END'), 
                       help='Port range (e.g., --range 1 1000)')
    parser.add_argument('-q', '--quick', action='store_true', help='Quick scan (16 common ports)')
    parser.add_argument('-b', '--banner', action='store_true', help='Enable banner grabbing')
    parser.add_argument('-s', '--save', action='store_true', help='Auto-save results')
    parser.add_argument('--threads', type=int, default=100, help='Number of threads (default: 100)')
    
    args = parser.parse_args()
    
    # If no arguments, run interactive mode
    if len(sys.argv) == 1:
        interactive_mode()
        return
    
    # Validate target
    if not args.target:
        print(f"{Colors.RED}❌ Error: Target required! Use -t or --target{Colors.RESET}")
        print(f"\nExample: python {sys.argv[0]} -t 192.168.1.87 --quick")
        sys.exit(1)
    
    # Execute scan
    if args.quick:
        quick_scan(args.target, grab_banners=args.banner, auto_save=args.save)
    elif args.range:
        threaded_scan(args.target, tuple(args.range), threads=args.threads, 
                     grab_banners=args.banner, auto_save=args.save)
    elif args.ports:
        # Parse port range
        if '-' in args.ports:
            start, end = map(int, args.ports.split('-'))
            threaded_scan(args.target, (start, end), threads=args.threads,
                         grab_banners=args.banner, auto_save=args.save)
        else:
            # Specific ports
            ports = [int(p) for p in args.ports.split(',')]
            # Scan specific ports (not implemented yet)
            print(f"{Colors.YELLOW}Specific port scanning coming soon!{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}No scan mode specified. Use --quick or --range{Colors.RESET}")
        print(f"Example: python {sys.argv[0]} -t {args.target} --quick")

def interactive_mode():
    """Original interactive mode"""
    print(f"{Colors.YELLOW}Choose scan mode:{Colors.RESET}")
    print(f"  {Colors.GREEN}1.{Colors.RESET} Quick Scan (16 most common ports) {Colors.CYAN}← FAST{Colors.RESET}")
    print(f"  {Colors.GREEN}2.{Colors.RESET} Range Scan (Specify custom range)")
    print(f"  {Colors.GREEN}3.{Colors.RESET} Full Scan (All 65535 ports) {Colors.RED}← VERY SLOW!{Colors.RESET}")
    print(f"  {Colors.GREEN}4.{Colors.RESET} Well-Known Ports (1-1024)")
    print(f"  {Colors.GREEN}5.{Colors.RESET} Exit\n")
    
    choice = input(f"{Colors.YELLOW}Your choice (1-5): {Colors.RESET}").strip()
    
    if choice == '5':
        print(f"{Colors.CYAN}👋 Goodbye!{Colors.RESET}")
        sys.exit()
    
    target = input(f"\n{Colors.YELLOW}Enter target (IP or hostname): {Colors.RESET}").strip()
    if not target:
        print(f"{Colors.RED}❌ Target required!{Colors.RESET}")
        return
    
    grab_banners = input(f"{Colors.YELLOW}Grab banners? (yes/no): {Colors.RESET}").lower() == 'yes'
    
    if choice == '1':
        quick_scan(target, grab_banners)
    elif choice == '2':
        start = int(input(f"{Colors.YELLOW}Start port: {Colors.RESET}") or 1)
        end = int(input(f"{Colors.YELLOW}End port: {Colors.RESET}") or 1000)
        threads = int(input(f"{Colors.YELLOW}Threads (default 100): {Colors.RESET}") or 100)
        threaded_scan(target, (start, end), threads, grab_banners)
    elif choice == '3':
        confirm = input(f"{Colors.RED}⚠️ Full scan takes 10-20 min! Type 'YES': {Colors.RESET}")
        if confirm == 'YES':
            threaded_scan(target, (1, 65535), 200, grab_banners)
    elif choice == '4':
        threaded_scan(target, (1, 1024), 100, grab_banners)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️ Interrupted!{Colors.RESET}")
        sys.exit()