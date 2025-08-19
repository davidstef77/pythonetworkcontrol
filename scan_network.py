# Verifica toate dispozitivele active pe rețeaua locală

import subprocess

def ping(host):
    """Returnează True dacă hostul răspunde la ping, altfel False."""
    result = subprocess.run(['ping', '-n', '1', '-w', '500', host],
                            stdout=subprocess.DEVNULL)
    return result.returncode == 0

def scan_network(subnet):
    """Scanează subnetul și returnează lista IP-urilor active."""
    live_hosts = []
    for i in range(1, 255 ):
        ip = f"{subnet}.{i}"
        if ping(ip):
            live_hosts.append(ip)
    return live_hosts

# Setează subnetul tău local (fără ultimul octet)
subnet = "192.168.0"
devices = scan_network(subnet)
print("Dispozitive active pe rețea:")
for ip in devices:
    print(ip)
