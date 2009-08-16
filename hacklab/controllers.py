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
import startup

from datetime import datetime
from sponge import route
from sponge import Controller
from sponge import template

startup.startup()

AVAILABLE_FORMATS = {
    'date': '%Y-%m-%d',
    'time': '%H:%M:%S',
    'date_and_time': '%Y-%m-%d - %H:%M:%S',
}

INVALID_FORMAT_STRING = 'invalid format, should be in: %s'
TIME_JSON = '{"time": "%s"}'

class AjaxController(Controller):
    @route('/current_:kind', name='ajax_time')
    def get_ajax_time(self, kind):
        now = datetime.now()
        kind = kind.lower()
        if kind not in AVAILABLE_FORMATS:
            cherrypy.response.status = 400
            return INVALID_FORMAT_STRING % ", ".join(AVAILABLE_FORMATS.keys())

        chosen = AVAILABLE_FORMATS[kind]
        formatted = now.strftime(chosen)
        return TIME_JSON % formatted

class HelloWorldController(Controller):
    @route('/', 'hello_index')
    def index(self):
        return template.render_html('index.html')

    @route('/:what', 'hello_custom')
    def custom_page(self, what):
        if what.lower() not in ('work', 'play'):
            return 'Invalid action: %s' % what

        return template.render_html('custom.html', {'action': what})
