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

def authenticated_route(path, name=None, login_at='/login'):
    def decor(func):
        def wrap(*args, **kw):
            user = cherrypy.session.get('user')
            if user:
                return func(*args, **kw)

            pi = cherrypy.request.path_info
            raise cherrypy.HTTPRedirect("%s?redirect=%s" % (login_at, pi))

        wrap.__name__ = func.__name__
        r = route(path, name)
        return r(wrap)

    return decor

class UserController(Controller):
    @route('/new')
    def new_user(self, **data):
        if 'email' not in data:
            data['email'] = ''

        for k in data.keys():
            if k not in ('name', 'email', 'password'):
                del data[k]
            else:
                data[k] = unicode(data[k], 'utf-8')

        if 'email' and 'password' in data:
            cherrypy.session['user'] = User.create(**data)
            raise cherrypy.HTTPRedirect('/repository/new')

        return template.render_html('register.html', data)

    @route('/logout')
    def logout(self, **data):
        if 'user' in cherrypy.session:
            del cherrypy.session['user']

        raise cherrypy.HTTPRedirect('/')

class HackLabController(Controller):
    @route('/')
    def index(self):
        raise cherrypy.HTTPRedirect('/user/new')

    @authenticated_route('/repository/new')
    def new_repository(self):
        user = cherrypy.session['user']
        return template.render_html('repository.new.html', {'user': user})

    @route('/login')
    def login(self, **data):
        context = {}
        email = data.get('email')
        password = data.get('password')
        redirect_to = data.get('redirect', '/')

        context['not_registered'] = False
        context['wrong_password'] = False
        context['email'] = email or ''

        if email and password:
            try:
                user = User.authenticate(email, password)
                cherrypy.session['user'] = user
                raise cherrypy.HTTPRedirect(redirect_to)

            except User.NotFound, e:
                context['not_registered'] = unicode(email)

            except User.WrongPassword, e:
                context['wrong_password'] = unicode(e)

        return template.render_html('login.html', context)

    @authenticated_route('/dashboard')
    def dashboard(self):
        user = cherrypy.session['user']
        return template.render_html('dashboard.html', {'user': user})
