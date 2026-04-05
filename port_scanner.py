import socket
from datetime import datetime

def scan_single_port(target, port):
    """Scan satu port (sama seperti sebelumnya)"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((target, port))
        sock.close()
        return result == 0
    except:
        return False

def scan_port_range(target, start_port, end_port):
    """
    Scan range port dari start sampai end
    """
    print("\n" + "="*60)
    print(f"🎯 Target: {target}")
    print(f"📊 Port Range: {start_port} - {end_port}")
    print(f"🕐 Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")
    
    open_ports = []
    
    try:
        # Loop dari start sampai end port
        for port in range(start_port, end_port + 1):
            # Progress indicator
            print(f"Scanning port {port}...", end='\r')
            
            if scan_single_port(target, port):
                print(f"✅ Port {port} is OPEN" + " "*20)
                open_ports.append(port)
        
        print("\n" + "="*60)
        print(f"✅ Scan Complete!")
        print(f"📊 Total Open Ports: {len(open_ports)}")
        if open_ports:
            print(f"🔓 Open Ports: {open_ports}")
        print("="*60)
        
        return open_ports
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Scan interrupted by user!")
        sys.exit()

# Test
if __name__ == "__main__":
    target = "127.0.0.1"
    scan_port_range(target, 1, 100)