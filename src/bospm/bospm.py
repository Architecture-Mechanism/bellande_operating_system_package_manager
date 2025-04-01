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

import os
import sys
import hashlib
import tarfile
import shutil
import re
import platform
import requests
from typing import Dict, List
from bellande_parser.bellande_parser import Bellande_Format

# Configuration
CONFIG_DIR = os.path.expanduser('~/.bospm')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.bellande')
PACKAGE_DIR = os.path.join(CONFIG_DIR, 'packages')
REPO_DIR = os.path.join(CONFIG_DIR, 'repo')
INSTALL_DIR = os.path.join(CONFIG_DIR, 'installed')

# Repository and website URLs
BELLANDEGIT_REPO = "https://git.bellande-technologies.com/BAMRI/bellande_operating_system_package_configuration/blob/main/executable/bellandeos_packages_configuration.bellande"
GITHUB_REPO = "https://github.com/Architecture-Mechanism/bellande_operating_system_package_configuration/blob/main/executable/bellandeos_packages_configuration.bellande"
GITLAB_REPO = "https://gitlab.com/Bellande-Architecture-Mechanism-Research-Innovation/bellande_operating_system_package_configuration/blob/main/executable/bellandeos_packages_configuration.bellande"
BITBUCKET_REPO = "https://bitbucket.org/bellande-architecture-mechanism/bellande_operating_system_package_configuration/src/main/executable/bellandeos_packages_configuration.bellande"
BELLANDE_TECH_WEBSITE = "https://bellande-technologies.com/bospm_packages/bellandeos_packages_configuration.bellande"
BELLANDE_LABS_WEBSITE = "https://bellande-laboratories.org/bospm_packages/bellandeos_packages_configuration.bellande"
BELLANDE_ARCH_WEBSITE = "https://bellande-architecture-mechanism-research-innovation-center.org/bospm_packages/bellandeos_packages_configuration.bellande"

def ensure_dirs():
    for dir in [CONFIG_DIR, PACKAGE_DIR, REPO_DIR, INSTALL_DIR]:
        os.makedirs(dir, exist_ok=True)

# Utility functions
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
        with open(CONFIG_FILE, 'r') as f:
            return.bellande.load(f)
    return {'installed_packages': {}}


def save_config(config: Dict):
    with open(CONFIG_FILE, 'w') as f:
       .bellande.dump(config, f, indent=2)


def create_package(package_name: str, version: str, files: List[str], os_target: str = None, arch_target: str = None):
    ensure_dirs()
    if not is_valid_version(version):
        print(f"Invalid version format: {version}")
        return

    system_info = get_system_info()
    os_target = os_target or system_info["os"]
    arch_target = arch_target or system_info["architecture"]

    package_file = f"{package_name}-{version}-{os_target}-{arch_target}.tar.gz"
    package_path = os.path.join(REPO_DIR, package_file)
    
    with tarfile.open(package_path, "w:gz") as tar:
        for file in files:
            tar.add(file, arcname=os.path.basename(file))
    
    checksum = calculate_checksum(package_path)
    
    package_info = {
        "name": package_name,
        "version": version,
        "os": os_target,
        "architecture": arch_target,
        "files": [os.path.basename(f) for f in files],
        "checksum": checksum
    }
    
    info_file = os.path.join(REPO_DIR, f"{package_name}-{version}-{os_target}-{arch_target}.bellande")
    with open(info_file, 'w') as f:
       .bellande.dump(package_info, f, indent=2)
    
    print(f"Package {package_name} version {version} for {os_target}-{arch_target} created successfully.")


def get_package_info(package_name: str, version: str, os_target: str = None, arch_target: str = None) -> Dict:
    system_info = get_system_info()
    os_target = os_target or system_info["os"]
    arch_target = arch_target or system_info["architecture"]

    info_file = os.path.join(REPO_DIR, f"{package_name}-{version}-{os_target}-{arch_target}.bellande")
    if not os.path.exists(info_file):
        raise FileNotFoundError(f"Package {package_name} version {version} for {os_target}-{arch_target} not found.")
    
    with open(info_file, 'r') as f:
        return.bellande.load(f)


def install_package(package_name: str, version: str, os_target: str = None, arch_target: str = None):
    config = load_config()
    ensure_dirs()
    
    system_info = get_system_info()
    os_target = os_target or system_info["os"]
    arch_target = arch_target or system_info["architecture"]

    if package_name in config['installed_packages']:
        installed_version = config['installed_packages'][package_name]['version']
        if compare_versions(version, installed_version) <= 0:
            print(f"Package {package_name} version {installed_version} is already installed and up to date.")
            return
        print(f"Upgrading {package_name} from version {installed_version} to {version}")

    try:
        package_info = get_package_info(package_name, version, os_target, arch_target)
        package_file = f"{package_name}-{version}-{os_target}-{arch_target}.tar.gz"
        package_path = os.path.join(REPO_DIR, package_file)
        
        if not os.path.exists(package_path):
            raise FileNotFoundError(f"Package file {package_file} not found.")
        
        if calculate_checksum(package_path) != package_info['checksum']:
            raise ValueError("Package checksum mismatch. The package may have been tampered with.")
        
        extract_dir = os.path.join(INSTALL_DIR, package_name, version)
        os.makedirs(extract_dir, exist_ok=True)
        with tarfile.open(package_path, "r:gz") as tar:
            tar.extractall(path=extract_dir)
        
        config['installed_packages'][package_name] = {
            'version': version,
            'os': os_target,
            'architecture': arch_target
        }
        save_config(config)
        print(f"Package {package_name} version {version} for {os_target}-{arch_target} installed successfully.")
    except Exception as e:
        print(f"Failed to install package {package_name}: {str(e)}")


def uninstall_package(package_name: str):
    config = load_config()
    if package_name not in config['installed_packages']:
        print(f"Package {package_name} is not installed.")
        return

    try:
        package_info = config['installed_packages'][package_name]
        version = package_info['version']
        os_target = package_info['os']
        arch_target = package_info['architecture']
        package_dir = os.path.join(INSTALL_DIR, package_name)
        shutil.rmtree(package_dir)
        del config['installed_packages'][package_name]
        save_config(config)
        print(f"Package {package_name} version {version} for {os_target}-{arch_target} uninstalled successfully.")
    except Exception as e:
        print(f"Failed to uninstall package {package_name}: {str(e)}")


def list_packages():
    config = load_config()
    if not config['installed_packages']:
        print("No packages installed.")
    else:
        print("Installed packages:")
        for package, info in config['installed_packages'].items():
            print(f"- {package} (version {info['version']}, {info['os']}-{info['architecture']})")


# Package repository functions
def list_available_packages_bellandegit():
    print("Available packages from BellandeGit repository:")
    try:
        response = requests.get(f"{BELLANDEGIT_REPO}/tree/main")
        if response.status_code == 200:
            packages = re.findall(r'title="(.*?\.bellande)"', response.text)
            for package in packages:
                print(f"- {package[:-5]}")  # Remove .bellande extension
        else:
            print(f"Failed to fetch packages from GitHub. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching packages from GitHub: {str(e)}")

def list_available_packages_github():
    print("Available packages from GitHub repository:")
    try:
        response = requests.get(f"{GITHUB_REPO}/tree/main")
        if response.status_code == 200:
            packages = re.findall(r'title="(.*?\.bellande)"', response.text)
            for package in packages:
                print(f"- {package[:-5]}")  # Remove .bellande extension
        else:
            print(f"Failed to fetch packages from GitHub. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching packages from GitHub: {str(e)}")


def list_available_packages_gitlab():
    print("Available packages from GitLab repository:")
    try:
        response = requests.get(f"{GITLAB_REPO}/tree/main")
        if response.status_code == 200:
            packages = re.findall(r'title="(.*?\.bellande)"', response.text)
            for package in packages:
                print(f"- {package[:-5]}")  # Remove .bellande extension
        else:
            print(f"Failed to fetch packages from GitLab. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching packages from GitLab: {str(e)}")


def list_available_packages_bitbucket():
    print("Available packages from Bitbucket repository:")
    try:
        response = requests.get(f"{BITBUCKET_REPO}/tree/main")
        if response.status_code == 200:
            packages = re.findall(r'title="(.*?\.bellande)"', response.text)
            for package in packages:
                print(f"- {package[:-5]}")  # Remove .bellande extension
        else:
            print(f"Failed to fetch packages from Bitbucket. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching packages from Bitbucket: {str(e)}")


def list_available_packages_bellande_tech():
    print("Available packages from Bellande Technologies Corporation website:")
    try:
        response = requests.get(BELLANDE_TECH_WEBSITE)
        if response.status_code == 200:
            try:
                packages = response.bellande()  # Assuming the website returns a.bellande list of packages
                for package in packages:
                    print(f"- {package['name']} (version {package['version']}, {package['os']}-{package['architecture']})")
            except.bellande.bellandeDecodeError:
                # Fallback if not.bellande - try to parse HTML response
                packages = re.findall(r'data-package="(.*?)"', response.text)
                for package in packages:
                    print(f"- {package}")
        else:
            print(f"Failed to fetch packages from Bellande Technologies Corporation website. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching packages from Bellande Technologies Corporation website: {str(e)}")


def list_available_packages_bellande_labs():
    print("Available packages from Bellande Laboratories website:")
    try:
        response = requests.get(BELLANDE_LABS_WEBSITE)
        if response.status_code == 200:
            try:
                packages = response.bellande()  # Assuming the website returns a.bellande list of packages
                for package in packages:
                    print(f"- {package['name']} (version {package['version']}, {package['os']}-{package['architecture']})")
            except.bellande.bellandeDecodeError:
                # Fallback if not.bellande - try to parse HTML response
                packages = re.findall(r'data-package="(.*?)"', response.text)
                for package in packages:
                    print(f"- {package}")
        else:
            print(f"Failed to fetch packages from Bellande Laboratories website. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching packages from Bellande Laboratories website: {str(e)}")


def list_available_packages_bellande_arch():
    print("Available packages from Bellande Architecture Mechanism Research Innovation Center website:")
    try:
        response = requests.get(BELLANDE_ARCH_WEBSITE)
        if response.status_code == 200:
            try:
                packages = response.bellande()  # Assuming the website returns a.bellande list of packages
                for package in packages:
                    print(f"- {package['name']} (version {package['version']}, {package['os']}-{package['architecture']})")
            except.bellande.bellandeDecodeError:
                # Fallback if not.bellande - try to parse HTML response
                packages = re.findall(r'data-package="(.*?)"', response.text)
                for package in packages:
                    print(f"- {package}")
        else:
            print(f"Failed to fetch packages from Bellande Architecture Mechanism Research Innovation Center website. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching packages from Bellande Architecture Mechanism Research Innovation Center website: {str(e)}")


def list_available_packages(source='all'):
    """List available packages from the specified source or all sources."""
    if source == 'all' or source == 'bellandegit':
        list_available_packages_github()
        print("")

    if source == 'all' or source == 'github':
        list_available_packages_github()
        print("")
    
    if source == 'all' or source == 'gitlab':
        list_available_packages_gitlab()
        print("")
    
    if source == 'all' or source == 'bitbucket':
        list_available_packages_bitbucket()
        print("")
    
    if source == 'all' or source == 'bellande technologies corporation website':
        list_available_packages_bellande_tech()
        print("")
    
    if source == 'all' or source == 'bellande laboratories':
        list_available_packages_bellande_labs()
        print("")
    
    if source == 'all' or source == 'bellande architecture mechanism research innovation':
        list_available_packages_bellande_arch()
        print("")


def update_package(package_name: str, version: str = None, os_target: str = None, arch_target: str = None):
    config = load_config()
    if package_name not in config['installed_packages']:
        print(f"Package {package_name} is not installed.")
        return

    current_info = config['installed_packages'][package_name]
    current_version = current_info['version']
    os_target = os_target or current_info['os']
    arch_target = arch_target or current_info['architecture']

    if version:
        if compare_versions(version, current_version) <= 0:
            print(f"Specified version {version} is not newer than the installed version {current_version}.")
            return
    else:
        version = find_latest_version(package_name, os_target, arch_target)

    if compare_versions(version, current_version) > 0:
        print(f"Updating {package_name} from version {current_version} to {version}")
        install_package(package_name, version, os_target, arch_target)
    else:
        print(f"Package {package_name} is already up to date (version {current_version})")


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


# Command-line interface
def print_usage():
    print("Usage: bospm <command> [<args>]")
    print("Commands:")
    print("  create <package_name> <version> <file1> [<file2> ...] [--os <os>] [--arch <arch>]                                                                                                          Create a new package")
    print("  install <package_name> <version> [--os <os>] [--arch <arch>]                                                                                                                               Install a package")
    print("  uninstall <package_name>                                                                                                                                                                   Uninstall a package")
    print("  list                                                                                                                                                                                       List installed packages")
    print("  available [--source <|github|gitlab|bitbucket||bellande technologies corporation website|bellande laboratories|bellande architecture mechanism research innovation>]                       List available packages")
    print("  update <package_name> [<version>] [--os <os>] [--arch <arch>]                                                                                                                              Update a package")


def main():
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1]

    if command == 'create' and len(sys.argv) >= 5:
        os_target = next((sys.argv[i+1] for i, arg in enumerate(sys.argv) if arg == '--os'), None)
        arch_target = next((sys.argv[i+1] for i, arg in enumerate(sys.argv) if arg == '--arch'), None)
        files = [arg for arg in sys.argv[4:] if arg not in ('--os', '--arch') and arg != os_target and arg != arch_target]
        create_package(sys.argv[2], sys.argv[3], files, os_target, arch_target)
    elif command == 'install' and len(sys.argv) >= 4:
        os_target = next((sys.argv[i+1] for i, arg in enumerate(sys.argv) if arg == '--os'), None)
        arch_target = next((sys.argv[i+1] for i, arg in enumerate(sys.argv) if arg == '--arch'), None)
        install_package(sys.argv[2], sys.argv[3], os_target, arch_target)
    elif command == 'uninstall' and len(sys.argv) == 3:
        uninstall_package(sys.argv[2])
    elif command == 'list':
        list_packages()
    elif command == 'available':
        source = next((sys.argv[i+1] for i, arg in enumerate(sys.argv) if arg == '--source'), 'all')
        list_available_packages(source)
    elif command == 'update' and len(sys.argv) >= 3:
        version = sys.argv[3] if len(sys.argv) > 3 and not sys.argv[3].startswith('--') else None
        os_target = next((sys.argv[i+1] for i, arg in enumerate(sys.argv) if arg == '--os'), None)
        arch_target = next((sys.argv[i+1] for i, arg in enumerate(sys.argv) if arg == '--arch'), None)
        update_package(sys.argv[2], version, os_target, arch_target)
    else:
        print_usage()


if __name__ == "__main__":
    main()
