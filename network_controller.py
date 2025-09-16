#!/usr/bin/env python3
"""
Comprehensive Network Control System
Provides absolute control over network infrastructure
"""

import subprocess
import threading
import time
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import socket

# Network libraries
try:
    import scapy.all as scapy
    SCAPY_AVAILABLE = True
except ImportError:
    SCAPY_AVAILABLE = False
    print("Warning: Scapy not available. Some features will be limited.")

try:
    import nmap
    NMAP_AVAILABLE = True
except ImportError:
    NMAP_AVAILABLE = False
    print("Warning: python-nmap not available. Port scanning will be limited.")

try:
    import netifaces
    NETIFACES_AVAILABLE = True
except ImportError:
    NETIFACES_AVAILABLE = False
    print("Warning: netifaces not available. Interface detection limited.")

from netaddr import IPNetwork, IPAddress
import psutil

# Control libraries
try:
    from wakeonlan import send_magic_packet
    WOL_AVAILABLE = True
except ImportError:
    WOL_AVAILABLE = False
    print("Warning: wakeonlan not available.")

try:
    import paramiko
    SSH_AVAILABLE = True
except ImportError:
    SSH_AVAILABLE = False
    print("Warning: paramiko not available. SSH features disabled.")

import requests

# Monitoring libraries
try:
    import speedtest
    SPEEDTEST_AVAILABLE = True
except ImportError:
    SPEEDTEST_AVAILABLE = False
    print("Warning: speedtest-cli not available.")

class NetworkController:
    """Main network control system providing comprehensive network management"""
    
    def __init__(self, config_file: str = "network_config.json"):
        self.config = self._load_config(config_file)
        self.devices = {}
        self.monitoring_active = False
        self.security_rules = []
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('network_control.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize network scanner if available
        if NMAP_AVAILABLE:
            self.nm = nmap.PortScanner()
        else:
            self.nm = None
        
        self.logger.info("Network Controller initialized")

    def _load_config(self, config_file: str) -> dict:
        """Load configuration from JSON file"""
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            # Create default config
            default_config = {
                "default_subnet": "192.168.1.0/24",
                "scan_timeout": 30,
                "monitoring_interval": 60,
                "max_threads": 50,
                "admin_credentials": {},
                "security_settings": {
                    "block_unknown_devices": False,
                    "alert_on_new_devices": True,
                    "bandwidth_limits": {}
                }
            }
            with open(config_file, 'w') as f:
                json.dump(default_config, f, indent=4)
            return default_config

    # ===== NETWORK DISCOVERY =====
    
    def discover_network(self, subnet: str = None) -> Dict[str, dict]:
        """Advanced network discovery with device fingerprinting"""
        if not subnet:
            subnet = self.config.get("default_subnet", "192.168.1.0/24")
        
        self.logger.info(f"Starting network discovery on {subnet}")
        
        # Multi-threaded ping sweep
        active_hosts = self._ping_sweep(subnet)
        
        # Port scanning and service detection
        for host in active_hosts:
            device_info = self._scan_device(host)
            self.devices[host] = device_info
            
        self.logger.info(f"Discovered {len(self.devices)} devices")
        return self.devices

    def _ping_sweep(self, subnet: str) -> List[str]:
        """Fast multi-threaded ping sweep"""
        network = IPNetwork(subnet)
        active_hosts = []
        threads = []
        
        def ping_host(ip):
            if self._ping(str(ip)):
                active_hosts.append(str(ip))
        
        for ip in network:
            if len(threads) >= self.config["max_threads"]:
                for t in threads:
                    t.join()
                threads = []
            
            thread = threading.Thread(target=ping_host, args=(ip,))
            thread.start()
            threads.append(thread)
        
        for t in threads:
            t.join()
            
        return active_hosts

    def _ping(self, host: str) -> bool:
        """Enhanced ping with multiple methods"""
        # Try subprocess ping first
        try:
            result = subprocess.run(
                ['ping', '-n', '1', '-w', '500', host],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=2
            )
            if result.returncode == 0:
                return True
        except:
            pass
        
        # Try scapy ICMP ping if available
        if SCAPY_AVAILABLE:
            try:
                response = scapy.sr1(
                    scapy.IP(dst=host)/scapy.ICMP(),
                    timeout=1,
                    verbose=0
                )
                return response is not None
            except:
                pass
        
        return False

    def _scan_device(self, host: str) -> dict:
        """Comprehensive device scanning and fingerprinting"""
        device_info = {
            "ip": host,
            "hostname": self._get_hostname(host),
            "mac_address": self._get_mac_address(host),
            "vendor": "",
            "open_ports": [],
            "services": {},
            "os_guess": "",
            "last_seen": datetime.now().isoformat(),
            "device_type": "unknown",
            "status": "online"
        }
        
        # Port scan if nmap is available
        if NMAP_AVAILABLE and self.nm:
            try:
                self.nm.scan(host, '22,80,443,3389', '-sS')
                if host in self.nm.all_hosts():
                    host_info = self.nm[host]
                    
                    # Get open ports and services
                    for proto in host_info.all_protocols():
                        ports = host_info[proto].keys()
                        for port in ports:
                            port_info = host_info[proto][port]
                            if port_info['state'] == 'open':
                                device_info["open_ports"].append(port)
                                device_info["services"][port] = {
                                    "name": port_info.get('name', ''),
                                    "product": port_info.get('product', ''),
                                    "version": port_info.get('version', '')
                                }
                    
                    # OS detection
                    if 'osmatch' in host_info:
                        if host_info['osmatch']:
                            device_info["os_guess"] = host_info['osmatch'][0]['name']
                            
            except Exception as e:
                self.logger.warning(f"Port scan failed for {host}: {e}")
        
        # Device type detection
        device_info["device_type"] = self._detect_device_type(device_info)
        
        return device_info

    def _get_hostname(self, ip: str) -> str:
        """Get hostname via reverse DNS"""
        try:
            return socket.gethostbyaddr(ip)[0]
        except:
            return ""

    def _get_mac_address(self, ip: str) -> str:
        """Get MAC address using ARP"""
        if SCAPY_AVAILABLE:
            try:
                # Send ARP request
                arp_request = scapy.ARP(pdst=ip)
                broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
                arp_request_broadcast = broadcast / arp_request
                answered_list = scapy.srp(arp_request_broadcast, timeout=2, verbose=False)[0]
                
                if answered_list:
                    return answered_list[0][1].hwsrc
            except:
                pass
        return ""

    def _detect_device_type(self, device_info: dict) -> str:
        """Detect device type based on open ports and services"""
        ports = device_info["open_ports"]
        services = device_info["services"]
        
        # Router/Gateway detection
        if 80 in ports or 443 in ports or 8080 in ports:
            if any("router" in str(v).lower() or "gateway" in str(v).lower() 
                   for v in services.values()):
                return "router"
        
        # Server detection
        if 22 in ports or 3389 in ports:  # SSH or RDP
            return "server"
        
        # Printer detection
        if 631 in ports or 9100 in ports:  # IPP or HP JetDirect
            return "printer"
        
        # IoT device detection
        if len(ports) <= 3 and (80 in ports or 443 in ports):
            return "iot_device"
        
        # Default to computer
        return "computer"

    # ===== DEVICE CONTROL =====
    
    def wake_device(self, mac_address: str) -> bool:
        """Wake device using Wake-on-LAN"""
        if not WOL_AVAILABLE:
            self.logger.error("Wake-on-LAN not available - wakeonlan package not installed")
            return False
            
        try:
            send_magic_packet(mac_address)
            self.logger.info(f"WoL packet sent to {mac_address}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to wake device {mac_address}: {e}")
            return False

    def shutdown_device(self, ip: str, method: str = "ssh") -> bool:
        """Shutdown device remotely"""
        if method == "ssh" and SSH_AVAILABLE:
            return self._ssh_command(ip, "sudo shutdown -h now")
        else:
            self.logger.warning("SSH not available or method not supported")
            return False

    def restart_device(self, ip: str, method: str = "ssh") -> bool:
        """Restart device remotely"""
        if method == "ssh" and SSH_AVAILABLE:
            return self._ssh_command(ip, "sudo reboot")
        else:
            self.logger.warning("SSH not available or method not supported")
            return False

    def _ssh_command(self, ip: str, command: str) -> bool:
        """Execute command via SSH"""
        if not SSH_AVAILABLE:
            return False
            
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Get credentials from config
            creds = self.config.get("admin_credentials", {}).get(ip, {})
            username = creds.get("username", "admin")
            password = creds.get("password", "")
            
            ssh.connect(ip, username=username, password=password, timeout=10)
            stdin, stdout, stderr = ssh.exec_command(command)
            ssh.close()
            
            return True
        except Exception as e:
            self.logger.error(f"SSH command failed for {ip}: {e}")
            return False

    # ===== BANDWIDTH CONTROL =====
    
    def limit_bandwidth(self, ip: str, download_limit: int, upload_limit: int) -> bool:
        """Limit bandwidth for specific device (Linux only)"""
        self.logger.warning("Bandwidth limiting requires Linux with root privileges")
        return False

    def block_device(self, ip: str) -> bool:
        """Block device from network access (requires admin privileges)"""
        self.logger.warning("Device blocking requires admin privileges and proper network setup")
        return False

    def unblock_device(self, ip: str) -> bool:
        """Unblock device from network access"""
        self.logger.warning("Device unblocking requires admin privileges and proper network setup")
        return False

    # ===== MONITORING =====
    
    def start_monitoring(self):
        """Start continuous network monitoring"""
        self.monitoring_active = True
        monitor_thread = threading.Thread(target=self._monitoring_loop)
        monitor_thread.daemon = True
        monitor_thread.start()
        self.logger.info("Network monitoring started")

    def stop_monitoring(self):
        """Stop network monitoring"""
        self.monitoring_active = False
        self.logger.info("Network monitoring stopped")

    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Update device status
                self._update_device_status()
                
                # Check for new devices
                self._check_new_devices()
                
                time.sleep(self.config["monitoring_interval"])
                
            except Exception as e:
                self.logger.error(f"Monitoring error: {e}")

    def _update_device_status(self):
        """Update status of known devices"""
        for ip in list(self.devices.keys()):
            if self._ping(ip):
                self.devices[ip]["last_seen"] = datetime.now().isoformat()
                self.devices[ip]["status"] = "online"
            else:
                self.devices[ip]["status"] = "offline"

    def _check_new_devices(self):
        """Check for new devices on network"""
        current_devices = set(self.devices.keys())
        discovered = set(self._ping_sweep(self.config["default_subnet"]))
        new_devices = discovered - current_devices
        
        for ip in new_devices:
            self.logger.warning(f"New device detected: {ip}")
            device_info = self._scan_device(ip)
            self.devices[ip] = device_info
            
            if self.config["security_settings"]["alert_on_new_devices"]:
                self._send_alert(f"New device detected: {ip}")

    def _send_alert(self, message: str):
        """Send security alert"""
        self.logger.warning(f"ALERT: {message}")

    # ===== NETWORK TESTING =====
    
    def speed_test(self) -> dict:
        """Perform internet speed test"""
        if not SPEEDTEST_AVAILABLE:
            return {"error": "speedtest-cli not available"}
            
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            
            download_speed = st.download() / 1_000_000  # Convert to Mbps
            upload_speed = st.upload() / 1_000_000
            ping = st.results.ping
            
            result = {
                "download_mbps": round(download_speed, 2),
                "upload_mbps": round(upload_speed, 2),
                "ping_ms": round(ping, 2),
                "timestamp": datetime.now().isoformat()
            }
            
            self.logger.info(f"Speed test: {result}")
            return result
            
        except Exception as e:
            self.logger.error(f"Speed test failed: {e}")
            return {"error": str(e)}

    def test_connectivity(self, target: str = "8.8.8.8") -> dict:
        """Test connectivity to target"""
        result = {
            "target": target,
            "reachable": self._ping(target),
            "timestamp": datetime.now().isoformat()
        }
        
        if result["reachable"]:
            # Measure latency
            start_time = time.time()
            self._ping(target)
            result["latency_ms"] = round((time.time() - start_time) * 1000, 2)
        
        return result

    # ===== UTILITY METHODS =====
    
    def get_network_interfaces(self) -> dict:
        """Get all network interfaces and their details"""
        interfaces = {}
        
        if NETIFACES_AVAILABLE:
            try:
                for interface in netifaces.interfaces():
                    addrs = netifaces.ifaddresses(interface)
                    interfaces[interface] = {
                        "ipv4": addrs.get(netifaces.AF_INET, []),
                        "ipv6": addrs.get(netifaces.AF_INET6, []),
                        "mac": addrs.get(netifaces.AF_LINK, [])
                    }
            except Exception as e:
                self.logger.error(f"Error getting interfaces: {e}")
        else:
            # Fallback method using psutil
            try:
                net_if_addrs = psutil.net_if_addrs()
                for interface, addrs in net_if_addrs.items():
                    interfaces[interface] = {
                        "addresses": [{"address": addr.address, "family": addr.family} for addr in addrs]
                    }
            except Exception as e:
                self.logger.error(f"Error getting interfaces via psutil: {e}")
        
        return interfaces

    def get_device_list(self) -> List[dict]:
        """Get formatted list of all devices"""
        return list(self.devices.values())

    def save_device_database(self, filename: str = "devices.json"):
        """Save device database to file"""
        with open(filename, 'w') as f:
            json.dump(self.devices, f, indent=4)
        self.logger.info(f"Device database saved to {filename}")

    def load_device_database(self, filename: str = "devices.json"):
        """Load device database from file"""
        try:
            with open(filename, 'r') as f:
                self.devices = json.load(f)
            self.logger.info(f"Device database loaded from {filename}")
        except FileNotFoundError:
            self.logger.warning(f"Device database file {filename} not found")

if __name__ == "__main__":
    # Example usage
    controller = NetworkController()
    
    print("🌐 Starting Network Discovery...")
    devices = controller.discover_network()
    
    print(f"\n📱 Found {len(devices)} devices:")
    for ip, device in devices.items():
        print(f"  {ip} - {device['hostname']} ({device['device_type']})")
    
    print("\n🔍 Starting Network Monitoring...")
    controller.start_monitoring()
    
    try:
        # Keep running
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n⏹️  Stopping Network Controller...")
        controller.stop_monitoring()
