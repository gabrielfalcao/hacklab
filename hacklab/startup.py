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
import cherrypy
from os import kill
from os.path import dirname, join, abspath
from cherrypy.process.plugins import SimplePlugin
from cleese import Executer

class GitDaemon(SimplePlugin):
    """ Runs git daemon """
    command = "git daemon " \
              "--export-all " \
              "--listen=0.0.0.0 --base-path=%s"
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

def startup():
    wd = abspath(join(dirname(__file__), '..'))
    base_path = join(wd, 'repositories')
    p = GitDaemon(cherrypy.engine, base_path, wd)
    cherrypy.config['tools.sessions.storage_type'] = "file"
    cherrypy.config['tools.sessions.storage_path'] = join(wd, '.sessions')
    p.subscribe()
