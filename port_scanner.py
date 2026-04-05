# port_scanner.py
# Day 2 - Network Security Learning

import socket
import sys
from datetime import datetime

# ===== PORT DATABASE =====
COMMON_PORTS = {
    20: "FTP-DATA",
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    445: "SMB",
    3306: "MySQL",
    3389: "RDP",
    5432: "PostgreSQL",
    5900: "VNC",
    8080: "HTTP-Proxy",
    8443: "HTTPS-Alt",
}

def get_service_name(port):
    """
    Return nama service berdasarkan port number
    """
    return COMMON_PORTS.get(port, "Unknown")

def scan_port_with_service(target, port):
    """
    Scan port dan identifikasi service
    """
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((target, port))
        sock.close()
        
        if result == 0:
            service = get_service_name(port)
            return True, service
        return False, None
        
    except:
        return False, None

def scan_with_service_detection(target, start_port, end_port):
    """
    Enhanced scan dengan service detection
    """
    print("\n" + "="*70)
    print(f"🎯 Target: {target}")
    print(f"📊 Scanning ports {start_port}-{end_port}")
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    print(f"\n{'PORT':<8} {'STATE':<10} {'SERVICE':<20}")
    print("-"*70)
    
    open_ports = []
    
    try:
        for port in range(start_port, end_port + 1):
            # Progress indicator
            print(f"Scanning port {port}...", end='\r')
            
            is_open, service = scan_port_with_service(target, port)
            
            if is_open:
                state = "OPEN"
                print(f"{port:<8} {state:<10} {service:<20}")
                open_ports.append((port, service))
        
        print("\n" + "-"*70)
        print(f"✅ Scan Complete! Found {len(open_ports)} open port(s)")
        print(f"🕐 Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*70 + "\n")
        
        return open_ports
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Scan cancelled!")
        sys.exit()

# ===== MAIN PROGRAM =====
if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════╗
    ║         PORT SCANNER - Day 2 Project          ║
    ║           Cybersecurity Learning              ║
    ╚═══════════════════════════════════════════════╝
    """)
    
    # User input
    target = input("Enter target (IP or hostname): ").strip()
    
    if not target:
        target = "scanme.nmap.org"  # Default target
        print(f"⚠️ No target specified. Using default: {target}")
    
    start_port = input("Start port (default 1): ").strip()
    start_port = int(start_port) if start_port else 1
    
    end_port = input("End port (default 100): ").strip()
    end_port = int(end_port) if end_port else 100
    
    # Validate
    if start_port < 1 or end_port > 65535 or start_port > end_port:
        print("❌ Invalid port range! (1-65535)")
        sys.exit()
    
    # Warning untuk scan besar
    total_ports = end_port - start_port + 1
    if total_ports > 1000:
        print(f"\n⚠️ WARNING: Scanning {total_ports} ports will take a while!")
        confirm = input("Continue? (yes/no): ").lower()
        if confirm != 'yes':
            print("Scan cancelled.")
            sys.exit()
    
    # Run scan
    scan_with_service_detection(target, start_port, end_port)