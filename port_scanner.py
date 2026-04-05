#!/usr/bin/env python3
"""
ADVANCED PORT SCANNER V2.0 (FIXED)
Day 2 - Cybersecurity Learning Project

Features:
- Multi-threading (super fast!)
- Service detection
- Banner grabbing
- Save results to file (TXT + CSV)
- Progress tracking
- Color output
- Quick scan mode
"""

import socket
import sys
from datetime import datetime
import threading
from queue import Queue

# ===== COLOR CODES =====
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# ===== PORT DATABASE =====
COMMON_PORTS = {
    20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "Telnet",
    25: "SMTP", 53: "DNS", 69: "TFTP", 80: "HTTP",
    110: "POP3", 123: "NTP", 135: "MSRPC", 139: "NetBIOS",
    143: "IMAP", 161: "SNMP", 443: "HTTPS", 445: "SMB",
    465: "SMTPS", 514: "Syslog", 587: "SMTP", 993: "IMAPS",
    995: "POP3S", 1433: "MSSQL", 1521: "Oracle", 2049: "NFS",
    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 5900: "VNC",
    6379: "Redis", 8000: "HTTP-Alt", 8080: "HTTP-Proxy",
    8443: "HTTPS-Alt", 9200: "Elasticsearch", 27017: "MongoDB"
}

# ===== GLOBAL VARIABLES =====
print_lock = threading.Lock()
open_ports = []
scanned_count = 0
total_ports = 0

# ===== HELPER FUNCTIONS =====

def get_service_name(port):
    """Map port number to service name"""
    return COMMON_PORTS.get(port, "Unknown")

def grab_banner(target, port):
    """
    Try to grab banner from service
    """
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
    """Resolve hostname to IP address"""
    try:
        ip = socket.gethostbyname(target)
        return ip
    except socket.gaierror:
        print(f"{Colors.RED}❌ Cannot resolve hostname: {target}{Colors.RESET}")
        sys.exit()

def save_to_txt(target, ip, open_ports, filename=None):
    """Save scan results to text file"""
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
    """Save scan results to CSV format"""
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
    """Scan single port with optional banner grabbing"""
    global scanned_count
    
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((target, port))
        sock.close()
        
        # Update progress
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

def quick_scan(target, grab_banners=False):
    """Quick scan of most common ports only"""
    global scanned_count, total_ports, open_ports
    
    # Reset globals
    scanned_count = 0
    open_ports = []
    
    common = [21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 
              3306, 3389, 5432, 5900, 8080, 8443]
    
    total_ports = len(common)
    
    # Resolve target
    ip = resolve_hostname(target)
    
    # Print header
    print("\n" + Colors.BOLD + "="*80)
    print(f"           QUICK PORT SCAN (Most Common Ports)")
    print("="*80 + Colors.RESET)
    print(f"{Colors.CYAN}🎯 Target Hostname: {target}{Colors.RESET}")
    print(f"{Colors.CYAN}🎯 Target IP: {ip}{Colors.RESET}")
    print(f"{Colors.CYAN}📊 Scanning {total_ports} common ports{Colors.RESET}")
    print(f"{Colors.CYAN}🔍 Banner Grab: {'Enabled' if grab_banners else 'Disabled'}{Colors.RESET}")
    print(f"{Colors.CYAN}🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
    print(Colors.BOLD + "="*80 + Colors.RESET + "\n")
    
    start_time = datetime.now()
    
    # Scan each port
    for port in common:
        scan_port(ip, port, grab_banners)
    
    # Calculate duration
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Print results
    print("\n" + Colors.BOLD + "="*80)
    print(f"                    QUICK SCAN COMPLETE!")
    print("="*80 + Colors.RESET)
    print(f"{Colors.GREEN}✅ Total Ports Scanned: {total_ports}{Colors.RESET}")
    print(f"{Colors.GREEN}✅ Open Ports Found: {len(open_ports)}{Colors.RESET}")
    print(f"{Colors.GREEN}✅ Scan Duration: {duration:.2f} seconds{Colors.RESET}")
    print(f"{Colors.CYAN}🕐 Finished: {end_time.strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
    print(Colors.BOLD + "="*80 + Colors.RESET + "\n")
    
    # Summary table
    if open_ports:
        print(Colors.BOLD + "📋 DETAILED SUMMARY:" + Colors.RESET)
        print("-"*80)
        print(f"{'PORT':<8} {'SERVICE':<20} {'BANNER/VERSION':<50}")
        print("-"*80)
        for p in open_ports:
            banner = p['banner'][:47] + "..." if p['banner'] and len(p['banner']) > 50 else (p['banner'] or '-')
            print(f"{p['port']:<8} {p['service']:<20} {banner:<50}")
        print("-"*80 + "\n")
    else:
        print(f"{Colors.YELLOW}⚠️ No open ports found in quick scan.{Colors.RESET}\n")
    
    # Save options
    if open_ports:
        save = input(f"{Colors.YELLOW}💾 Save results? (yes/no): {Colors.RESET}").lower()
        if save == 'yes':
            save_to_txt(target, ip, open_ports)
            save_to_csv(target, ip, open_ports)
    
    return open_ports

def threaded_scan(target, port_range, threads=100, grab_banners=False):
    """Multi-threaded port scanner"""
    global scanned_count, total_ports, open_ports
    
    # Reset globals
    scanned_count = 0
    open_ports = []
    total_ports = port_range[1] - port_range[0] + 1
    
    # Resolve target
    ip = resolve_hostname(target)
    
    # Print header
    print("\n" + Colors.BOLD + "="*80)
    print(f"           ADVANCED PORT SCANNER V2.0")
    print("="*80 + Colors.RESET)
    print(f"{Colors.CYAN}🎯 Target Hostname: {target}{Colors.RESET}")
    print(f"{Colors.CYAN}🎯 Target IP: {ip}{Colors.RESET}")
    print(f"{Colors.CYAN}📊 Port Range: {port_range[0]}-{port_range[1]} ({total_ports} ports){Colors.RESET}")
    print(f"{Colors.CYAN}🧵 Threads: {threads}{Colors.RESET}")
    print(f"{Colors.CYAN}🔍 Banner Grab: {'Enabled' if grab_banners else 'Disabled'}{Colors.RESET}")
    print(f"{Colors.CYAN}🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
    print(Colors.BOLD + "="*80 + Colors.RESET + "\n")
    
    # Create port queue
    port_queue = Queue()
    for port in range(port_range[0], port_range[1] + 1):
        port_queue.put(port)
    
    # Worker function
    def worker():
        while not port_queue.empty():
            try:
                port = port_queue.get(timeout=1)
                scan_port(ip, port, grab_banners)
                port_queue.task_done()
            except:
                break
    
    # Start threads
    start_time = datetime.now()
    
    thread_list = []
    for _ in range(threads):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
        thread_list.append(t)
    
    # Wait for completion
    try:
        port_queue.join()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️ Scan interrupted by user!{Colors.RESET}")
        sys.exit()
    
    # Calculate duration
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    # Print results
    print("\n" + Colors.BOLD + "="*80)
    print(f"                    SCAN COMPLETE!")
    print("="*80 + Colors.RESET)
    print(f"{Colors.GREEN}✅ Total Ports Scanned: {total_ports}{Colors.RESET}")
    print(f"{Colors.GREEN}✅ Open Ports Found: {len(open_ports)}{Colors.RESET}")
    print(f"{Colors.GREEN}✅ Scan Duration: {duration:.2f} seconds{Colors.RESET}")
    print(f"{Colors.GREEN}✅ Speed: {total_ports/duration:.1f} ports/second{Colors.RESET}")
    print(f"{Colors.CYAN}🕐 Finished: {end_time.strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
    print(Colors.BOLD + "="*80 + Colors.RESET + "\n")
    
    # Summary table
    if open_ports:
        print(Colors.BOLD + "📋 DETAILED SUMMARY:" + Colors.RESET)
        print("-"*80)
        print(f"{'PORT':<8} {'SERVICE':<20} {'BANNER/VERSION':<50}")
        print("-"*80)
        for p in open_ports:
            banner = p['banner'][:47] + "..." if p['banner'] and len(p['banner']) > 50 else (p['banner'] or '-')
            print(f"{p['port']:<8} {p['service']:<20} {banner:<50}")
        print("-"*80 + "\n")
    
    # Save options
    if open_ports:
        save = input(f"{Colors.YELLOW}💾 Save results? (yes/no): {Colors.RESET}").lower()
        if save == 'yes':
            save_to_txt(target, ip, open_ports)
            save_to_csv(target, ip, open_ports)
    
    return open_ports

# ===== MAIN PROGRAM =====

def print_banner():
    """Print cool ASCII banner"""
    print(f"""
{Colors.CYAN}{Colors.BOLD}
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║          ADVANCED PORT SCANNER V2.0                       ║
    ║          Day 2 - Cybersecurity Learning                   ║
    ║                                                           ║
    ║          Features: Multi-thread, Banner Grab, Export      ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
{Colors.RESET}
    """)

def main():
    """Main program flow"""
    print_banner()
    
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
    
    # Get target
    target = input(f"\n{Colors.YELLOW}Enter target (IP or hostname): {Colors.RESET}").strip()
    if not target:
        print(f"{Colors.RED}❌ Target required!{Colors.RESET}")
        return
    
    # Get banner option
    grab_banners = input(f"{Colors.YELLOW}Grab banners? (yes/no, default: no): {Colors.RESET}").lower() == 'yes'
    
    # Execute based on choice
    if choice == '1':
        quick_scan(target, grab_banners)
        
    elif choice == '2':
        start = int(input(f"{Colors.YELLOW}Start port (default 1): {Colors.RESET}") or 1)
        end = int(input(f"{Colors.YELLOW}End port (default 1000): {Colors.RESET}") or 1000)
        threads = int(input(f"{Colors.YELLOW}Number of threads (default 100): {Colors.RESET}") or 100)
        
        if start < 1 or end > 65535 or start > end:
            print(f"{Colors.RED}❌ Invalid port range!{Colors.RESET}")
            return
        
        threaded_scan(target, (start, end), threads, grab_banners)
        
    elif choice == '3':
        print(f"\n{Colors.RED}⚠️ WARNING: Full scan of 65535 ports will take 10-20 minutes!{Colors.RESET}")
        confirm = input(f"{Colors.YELLOW}Continue? (type 'YES' in capitals): {Colors.RESET}")
        if confirm == 'YES':
            threaded_scan(target, (1, 65535), threads=200, grab_banners=grab_banners)
        else:
            print(f"{Colors.YELLOW}Scan cancelled.{Colors.RESET}")
            
    elif choice == '4':
        threaded_scan(target, (1, 1024), threads=100, grab_banners=grab_banners)
        
    else:
        print(f"{Colors.RED}❌ Invalid choice!{Colors.RESET}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️ Program interrupted!{Colors.RESET}")
        print(f"{Colors.CYAN}👋 Goodbye!{Colors.RESET}")
        sys.exit()
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {e}{Colors.RESET}")
        sys.exit()