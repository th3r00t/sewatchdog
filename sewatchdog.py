# Space Engineers Watchdog 
# Copyright (C) 2022  Raelon "th3r00t" Masters
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from pathlib import PureWindowsPath, Path
import configparser
import asyncio
import os
from unicodedata import name

config = {}
instances = {}

def mkconfig():
    try:
        _fparser = configparser.ConfigParser()
        _fparser["instances"] = {
            "servername": "/path/to/server"
        }
        with open (r'./sewatchdog.ini', 'w') as _cfile:
            _fparser.write(_cfile)
            _cfile.flush()
            _cfile.close()
        return True
    except Exception as e:
        print(e)
        return False

def getconfig():
    if not Path("./sewatchdog.ini").is_file():
        if not mkconfig():
            print("Error during config file generation")
            return False
    try:
        _instances = {}
        _fparser = configparser.ConfigParser()
        _fparser.read('./sewatchdog.ini')
        for instance in _fparser["instances"]:
            _instances[instance] = _fparser["instances"][instance]
        return _instances
    except Exception as e:
        print(e)
        return False


class Server:
    def __init__(self, name, path):
        self.name = name
        self.path = path
        self.pid = self.getpid(self.path)
        self.last_stamp = None
        self.getcanary()

    async def watchdog(self):
        while True:
            last_stamp = self.last_stamp
            await asyncio.sleep(10)
            self.getcanary()
            print(self.last_stamp - last_stamp)

    def __str__(self):
        return self.name

    def getcanary(self):
        try:
            _fp = self.path.replace('"', '')+'canary'
            self.last_stamp = os.stat(_fp).st_mtime
            with open(_fp, 'r') as _canary:
                return _canary.readline()
        except Exception as e:
            print(e)
            return False

    def getpid(self, server):
        try:
            _fp = server.replace('"', '')+'pid'
            with open(_fp, 'r') as _pid:
                return _pid.readline()
        except FileNotFoundError as e:
            print(e)
            return False

async def main():
    global instances, config
    config = getconfig()
    for server in config:
        try:
            instances[server]
        except KeyError:
            instances[server] = Server(server, config[server])
            await instances[server].watchdog()
            await asyncio.sleep(.2)
    await asyncio.sleep(.2)

if __name__ == "__main__":
    asyncio.run(main())