# -*- coding: utf-8 -*-
# <HackLab - Web Application for public git repositories hosting>
# Copyright (C) <2009>  Gabriel Falcão <gabriel@nacaolivre.org>
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import sys
import time
import cherrypy
from os import kill
from os.path import dirname, join, abspath
from datetime import datetime
from threading import Thread
from cherrypy.process.plugins import SimplePlugin
from cleese import Executer

class ShowCurrentTime(Thread):
    def __init__(self, output=None):
        Thread.__init__(self)
        if not output:
            output = sys.stdout

        self.output = output
        self.keep_working = True

    def run(self):
        while self.keep_working:
            time.sleep(1)
            now = datetime.now()
            self.output.write("The current time is: %s\n" % now.strftime("%H:%M:%S"))

class GitDaemon(SimplePlugin):
    """ Runs git daemon """
    command = "git daemon --pid-file=gitdaemon.pid --enable=receive-pack " \
              "--reuseaddr --max-connections=0 --export-all " \
              "--listen=0.0.0.0 --base-path=%s --base-path-relaxed "
    def __init__(self, bus, base_path, working_dir):
        SimplePlugin.__init__(self, bus)
        self.command = self.command % base_path
        self.daemon = Executer(self.command, working_dir)
        self.base_path = base_path
        self.working_dir = working_dir

    def start(self):
        self.daemon.execute()
        if self.daemon.poll():
            self.bus.log('Could not run git daemon, check if you already have a git daemon running at port 9418.')
            self.bus.log('Detailed problem:\n%s' % self.daemon.result.log)
            raise SystemExit(1)

        self.bus.log('Git daemon plugin is running.\n%s' % self.command)
        self.bus.log('Exporting all repositories under %s' % self.base_path)

    def stop(self):
        self.graceful()
        self.bus.log("Cleaning up GitDaemon's shell executer")
        del self.daemon

    def graceful(self):
        self.bus.log('Killing git daemon, pid %d' % self.daemon.process.pid)
        kill(self.daemon.process.pid, 9)
        self.bus.log('git daemon is now dead')

class TimeDisplay(SimplePlugin):
    """A bus that keep showing the time"""

    def __init__(self, bus):
        SimplePlugin.__init__(self, bus)
        self.thread = ShowCurrentTime()

    def start(self):
        self.thread.start()

    def stop(self):
        self.thread.keep_working = False
        self.thread.join()

def startup():
    wd = abspath(join(dirname(__file__), '..'))
    base_path = join(wd, 'repositories')
    p = GitDaemon(cherrypy.engine, base_path, wd)
    p.subscribe()
