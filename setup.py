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

from setuptools import setup, find_packages
from setuptools.command.install import install
import os
import sys
import shutil

def post_install():
    # Determine the appropriate installation directory
    if sys.platform.startswith('win'):
        install_dir = os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files'), 'bospm')
        script_dir = os.path.join(install_dir, 'Scripts')
        os.makedirs(script_dir, exist_ok=True)
        bat_path = os.path.join(script_dir, 'bospm.bat')
        with open(bat_path, 'w') as f:
            f.write('@echo off\n')
            f.write(f'python "{os.path.join(install_dir, "bospm.py")}" %*')
    else:  # Unix-like systems (BellandeOS, Linux, macOS)
        install_dir = '/usr/local/bospm'
        bin_dir = '/usr/local/bin'
        os.makedirs(install_dir, exist_ok=True)
        os.makedirs(bin_dir, exist_ok=True)
        script_path = os.path.join(bin_dir, 'bospm')
        with open(script_path, 'w') as f:
            f.write('#!/bin/bash\n')
            f.write(f'python3 "{os.path.join(install_dir, "bospm.py")}" "$@"')
        os.chmod(script_path, 0o755)

    # Copy the bospm.py script to the installation directory
    src_path = os.path.join('src', 'bospm', 'bospm.py')
    shutil.copy(src_path, install_dir)
    print(f"bospm has been installed to {install_dir}")
    if sys.platform.startswith('win'):
        print("Please add the following directory to your PATH:")
        print(script_dir)
    else:
        print("You can now use 'bospm' from anywhere in the terminal.")

class PostInstallCommand(install):
    def run(self):
        install.run(self)
        post_install()

# Read long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="bospm",
    version="0.1.1",
    description="Bellande Operating System Package Manager",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ronaldson Bellande",
    author_email="ronaldsonbellande@gmail.com",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    include_package_data=True,
    install_requires=[
        "requests>=2.25.1",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=2.7",
    extras_require={
        "dev": ["pytest", "pytest-cov[all]", "mypy", "black"],
    },
    entry_points={
        'console_scripts': [
            'bospm = bospm.bospm:main',
        ],
    },
    project_urls={
        "Home": "https://github.com/Architecture-Mechanism/bellande_operating_system_package_manager",
        "Bug Reports": "https://github.com/Architecture-Mechanism/bellande_operating_system_package_manager/issues",
        "Source": "https://github.com/Architecture-Mechanism/bellande_operating_system_package_manager",
    },
    cmdclass={
        'install': PostInstallCommand,
    },
    license="GNU General Public License v3 or later (GPLv3+)",
    platforms=["any"],
)
