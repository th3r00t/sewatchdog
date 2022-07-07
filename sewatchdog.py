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
import sys
import signal
import subprocess
import time
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
        print("Please adjust sewatchdog.ini accordingly")
        sys.exit()
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
        self.instance_path = path
        self.server_path = self.instance_path+'../'
        self.pid = self.getpid(self.instance_path)
        self.last_stamp = None
        self.getcanary()

    def watchdog(self):
            _watcher = True
            while _watcher:
                last_stamp = self.last_stamp
                time.sleep(20)
                self.getcanary()
                if last_stamp is None:
                    print('Waiting for Game Ready')
                    time.sleep(10)
                elif self.last_stamp - last_stamp != 0:
                    print(r'{} pulse rcvd {}'.format(self.last_stamp - last_stamp, time.time()))
                else:
                    print(self.last_stamp - last_stamp)
                    print(r'Killing Server {}'.format(time.time()))
                    self.die()
                    time.sleep(5)
                    self.spawn()

    def die(self):
        print('Killing Server')
        os.system("taskkill /f /im Testing.Server.exe")
        self.pid = None
        self.last_stamp = None

    def spawn(self):
        print("Launching Server")
        _server_path = Path(self.server_path, 'Testing.Server.exe').__str__()
        subprocess.Popen(_server_path, close_fds=True, creationflags=subprocess.DETACHED_PROCESS)

    def __str__(self):
        return self.name

    def getcanary(self):
        try:
            _fp = self.instance_path.replace('"', '')+'canary'
            self.last_stamp = os.stat(_fp).st_mtime
            with open(_fp, 'r') as _canary:
                pulse = _canary.readline()
                _canary.close()
            return pulse
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
    print("Goodbye")