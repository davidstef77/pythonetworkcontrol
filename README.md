# 🌐 Network Control System

**Absolute Total Network Control** - A comprehensive Python-based network management system that provides complete control over your network infrastructure.

## 🚀 Features

### 🔍 **Network Discovery**
- **Advanced Device Scanning** - Multi-threaded ping sweeps and port scanning
- **Device Fingerprinting** - OS detection, service identification, device type classification
- **MAC Address Resolution** - ARP-based MAC address discovery
- **Real-time Device Status** - Continuous monitoring of device availability

### ⚡ **Device Control**
- **Wake-on-LAN** - Remotely wake sleeping devices
- **Remote Shutdown/Restart** - Control devices via SSH or WMI
- **Network Access Control** - Block/unblock devices from network access
- **Bandwidth Limiting** - Throttle device bandwidth usage

### 📊 **Network Monitoring**
- **Real-time Monitoring** - Continuous network status updates
- **Traffic Analysis** - Monitor bandwidth usage and network patterns
- **Security Alerts** - Detect new devices and suspicious activity
- **Performance Testing** - Internet speed tests and connectivity checks

### 🛡️ **Security Features**
- **Intrusion Detection** - Monitor for unauthorized access
- **Device Whitelisting** - Control which devices can access the network
- **Firewall Integration** - Automated blocking of suspicious devices
- **Security Logging** - Comprehensive audit trails

### 📱 **Web Dashboard**
- **Real-time Interface** - Live updates via WebSocket
- **Device Management** - Control all devices from web interface
- **Network Visualization** - Charts and graphs of network status
- **Mobile Responsive** - Works on desktop, tablet, and mobile

## 🛠️ Installation

### Prerequisites
- **Python 3.8+**
- **Administrator/Root privileges** (for network control features)
- **Nmap** installed on system
- **Network interface access**

### 1. Clone Repository
```bash
git clone <repository-url>
cd networkcontrol
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. System Dependencies

#### Windows
```bash
# Install Nmap from https://nmap.org/download.html
# Ensure Python and pip are in PATH
```

#### Linux
```bash
sudo apt-get update
sudo apt-get install nmap python3-dev libpcap-dev
```

#### macOS
```bash
brew install nmap
```

### 4. Configuration
Create or modify `network_config.json`:
```json
{
    "default_subnet": "192.168.1.0/24",
    "scan_timeout": 30,
    "monitoring_interval": 60,
    "max_threads": 50,
    "admin_credentials": {
        "192.168.1.100": {
            "username": "admin",
            "password": "password"
        }
    },
    "security_settings": {
        "block_unknown_devices": false,
        "alert_on_new_devices": true,
        "bandwidth_limits": {}
    }
}
```

## 🚀 Usage

### Command Line Interface

#### Basic Network Scan
```python
from network_controller import NetworkController

controller = NetworkController()
devices = controller.discover_network()

for ip, device in devices.items():
    print(f"{ip} - {device['hostname']} ({device['device_type']})")
```

#### Start Monitoring
```python
controller.start_monitoring()
```

#### Device Control
```python
# Wake device
controller.wake_device("aa:bb:cc:dd:ee:ff")

# Shutdown device
controller.shutdown_device("192.168.1.100")

# Block device
controller.block_device("192.168.1.100")

# Limit bandwidth
controller.limit_bandwidth("192.168.1.100", 1000, 500)  # 1000kbit down, 500kbit up
```

### Web Dashboard

#### Start Web Interface
```bash
python web_dashboard.py
```

Then open your browser to: `http://localhost:5000`

#### Dashboard Features
- **🔍 Scan Network** - Discover all devices on network
- **▶️ Start/Stop Monitoring** - Real-time network monitoring
- **🚀 Speed Test** - Test internet connection speed
- **🌍 Connectivity Test** - Test connection to external hosts
- **🔌 Network Interfaces** - View network interface details

#### Device Controls
For each discovered device:
- **💤 Wake** - Send Wake-on-LAN packet
- **🔄 Restart** - Remotely restart device
- **⏹️ Shutdown** - Remotely shutdown device
- **🚫 Block** - Block device from network
- **✅ Unblock** - Restore network access
- **📊 Limit** - Set bandwidth limits

## 🔧 Advanced Configuration

### SSH Credentials
Add SSH credentials for remote device control:
```json
"admin_credentials": {
    "192.168.1.100": {
        "username": "admin",
        "password": "secure_password"
    },
    "192.168.1.101": {
        "username": "root",
        "password": "another_password"
    }
}
```

### Security Settings
```json
"security_settings": {
    "block_unknown_devices": true,
    "alert_on_new_devices": true,
    "bandwidth_limits": {
        "192.168.1.100": {"download": 5000, "upload": 1000}
    }
}
```

### Custom Subnet
```json
"default_subnet": "10.0.0.0/24"
```

## 🛡️ Security Considerations

### Required Privileges
- **Network scanning** requires elevated privileges
- **Device control** needs admin/root access
- **Firewall modification** requires system permissions

### Network Access
- Ensure proper firewall configuration
- Use strong authentication credentials
- Monitor access logs regularly

### Best Practices
- Change default passwords
- Use SSH key authentication when possible
- Regularly update device credentials
- Monitor for unauthorized access

## 📊 API Reference

### NetworkController Class

#### Discovery Methods
```python
discover_network(subnet=None) -> Dict[str, dict]
```

#### Control Methods
```python
wake_device(mac_address: str) -> bool
shutdown_device(ip: str, method: str = "ssh") -> bool
restart_device(ip: str, method: str = "ssh") -> bool
block_device(ip: str) -> bool
unblock_device(ip: str) -> bool
limit_bandwidth(ip: str, download_limit: int, upload_limit: int) -> bool
```

#### Monitoring Methods
```python
start_monitoring() -> None
stop_monitoring() -> None
speed_test() -> dict
test_connectivity(target: str = "8.8.8.8") -> dict
```

### Web API Endpoints

#### Device Management
- `GET /api/devices` - Get all devices
- `POST /api/device/{ip}/wake` - Wake device
- `POST /api/device/{ip}/shutdown` - Shutdown device
- `POST /api/device/{ip}/restart` - Restart device
- `POST /api/device/{ip}/block` - Block device
- `POST /api/device/{ip}/unblock` - Unblock device
- `POST /api/device/{ip}/limit_bandwidth` - Limit bandwidth

#### Network Operations
- `GET /api/scan` - Trigger network scan
- `GET /api/speedtest` - Run speed test
- `GET /api/connectivity/{target}` - Test connectivity
- `GET /api/interfaces` - Get network interfaces

## 🔍 Troubleshooting

### Common Issues

#### Permission Denied
```bash
# Run with elevated privileges
sudo python network_controller.py
```

#### Nmap Not Found
```bash
# Install nmap
sudo apt-get install nmap  # Linux
brew install nmap          # macOS
```

#### Device Not Responding
- Check if device supports Wake-on-LAN
- Verify SSH credentials
- Ensure device is on same network

#### Bandwidth Control Not Working
- Requires root privileges on Linux
- Need proper network interface configuration
- May require additional iptables setup

### Logging
Check `network_control.log` for detailed error messages and debugging information.

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## ⚠️ Disclaimer

This tool provides powerful network control capabilities. Use responsibly and only on networks you own or have explicit permission to manage. The authors are not responsible for any misuse or damage caused by this software.

## 🙏 Acknowledgments

- **Scapy** - Packet manipulation library
- **Nmap** - Network discovery and security auditing
- **Flask** - Web framework for dashboard
- **Chart.js** - Data visualization for web interface
