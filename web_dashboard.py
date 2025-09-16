#!/usr/bin/env python3
"""
Web Dashboard for Network Control System
Provides real-time monitoring and control interface
"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_socketio import SocketIO, emit
import json
import threading
import time
from datetime import datetime
from network_controller import NetworkController

app = Flask(__name__)
app.config['SECRET_KEY'] = 'network_control_secret_key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global network controller instance
controller = NetworkController()

class WebDashboard:
    def __init__(self):
        self.controller = controller
        self.update_thread = None
        self.running = False

    def start_real_time_updates(self):
        """Start real-time updates for web dashboard"""
        self.running = True
        self.update_thread = threading.Thread(target=self._update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()

    def _update_loop(self):
        """Send real-time updates to connected clients"""
        while self.running:
            try:
                # Get current network status
                devices = self.controller.get_device_list()
                network_stats = self._get_network_stats()
                
                # Emit updates to all connected clients
                socketio.emit('device_update', {
                    'devices': devices,
                    'stats': network_stats,
                    'timestamp': datetime.now().isoformat()
                })
                
                time.sleep(5)  # Update every 5 seconds
                
            except Exception as e:
                print(f"Update loop error: {e}")

    def _get_network_stats(self):
        """Get network statistics"""
        return {
            'total_devices': len(self.controller.devices),
            'online_devices': sum(1 for d in self.controller.devices.values() 
                                if d.get('status') == 'online'),
            'device_types': self._count_device_types()
        }

    def _count_device_types(self):
        """Count devices by type"""
        types = {}
        for device in self.controller.devices.values():
            device_type = device.get('device_type', 'unknown')
            types[device_type] = types.get(device_type, 0) + 1
        return types

dashboard = WebDashboard()

# ===== WEB ROUTES =====

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/devices')
def get_devices():
    """API endpoint to get all devices"""
    return jsonify(controller.get_device_list())

@app.route('/api/scan')
def scan_network():
    """API endpoint to trigger network scan"""
    try:
        devices = controller.discover_network()
        return jsonify({
            'success': True,
            'message': f'Discovered {len(devices)} devices',
            'devices': list(devices.values())
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Scan failed: {str(e)}'
        })

@app.route('/api/device/<ip>/wake', methods=['POST'])
def wake_device(ip):
    """Wake device via Wake-on-LAN"""
    try:
        device = controller.devices.get(ip)
        if not device:
            return jsonify({'success': False, 'message': 'Device not found'})
        
        mac = device.get('mac_address')
        if not mac:
            return jsonify({'success': False, 'message': 'MAC address not available'})
        
        success = controller.wake_device(mac)
        return jsonify({
            'success': success,
            'message': 'Wake-on-LAN packet sent' if success else 'Failed to wake device'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/device/<ip>/shutdown', methods=['POST'])
def shutdown_device(ip):
    """Shutdown device remotely"""
    try:
        success = controller.shutdown_device(ip)
        return jsonify({
            'success': success,
            'message': 'Shutdown command sent' if success else 'Failed to shutdown device'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/device/<ip>/restart', methods=['POST'])
def restart_device(ip):
    """Restart device remotely"""
    try:
        success = controller.restart_device(ip)
        return jsonify({
            'success': success,
            'message': 'Restart command sent' if success else 'Failed to restart device'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/device/<ip>/block', methods=['POST'])
def block_device(ip):
    """Block device from network"""
    try:
        success = controller.block_device(ip)
        return jsonify({
            'success': success,
            'message': 'Device blocked' if success else 'Failed to block device'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/device/<ip>/unblock', methods=['POST'])
def unblock_device(ip):
    """Unblock device from network"""
    try:
        success = controller.unblock_device(ip)
        return jsonify({
            'success': success,
            'message': 'Device unblocked' if success else 'Failed to unblock device'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/device/<ip>/limit_bandwidth', methods=['POST'])
def limit_bandwidth(ip):
    """Limit device bandwidth"""
    try:
        data = request.get_json()
        download_limit = data.get('download_limit', 1000)
        upload_limit = data.get('upload_limit', 1000)
        
        success = controller.limit_bandwidth(ip, download_limit, upload_limit)
        return jsonify({
            'success': success,
            'message': f'Bandwidth limited to {download_limit}kbit down, {upload_limit}kbit up' if success else 'Failed to limit bandwidth'
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/speedtest')
def run_speedtest():
    """Run internet speed test"""
    try:
        result = controller.speed_test()
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/connectivity/<target>')
def test_connectivity(target):
    """Test connectivity to target"""
    try:
        result = controller.test_connectivity(target)
        return jsonify({
            'success': True,
            'result': result
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/interfaces')
def get_interfaces():
    """Get network interfaces"""
    try:
        interfaces = controller.get_network_interfaces()
        return jsonify({
            'success': True,
            'interfaces': interfaces
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

# ===== SOCKETIO EVENTS =====

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('status', {'message': 'Connected to Network Control System'})

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@socketio.on('start_monitoring')
def handle_start_monitoring():
    """Start network monitoring"""
    controller.start_monitoring()
    dashboard.start_real_time_updates()
    emit('status', {'message': 'Network monitoring started'})

@socketio.on('stop_monitoring')
def handle_stop_monitoring():
    """Stop network monitoring"""
    controller.stop_monitoring()
    dashboard.running = False
    emit('status', {'message': 'Network monitoring stopped'})

if __name__ == '__main__':
    # Start the web dashboard
    print("🌐 Starting Network Control Web Dashboard...")
    print("📊 Dashboard will be available at: http://localhost:5000")
    
    # Start monitoring automatically
    controller.start_monitoring()
    dashboard.start_real_time_updates()
    
    # Run the Flask app
    socketio.run(app, host='0.0.0.0', port=5000, debug=False)
