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

from distutils.core import setup
import os
import sys

this_directory = os.path.abspath(os.path.dirname(__file__))

def read_file(filename):
    with open(os.path.join(this_directory, filename), 'r', encoding='utf-8') as f:
        return f.read()

long_description = read_file('README.md')

# Determine the list of classifiers based on Python version
if sys.version_info[0] == 2:
    python_classifiers = [
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
    ]
else:
    python_classifiers = [
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ]

setup(
    name="bospm",
    version="0.1.0",
    author="Ronaldson Bellande",
    author_email="ronaldsonbellande@gmail.com",
    description="Bellande Operating System Package Manager",
    long_description=long_description,
    url="https://github.com/Algorithm-Model-Research/bellande_operating_system_package_manager",
    packages=['bospm'],
    package_dir={'bospm': 'src/bospm'},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ] + python_classifiers,
    requires=["requests (>=2.25.1)"],
    scripts=['src/bospm/bospm.py'],
    license="GNU General Public License v3 or later (GPLv3+)",
    platforms=["any"],
)
