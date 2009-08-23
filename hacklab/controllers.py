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
from sponge import route, Controller, template
from hacklab.models import User
from hacklab.models.meta import get_session

class UserController(Controller):
    @route('/new')
    def new_user(self, **data):
        for k in data.keys():
            if k not in ('name', 'email', 'password'):
                del data[k]

        cherrypy.session['user'] = User.create(**data)
        raise cherrypy.HTTPRedirect('/dashboard')

class HackLabController(Controller):
    @route('/')
    def index(self):
        return template.render_html('index.html')

    @route('/dashboard')
    def dashboard(self):
        Session = get_session()
        session = Session()
        user = session.query(User).first()
        return template.render_html('dashboard.html', {'user': user})
