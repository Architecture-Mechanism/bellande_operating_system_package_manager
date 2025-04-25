# Copyright (C) 2024 Bellande Algorithm Model Research Innovation Center, Ronaldson Bellande

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

#!/usr/bin/env python3

import os, sys, time, signal, logging, argparse, threading, socketserver, json, hashlib, tarfile, shutil, re, platform, daemon, requests, subprocess
from typing import Dict, List, Optional, Union, Any
from pathlib import Path
from daemon import pidfile

# Import from the original script
# Using the Bellande_Format parser from the original code
from bellande_parser.bellande_parser import Bellande_Format

# Configuration
CONFIG_DIR = os.path.expanduser('~/.bospm')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.bellande')
PACKAGE_DIR = os.path.join(CONFIG_DIR, 'packages')
REPO_DIR = os.path.join(CONFIG_DIR, 'repo')
INSTALL_DIR = os.path.join(CONFIG_DIR, 'installed')
SERVICES_DIR = os.path.join(CONFIG_DIR, 'services')
LOG_FILE = os.path.join(CONFIG_DIR, 'bospm_service.log')
PID_FILE = os.path.join(CONFIG_DIR, 'bospm_service.pid')
SOCKET_FILE = os.path.join(CONFIG_DIR, 'bospm_service.sock')

# Repository and website URLs (from the original script)
BELLANDEGIT_REPO = "https://git.bellande-technologies.com/BAMRI/bellande_operating_system_package_configuration/blob/main/executable/bellandeos_packages_configuration.bellande"
GITHUB_REPO = "https://github.com/Architecture-Mechanism/bellande_operating_system_package_configuration/blob/main/executable/bellandeos_packages_configuration.bellande"
GITLAB_REPO = "https://gitlab.com/Bellande-Architecture-Mechanism-Research-Innovation/bellande_operating_system_package_configuration/blob/main/executable/bellandeos_packages_configuration.bellande"
BITBUCKET_REPO = "https://bitbucket.org/bellande-architecture-mechanism/bellande_operating_system_package_configuration/src/main/executable/bellandeos_packages_configuration.bellande"
BELLANDE_TECH_WEBSITE = "https://bellande-technologies.com/bospm_packages/bellandeos_packages_configuration.bellande"
BELLANDE_LABS_WEBSITE = "https://bellande-laboratories.org/bospm_packages/bellandeos_packages_configuration.bellande"
BELLANDE_ARCH_WEBSITE = "https://bellande-architecture-mechanism-research-innovation-center.org/bospm_packages/bellandeos_packages_configuration.bellande"

# Set up logging
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('bospm_service')

# Ensure directories exist
def ensure_dirs():
    for dir_path in [CONFIG_DIR, PACKAGE_DIR, REPO_DIR, INSTALL_DIR, SERVICES_DIR]:
        os.makedirs(dir_path, exist_ok=True)

# Utility functions (from the original script)
def calculate_checksum(file_path: str) -> str:
    with open(file_path, "rb") as f:
        file_hash = hashlib.sha256()
        chunk = f.read(8192)
        while chunk:
            file_hash.update(chunk)
            chunk = f.read(8192)
    return file_hash.hexdigest()

def compare_versions(version1: str, version2: str) -> int:
    v1_parts = [int(x) for x in version1.split('.')]
    v2_parts = [int(x) for x in version2.split('.')]
    for i in range(max(len(v1_parts), len(v2_parts))):
        v1 = v1_parts[i] if i < len(v1_parts) else 0
        v2 = v2_parts[i] if i < len(v2_parts) else 0
        if v1 > v2:
            return 1
        elif v1 < v2:
            return -1
    return 0

def is_valid_version(version: str) -> bool:
    return bool(re.match(r'^\d+(\.\d+)*$', version))

def get_system_info() -> Dict[str, str]:
    return {
        "os": platform.system().lower(),
        "architecture": platform.machine().lower(),
        "python_version": platform.python_version()
    }

# Package management functions
def load_config() -> Dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return Bellande_Format.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
    return {'installed_packages': {}, 'services': {}}

def save_config(config: Dict):
    try:
        with open(CONFIG_FILE, 'w') as f:
            Bellande_Format.dump(config, f, indent=2)
    except Exception as e:
        logger.error(f"Error saving config: {str(e)}")

# Function implementations (from original script)
def create_package(package_name: str, version: str, files: List[str], os_target: str = None, arch_target: str = None, 
                   is_service: bool = False, service_executable: str = None, service_args: List[str] = None) -> Dict[str, Any]:
    try:
        ensure_dirs()
        if not is_valid_version(version):
            return {"status": "error", "message": f"Invalid version format: {version}"}

        system_info = get_system_info()
        os_target = os_target or system_info["os"]
        arch_target = arch_target or system_info["architecture"]

        package_file = f"{package_name}-{version}-{os_target}-{arch_target}.tar.gz"
        package_path = os.path.join(REPO_DIR, package_file)
        
        with tarfile.open(package_path, "w:gz") as tar:
            for file in files:
                if not os.path.exists(file):
                    return {"status": "error", "message": f"File not found: {file}"}
                tar.add(file, arcname=os.path.basename(file))
        
        checksum = calculate_checksum(package_path)
        
        package_info = {
            "name": package_name,
            "version": version,
            "os": os_target,
            "architecture": arch_target,
            "files": [os.path.basename(f) for f in files],
            "checksum": checksum,
            "is_service": is_service
        }
        
        if is_service and service_executable:
            package_info["service_executable"] = service_executable
            if service_args:
                package_info["service_args"] = service_args
        
        info_file = os.path.join(REPO_DIR, f"{package_name}-{version}-{os_target}-{arch_target}.bellande")
        with open(info_file, 'w') as f:
            Bellande_Format.dump(package_info, f, indent=2)
        
        return {"status": "success", "message": f"Package {package_name} version {version} for {os_target}-{arch_target} created successfully."}
    except Exception as e:
        logger.error(f"Error creating package: {str(e)}")
        return {"status": "error", "message": f"Failed to create package: {str(e)}"}

def get_package_info(package_name: str, version: str, os_target: str = None, arch_target: str = None) -> Dict:
    system_info = get_system_info()
    os_target = os_target or system_info["os"]
    arch_target = arch_target or system_info["architecture"]

    info_file = os.path.join(REPO_DIR, f"{package_name}-{version}-{os_target}-{arch_target}.bellande")
    if not os.path.exists(info_file):
        raise FileNotFoundError(f"Package {package_name} version {version} for {os_target}-{arch_target} not found.")
    
    try:
        with open(info_file, 'r') as f:
            return Bellande_Format.load(f)
    except Exception as e:
        logger.error(f"Error getting package info: {str(e)}")
        raise

def install_package(package_name: str, version: str, os_target: str = None, arch_target: str = None, start_service: bool = True) -> Dict[str, Any]:
    try:
        config = load_config()
        ensure_dirs()
        
        system_info = get_system_info()
        os_target = os_target or system_info["os"]
        arch_target = arch_target or system_info["architecture"]

        if package_name in config['installed_packages']:
            installed_version = config['installed_packages'][package_name]['version']
            if compare_versions(version, installed_version) <= 0:
                return {"status": "info", "message": f"Package {package_name} version {installed_version} is already installed and up to date."}
            logger.info(f"Upgrading {package_name} from version {installed_version} to {version}")
            
            # Stop service if it's running
            if package_name in config.get('services', {}):
                stop_service(package_name)

        try:
            package_info = get_package_info(package_name, version, os_target, arch_target)
            package_file = f"{package_name}-{version}-{os_target}-{arch_target}.tar.gz"
            package_path = os.path.join(REPO_DIR, package_file)
            
            if not os.path.exists(package_path):
                return {"status": "error", "message": f"Package file {package_file} not found."}
            
            if calculate_checksum(package_path) != package_info['checksum']:
                return {"status": "error", "message": "Package checksum mismatch. The package may have been tampered with."}
            
            extract_dir = os.path.join(INSTALL_DIR, package_name, version)
            os.makedirs(extract_dir, exist_ok=True)
            with tarfile.open(package_path, "r:gz") as tar:
                tar.extractall(path=extract_dir)
            
            config['installed_packages'][package_name] = {
                'version': version,
                'os': os_target,
                'architecture': arch_target,
                'install_path': extract_dir
            }
            
            # Set up as a service if required
            if package_info.get('is_service', False) and package_info.get('service_executable'):
                service_executable = os.path.join(extract_dir, package_info['service_executable'])
                service_args = package_info.get('service_args', [])
                
                if os.path.exists(service_executable):
                    config.setdefault('services', {})[package_name] = {
                        'executable': service_executable,
                        'args': service_args,
                        'pid_file': os.path.join(SERVICES_DIR, f"{package_name}.pid"),
                        'log_file': os.path.join(SERVICES_DIR, f"{package_name}.log"),
                        'status': 'stopped'
                    }
                    
                    if start_service:
                        save_config(config)  # Save before starting
                        start_result = start_service(package_name)
                        if start_result.get('status') == 'success':
                            logger.info(f"Service {package_name} started successfully")
                        else:
                            logger.warning(f"Failed to start service {package_name}: {start_result.get('message')}")
            
            save_config(config)
            return {"status": "success", "message": f"Package {package_name} version {version} for {os_target}-{arch_target} installed successfully."}
        except Exception as e:
            return {"status": "error", "message": f"Failed to install package {package_name}: {str(e)}"}
    except Exception as e:
        logger.error(f"Error installing package: {str(e)}")
        return {"status": "error", "message": f"Failed to install package {package_name}: {str(e)}"}

def uninstall_package(package_name: str) -> Dict[str, Any]:
    try:
        config = load_config()
        if package_name not in config['installed_packages']:
            return {"status": "error", "message": f"Package {package_name} is not installed."}

        try:
            # Stop service if running
            if package_name in config.get('services', {}):
                stop_result = stop_service(package_name)
                if stop_result.get('status') != 'success':
                    logger.warning(f"Failed to stop service {package_name}: {stop_result.get('message')}")
                # Remove service configuration
                del config['services'][package_name]
            
            package_info = config['installed_packages'][package_name]
            version = package_info['version']
            os_target = package_info['os']
            arch_target = package_info['architecture']
            package_dir = os.path.join(INSTALL_DIR, package_name)
            shutil.rmtree(package_dir)
            del config['installed_packages'][package_name]
            save_config(config)
            return {"status": "success", "message": f"Package {package_name} version {version} for {os_target}-{arch_target} uninstalled successfully."}
        except Exception as e:
            return {"status": "error", "message": f"Failed to uninstall package {package_name}: {str(e)}"}
    except Exception as e:
        logger.error(f"Error uninstalling package: {str(e)}")
        return {"status": "error", "message": f"Failed to uninstall package {package_name}: {str(e)}"}

def list_packages() -> Dict[str, Any]:
    try:
        config = load_config()
        if not config['installed_packages']:
            return {"status": "info", "message": "No packages installed.", "packages": {}}
        
        # Add service status information if available
        packages_info = config['installed_packages'].copy()
        for pkg_name, pkg_info in packages_info.items():
            if pkg_name in config.get('services', {}):
                pkg_info['is_service'] = True
                pkg_info['service_status'] = config['services'][pkg_name].get('status', 'unknown')
            else:
                pkg_info['is_service'] = False
        
        return {
            "status": "success", 
            "message": "Packages retrieved successfully", 
            "packages": packages_info
        }
    except Exception as e:
        logger.error(f"Error listing packages: {str(e)}")
        return {"status": "error", "message": f"Failed to list packages: {str(e)}"}

def find_latest_version(package_name: str, os_target: str, arch_target: str) -> str:
    versions = []
    for file in os.listdir(REPO_DIR):
        if file.startswith(f"{package_name}-") and file.endswith(f"-{os_target}-{arch_target}.bellande"):
            version = file.split('-')[1]
            if is_valid_version(version):
                versions.append(version)
    
    if not versions:
        raise ValueError(f"No versions found for package {package_name} on {os_target}-{arch_target}")
    
    return max(versions, key=lambda v: [int(x) for x in v.split('.')])

def update_package(package_name: str, version: str = None, os_target: str = None, arch_target: str = None) -> Dict[str, Any]:
    try:
        config = load_config()
        if package_name not in config['installed_packages']:
            return {"status": "error", "message": f"Package {package_name} is not installed."}

        current_info = config['installed_packages'][package_name]
        current_version = current_info['version']
        os_target = os_target or current_info['os']
        arch_target = arch_target or current_info['architecture']

        if version:
            if compare_versions(version, current_version) <= 0:
                return {"status": "info", "message": f"Specified version {version} is not newer than the installed version {current_version}."}
        else:
            try:
                version = find_latest_version(package_name, os_target, arch_target)
            except ValueError as e:
                return {"status": "error", "message": str(e)}

        if compare_versions(version, current_version) > 0:
            logger.info(f"Updating {package_name} from version {current_version} to {version}")
            return install_package(package_name, version, os_target, arch_target)
        else:
            return {"status": "info", "message": f"Package {package_name} is already up to date (version {current_version})"}
    except Exception as e:
        logger.error(f"Error updating package: {str(e)}")
        return {"status": "error", "message": f"Failed to update package {package_name}: {str(e)}"}

# Service management functions
def start_service(package_name: str) -> Dict[str, Any]:
    try:
        config = load_config()
        if package_name not in config.get('services', {}):
            return {"status": "error", "message": f"Package {package_name} is not registered as a service."}
        
        service_info = config['services'][package_name]
        executable = service_info['executable']
        args = service_info.get('args', [])
        pid_file = service_info['pid_file']
        log_file = service_info['log_file']
        
        if service_info.get('status') == 'running':
            try:
                with open(pid_file, 'r') as f:
                    pid = int(f.read().strip())
                try:
                    os.kill(pid, 0)  # Check if process is running
                    return {"status": "info", "message": f"Service {package_name} is already running with PID {pid}"}
                except OSError:
                    # Process not running but PID file exists
                    logger.warning(f"Service {package_name} marked as running but process {pid} not found")
            except (FileNotFoundError, ValueError):
                logger.warning(f"Service {package_name} marked as running but PID file not found or invalid")
        
        # Ensure service directory exists
        os.makedirs(os.path.dirname(pid_file), exist_ok=True)
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        # Start service in daemon mode
        try:
            with open(log_file, 'a') as log:
                with daemon.DaemonContext(
                    pidfile=pidfile.TimeoutPIDLockFile(pid_file),
                    stdout=log,
                    stderr=log,
                    working_directory=os.path.dirname(executable),
                    umask=0o002
                ):
                    subprocess.Popen([executable] + args)
            
            # Wait a moment to ensure process starts
            time.sleep(1)
            
            # Check if PID file was created
            if os.path.exists(pid_file):
                with open(pid_file, 'r') as f:
                    pid = f.read().strip()
                    
                # Update service status
                config['services'][package_name]['status'] = 'running'
                save_config(config)
                
                return {"status": "success", "message": f"Service {package_name} started with PID {pid}"}
            else:
                return {"status": "error", "message": f"Failed to start service {package_name}: PID file not created"}
        except Exception as e:
            return {"status": "error", "message": f"Failed to start service {package_name}: {str(e)}"}
    except Exception as e:
        logger.error(f"Error starting service {package_name}: {str(e)}")
        return {"status": "error", "message": f"Failed to start service {package_name}: {str(e)}"}

def stop_service(package_name: str) -> Dict[str, Any]:
    try:
        config = load_config()
        if package_name not in config.get('services', {}):
            return {"status": "error", "message": f"Package {package_name} is not registered as a service."}
        
        service_info = config['services'][package_name]
        pid_file = service_info['pid_file']
        
        if not os.path.exists(pid_file):
            config['services'][package_name]['status'] = 'stopped'
            save_config(config)
            return {"status": "info", "message": f"Service {package_name} is not running (no PID file)"}
        
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            try:
                os.kill(pid, signal.SIGTERM)
                logger.info(f"Sent SIGTERM to {package_name} process {pid}")
                
                # Wait for the process to terminate
                for _ in range(10):
                    time.sleep(0.5)
                    try:
                        os.kill(pid, 0)
                    except OSError:
                        # Process has terminated
                        if os.path.exists(pid_file):
                            os.unlink(pid_file)
                        config['services'][package_name]['status'] = 'stopped'
                        save_config(config)
                        return {"status": "success", "message": f"Service {package_name} stopped successfully"}
                
                # If we get here, the process didn't stop gracefully, use SIGKILL
                logger.warning(f"Service {package_name} did not stop gracefully, sending SIGKILL")
                os.kill(pid, signal.SIGKILL)
                time.sleep(0.5)
                
                if os.path.exists(pid_file):
                    os.unlink(pid_file)
                config['services'][package_name]['status'] = 'stopped'
                save_config(config)
                return {"status": "success", "message": f"Service {package_name} forcefully stopped"}
                
            except ProcessLookupError:
                logger.info(f"Service {package_name} process {pid} not found but PID file exists")
                if os.path.exists(pid_file):
                    os.unlink(pid_file)
                config['services'][package_name]['status'] = 'stopped'
                save_config(config)
                return {"status": "success", "message": f"Service {package_name} is not running (stale PID file removed)"}
                
        except Exception as e:
            return {"status": "error", "message": f"Failed to stop service {package_name}: {str(e)}"}
    except Exception as e:
        logger.error(f"Error stopping service {package_name}: {str(e)}")
        return {"status": "error", "message": f"Failed to stop service {package_name}: {str(e)}"}

def restart_service(package_name: str) -> Dict[str, Any]:
    stop_result = stop_service(package_name)
    if stop_result.get('status') not in ['success', 'info']:
        return stop_result
    
    # Wait a moment before restarting
    time.sleep(1)
    
    return start_service(package_name)

def service_status(package_name: str) -> Dict[str, Any]:
    try:
        config = load_config()
        if package_name not in config.get('services', {}):
            return {"status": "error", "message": f"Package {package_name} is not registered as a service."}
        
        service_info = config['services'][package_name]
        pid_file = service_info['pid_file']
        
        if not os.path.exists(pid_file):
            service_info['status'] = 'stopped'
            config['services'][package_name] = service_info
            save_config(config)
            return {"status": "info", "message": f"Service {package_name} is stopped", "service_status": "stopped"}
        
        try:
            with open(pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            try:
                os.kill(pid, 0)  # Check if process is running
                service_info['status'] = 'running'
                config['services'][package_name] = service_info
                save_config(config)
                return {
                    "status": "success", 
                    "message": f"Service {package_name} is running with PID {pid}", 
                    "service_status": "running",
                    "pid": pid
                }
            except OSError:
                # Process not running but PID file exists
                if os.path.exists(pid_file):
                    os.unlink(pid_file)
                service_info['status'] = 'stopped'
                config['services'][package_name] = service_info
                save_config(config)
                return {
                    "status": "info", 
                    "message": f"Service {package_name} is not running (stale PID file removed)", 
                    "service_status": "stopped"
                }
        except Exception as e:
            return {"status": "error", "message": f"Failed to get status of service {package_name}: {str(e)}"}
    except Exception as e:
        logger.error(f"Error getting service status for {package_name}: {str(e)}")
        return {"status": "error", "message": f"Failed to get status of service {package_name}: {str(e)}"}

def list_services() -> Dict[str, Any]:
    try:
        config = load_config()
        services = config.get('services', {})
        
        if not services:
            return {"status": "info", "message": "No services configured.", "services": {}}
        
        # Update and verify status of all services
        for service_name, service_info in services.items():
            status_result = service_status(service_name)
            services[service_name]['status'] = status_result.get('service_status', 'unknown')
        
        return {
            "status": "success", 
            "message": "Services retrieved successfully", 
            "services": services
        }
    except Exception as e:
        logger.error(f"Error listing services: {str(e)}")
        return {"status": "error", "message": f"Failed to list services: {str(e)}"}

# Socket server for handling client requests
class BOSPMServiceHandler(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            data = self.rfile.readline().strip().decode('utf-8')
            request = json.loads(data)
            
            command = request.get('command')
            logger.info(f"Received command: {command}")
            
            response = self.process_command(command, request)
            
            self.wfile.write((json.dumps(response) + '\n').encode('utf-8'))
        except Exception as e:
            logger.error(f"Error handling request: {str(e)}")
            self.wfile.write((json.dumps({
                "status": "error",
                "message": f"Server error: {str(e)}"
            }) + '\n').encode('utf-8'))
    
    def process_command(self, command, request):
        if command == 'create':
            return create_package(
                request.get('package_name'),
                request.get('version'),
                request.get('files', []),
                request.get('os_target'),
                request.get('arch_target'),
                request.get('is_service', False),
                request.get('service_executable'),
                request.get('service_args')
            )
        elif command == 'install':
            return install_package(
                request.get('package_name'),
                request.get('version'),
                request.get('os_target'),
                request.get('arch_target'),
                request.get('start_service', True)
            )
        elif command == 'uninstall':
            return uninstall_package(request.get('package_name'))
        elif command == 'list':
            return list_packages()
        elif command == 'update':
            return update_package(
                request.get('package_name'),
                request.get('version'),
                request.get('os_target'),
                request.get('arch_target')
            )
        elif command == 'start_service':
            return start_service(request.get('package_name'))
        elif command == 'stop_service':
            return stop_service(request.get('package_name'))
        elif command == 'restart_service':
            return restart_service(request.get('package_name'))
        elif command == 'service_status':
            return service_status(request.get('package_name'))
        elif command == 'list_services':
            return list_services()
        elif command == 'ping':
            return {"status": "success", "message": "pong"}
        else:
            return {"status": "error", "message": f"Unknown command: {command}"}

class ThreadedUnixStreamServer(socketserver.ThreadingMixIn, socketserver.UnixStreamServer):
    daemon_threads = True

def run_service():
    ensure_dirs()
    logger.info("Starting BOSPM service")
    
    # Remove socket file if it already exists
    if os.path.exists(SOCKET_FILE):
        os.unlink(SOCKET_FILE)
    
    # Create server
    try:
        server = ThreadedUnixStreamServer(SOCKET_FILE, BOSPMServiceHandler)
        os.chmod(SOCKET_FILE, 0o666)  # Make socket accessible to all users
        
        # Set up signal handlers
        def signal_handler(sig, frame):
            logger.info(f"Received signal {sig}, shutting down")
            server.shutdown()
            os.unlink(SOCKET_FILE)
            sys.exit(0)
        
        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)
        
        # Start server thread
        server_thread = threading.Thread(target=server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        logger.info(f"BOSPM service running on {SOCKET_FILE}")
        
        # Keep alive
        while True:
            time.sleep(60)
            
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        if os.path.exists(SOCKET_FILE):
            os.unlink(SOCKET_FILE)
        sys.exit(1)

# Client class for communicating with the service
class BOSPMClient:
    def __init__(self, socket_file=SOCKET_FILE):
        self.socket_file = socket_file
    
    def send_command(self, command_dict):
        import socket
        client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            client.connect(self.socket_file)
            client.sendall((json.dumps(command_dict) + '\n').encode('utf-8'))
            
            response = client.recv(4096).decode('utf-8')
            return json.loads(response)
        except ConnectionRefusedError:
            return {"status": "error", "message": "Service not running"}
        finally:
            client.close()
    
    def ping(self):
        return self.send_command({"command": "ping"})
    
    def create_package(self, package_name, version, files, os_target=None, arch_target=None):
        return self.send_command({
            "command": "create",
            "package_name": package_name,
            "version": version,
            "files": files,
            "os_target": os_target,
            "arch_target": arch_target
        })
    
    def install_package(self, package_name, version, os_target=None, arch_target=None):
        return self.send_command({
            "command": "install",
            "package_name": package_name,
            "version": version,
            "os_target": os_target,
            "arch_target": arch_target
        })
    
    def uninstall_package(self, package_name):
        return self.send_command({
            "command": "uninstall",
            "package_name": package_name
        })
    
    def list_packages(self):
        return self.send_command({"command": "list"})
    
    def update_package(self, package_name, version=None, os_target=None, arch_target=None):
        return self.send_command({
            "command": "update",
            "package_name": package_name,
            "version": version,
            "os_target": os_target,
            "arch_target": arch_target
        })

# Main function to handle service operations
def main():
    parser = argparse.ArgumentParser(description='Bellande Operating System Package Manager Service')
    subparsers = parser.add_subparsers(dest='action', help='Action to perform')
    
    # Start command
    start_parser = subparsers.add_parser('start', help='Start the BOSPM service')
    start_parser.add_argument('--foreground', action='store_true', help='Run in foreground (no daemon)')
    
    # Stop command
    subparsers.add_parser('stop', help='Stop the BOSPM service')
    
    # Status command
    subparsers.add_parser('status', help='Check the status of the BOSPM service')
    
    # Client commands
    client_parser = subparsers.add_parser('client', help='Client operations')
    client_subparsers = client_parser.add_subparsers(dest='client_action', help='Client action to perform')
    
    # Create package
    create_parser = client_subparsers.add_parser('create', help='Create a new package')
    create_parser.add_argument('package_name', help='Name of the package')
    create_parser.add_argument('version', help='Version of the package')
    create_parser.add_argument('files', nargs='+', help='Files to include in the package')
    create_parser.add_argument('--os', dest='os_target', help='Target OS')
    create_parser.add_argument('--arch', dest='arch_target', help='Target architecture')
    
    # Install package
    install_parser = client_subparsers.add_parser('install', help='Install a package')
    install_parser.add_argument('package_name', help='Name of the package')
    install_parser.add_argument('version', help='Version of the package')
    install_parser.add_argument('--os', dest='os_target', help='Target OS')
    install_parser.add_argument('--arch', dest='arch_target', help='Target architecture')
    
    # Uninstall package
    uninstall_parser = client_subparsers.add_parser('uninstall', help='Uninstall a package')
    uninstall_parser.add_argument('package_name', help='Name of the package')
    
    # List packages
    client_subparsers.add_parser('list', help='List installed packages')
    
    # Update package
    update_parser = client_subparsers.add_parser('update', help='Update a package')
    update_parser.add_argument('package_name', help='Name of the package')
    update_parser.add_argument('version', nargs='?', help='Version to update to (optional)')
    update_parser.add_argument('--os', dest='os_target', help='Target OS')
    update_parser.add_argument('--arch', dest='arch_target', help='Target architecture')
    
    args = parser.parse_args()
    
    if args.action == 'start':
        if os.path.exists(PID_FILE):
            with open(PID_FILE, 'r') as f:
                pid = f.read().strip()
            try:
                os.kill(int(pid), 0)
                print(f"Service is already running with PID {pid}")
                return
            except OSError:
                # PID file exists but process is not running
                os.unlink(PID_FILE)
        
        if args.foreground:
            # Run in foreground
            ensure_dirs()
            run_service()
        else:
            # Run as daemon
            ensure_dirs()
            with daemon.DaemonContext(
                pidfile=pidfile.TimeoutPIDLockFile(PID_FILE),
                umask=0o002,
                signal_map={
                    signal.SIGTERM: lambda signum, frame: sys.exit(0),
                    signal.SIGINT: lambda signum, frame: sys.exit(0)
                }
            ):
                run_service()
    
    elif args.action == 'stop':
        if os.path.exists(PID_FILE):
            with open(PID_FILE, 'r') as f:
                pid = f.read().strip()
            try:
                os.kill(int(pid), signal.SIGTERM)
                print(f"Sent SIGTERM to process {pid}")
                # Wait for the process to terminate
                for _ in range(10):
                    time.sleep(0.5)
                    try:
                        os.kill(int(pid), 0)
                    except OSError:
                        print("Service stopped")
                        if os.path.exists(PID_FILE):
                            os.unlink(PID_FILE)
                        return
                print("Warning: Service did not stop gracefully, sending SIGKILL")
                os.kill(int(pid), signal.SIGKILL)
            except ProcessLookupError:
                print("Service not running but PID file exists")
                os.unlink(PID_FILE)
            except Exception as e:
                print(f"Error stopping service: {str(e)}")
        else:
            print("Service not running (no PID file)")
    
    elif args.action == 'status':
        if os.path.exists(PID_FILE):
            with open(PID_FILE, 'r') as f:
                pid = f.read().strip()
            try:
                os.kill(int(pid), 0)
                print(f"Service is running with PID {pid}")
                
                # Try to ping the service
                client = BOSPMClient()
                response = client.ping()
                if response.get('status') == 'success':
                    print("Service is responding to commands")
                else:
                    print(f"Service is not responding: {response.get('message', 'Unknown error')}")
            except OSError:
                print("Service not running but PID file exists")
        else:
            print("Service not running (no PID file)")
    
    elif args.action == 'client':
        client = BOSPMClient()
        
        if args.client_action == 'create':
            response = client.create_package(
                args.package_name,
                args.version,
                args.files,
                args.os_target,
                args.arch_target
            )
            print(response.get('message'))
        
        elif args.client_action == 'install':
            response = client.install_package(
                args.package_name,
                args.version,
                args.os_target,
                args.arch_target
            )
            print(response.get('message'))
        
        elif args.client_action == 'uninstall':
            response = client.uninstall_package(args.package_name)
            print(response.get('message'))
        
        elif args.client_action == 'list':
            response = client.list_packages()
            if response.get('status') == 'success':
                packages = response.get('packages', {})
                if not packages:
                    print("No packages installed")
                else:
                    print("Installed packages:")
                    for package, info in packages.items():
                        print(f"- {package} (version {info['version']}, {info['os']}-{info['architecture']})")
            else:
                print(response.get('message'))
        
        elif args.client_action == 'update':
            response = client.update_package(
                args.package_name,
                args.version,
                args.os_target,
                args.arch_target
            )
            print(response.get('message'))
        
        else:
            print("No client action specified")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
