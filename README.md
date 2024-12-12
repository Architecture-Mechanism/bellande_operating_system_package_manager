# Bellande Operating System Package Manager (BOSPM)
- BOSPM Stands for Bellande Operating System Package Manager

## Install pip with sudo or bell
- `sudo pip install bospm`
- `bell pip install bospm`

## BOSPM
[![Bellande's Package](https://img.shields.io/badge/Bellande's%20Package-BOSPM-blue?style=for-the-badge&logo=python&color=blue)](https://pypi.org/project/bospm)

## BellandeOS
- BOSPM is a cross-platform package manager built entirely in Python. It works on Windows, macOS, Linux, and BellandeOS without relying on any external package managers

## Repository
**The BOSPM project is hosted on Bellande Technologies Git and Github**
- The BOSPM project hosted on Bellande Technologies Git: [https://git.bellande-technologies.com/BAMRI/bellande_operating_system_package_manager](https://git.bellande-technologies.com/BAMRI/bellande_operating_system_package_manager)
- The BOSPM project hosted on GitHub: [https://github.com/Architecture-Mechanism/bellande_operating_system_package_manager](https://github.com/Architecture-Mechanism/bellande_operating_system_package_manager)


## BOSPM Terminal Commands Usage
After installation, you can use bospm commands directly from the terminal:

- bospm create <package_name> <version> <file1> [<file2> ...] [--os <os>] [--arch <arch>]  Create a new package
- bospm install <package_name> <version> [--os <os>] [--arch <arch>]                       Install a package
- bospm uninstall <package_name>                                                           Uninstall a package
- bospm list                                                                               List installed packages
- bospm available [--source <github|website>]                                              List available packages
- bospm update <package_name> [<version>] [--os <os>] [--arch <arch>]                      Update a package

### Upgrade (if not upgraded)
- `$ pip install --upgrade bospm`

## Contributing
Contributions are welcome! Please feel free to submit a Pull Request.

## License
(BOSPM) Bellande Operating System Package Manager is distributed under the [GNU General Public License v3.0](https://www.gnu.org/licenses/gpl-3.0.en.html), see [LICENSE](https://github.com/Architecture-Mechanism/bellande_operating_system_package_manager/blob/main/LICENSE) and [NOTICE](https://github.com/Architecture-Mechanism/bellande_operating_system_package_manager/blob/main/LICENSE) for more information.
