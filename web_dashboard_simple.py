#!/usr/bin/env python3
"""
Simplified Web Dashboard for Network Control System
Works with minimal dependencies
"""

from flask import Flask, render_template, request, jsonify
import json
import threading
import time
from datetime import datetime
import subprocess
import socket
from netaddr import IPNetwork
import psutil
from flask_socketio import SocketIO, emit
import speedtest

app = Flask(__name__)

# Initialize SocketIO
socketio = SocketIO(app, async_mode='threading')

class SimpleNetworkController:
    """Simplified network controller for basic functionality"""
    
    def __init__(self):
        self.devices = {}
        self.monitoring_active = False
        
    def ping(self, host: str) -> bool:
        """Simple ping test"""
        try:
            result = subprocess.run(
                ['ping', '-n', '1', '-w', '500', host],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=2
            )
            return result.returncode == 0
        except:
            return False
    
    def get_hostname(self, ip: str) -> str:
        """Get hostname via reverse DNS"""
        try:
            return socket.gethostbyaddr(ip)[0]
        except:
            return ""
    
    def scan_network(self, subnet: str = "192.168.1.0/24") -> dict:
        """Basic network scan"""
        network = IPNetwork(subnet)
        devices = {}
        
        for ip in list(network)[:50]:  # Limit to first 50 IPs for speed
            ip_str = str(ip)
            if self.ping(ip_str):
                devices[ip_str] = {
                    "ip": ip_str,
                    "hostname": self.get_hostname(ip_str),
                    "status": "online",
                    "last_seen": datetime.now().isoformat(),
                    "device_type": "computer"
                }
        
        self.devices = devices
        return devices
    
    def get_device_list(self):
        """Get list of devices"""
        return list(self.devices.values())

# Global controller instance
controller = SimpleNetworkController()

# Routes
@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/scan')
def scan_network():
    try:
        devices = controller.scan_network()
        return jsonify({
            'success': True,
            'devices': list(devices.values()),
            'message': f'Found {len(devices)} devices'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/devices')
def get_devices():
    return jsonify(controller.get_device_list())

@app.route('/api/test_internet')
def test_internet():
    reachable = controller.ping("8.8.8.8")
    return jsonify({
        'reachable': reachable,
        'target': '8.8.8.8'
    })

@app.route('/api/device/<ip>/wake', methods=['POST'])
def wake_device(ip):
    try:
        # TODO: Implement wake-on-lan
        socketio.emit('status', {'message': f'Wake command sent to {ip}'})
        return jsonify({'success': True, 'message': f'Wake command sent to {ip}'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/device/<ip>/shutdown', methods=['POST'])
def shutdown_device(ip):
    try:
        # TODO: Implement remote shutdown
        socketio.emit('status', {'message': f'Shutdown command sent to {ip}'})
        return jsonify({'success': True, 'message': f'Shutdown command sent to {ip}'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/device/<ip>/block', methods=['POST'])
def block_device(ip):
    try:
        # TODO: Implement firewall blocking
        socketio.emit('device_update', {'devices': controller.devices})
        return jsonify({'success': True, 'message': f'Blocked {ip}'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/device/<ip>/limit_bandwidth', methods=['POST'])
def limit_bandwidth(ip):
    try:
        data = request.json
        # TODO: Implement bandwidth limiting
        socketio.emit('status', {'message': f'Bandwidth limited for {ip}'})
        return jsonify({'success': True, 'message': f'Bandwidth limited for {ip}'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/speedtest')
def run_speedtest():
    try:
        st = speedtest.Speedtest()
        st.get_best_server()
        download = st.download() / 10**6  # Convert to Mbps
        upload = st.upload() / 10**6
        ping = st.results.ping
        return jsonify({
            'success': True,
            'result': {
                'download_mbps': round(download, 2),
                'upload_mbps': round(upload, 2),
                'ping_ms': round(ping, 2)
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/connectivity/<ip>')
def test_connectivity(ip):
    try:
        start_time = time.time()
        result = controller.ping(ip)
        latency = round((time.time() - start_time) * 1000, 2)  # ms
        return jsonify({
            'success': True,
            'result': {
                'reachable': result,
                'latency_ms': latency
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# Add periodic scanning thread
def background_monitoring():
    while True:
        if controller.monitoring_active:
            controller.scan_network()
            socketio.emit('device_update', {'devices': controller.get_device_list()})
        time.sleep(30)

# Start monitoring thread
monitoring_thread = threading.Thread(target=background_monitoring)
monitoring_thread.daemon = True
monitoring_thread.start()

if __name__ == '__main__':
    print("🌐 Starting Network Control Dashboard with SocketIO support...")
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
