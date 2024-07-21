# Bellande Operating System Package Manager (BOSPM)
- BOSPM Stands for Bellande Operating System Package Manager

## BOSPM
[![Bellande's Package](https://img.shields.io/badge/Bellande's%20Package-BOSPM-blue?style=for-the-badge&logo=python&color=blue)](https://pypi.org/project/bospm)

## BellandeOS
- BOSPM is a cross-platform package manager built entirely in Python. It works on Windows, macOS, Linux, and BellandeOS without relying on any external package managers

## Repository

The BOSPM project is hosted on GitHub: [https://github.com/Algorithm-Model-Research/bellande_operating_system_package_manager](https://github.com/Algorithm-Model-Research/bellande_operating_system_package_manager)


## BOSPM Terminal Commands Usage
After installation, you can use bospm commands directly from the terminal:

- bospm create <package_name> <version> <file1> [<file2> ...] [--os <os>] [--arch <arch>]  Create a new package
- bospm install <package_name> <version> [--os <os>] [--arch <arch>]                       Install a package
- bospm uninstall <package_name>                                                           Uninstall a package
- bospm list                                                                               List installed packages
- bospm available [--source <github|website>]                                              List available packages
- bospm update <package_name> [<version>] [--os <os>] [--arch <arch>]                      Update a package

### Installation
- `$ pip install bospm`

### Upgrade (if not upgraded)
- `$ pip install --upgrade bospm`

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.
