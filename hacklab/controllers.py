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
import os
import cherrypy
import simplejson
from sponge import route, Controller, template
from hacklab.models import User
from hacklab.models import GitRepository
from hacklab.models import PublicKey
from hacklab.models import meta
from sqlalchemy.exc import IntegrityError

def authenticated_route(path, name=None, login_at='/login'):
    def decor(func):
        def wrap(self, *args, **kw):
            session = meta.get_session()
            user_id = cherrypy.session.get('user_id')
            user = None
            if user_id:
                user = session.query(User).filter_by(id=user_id).first()

            if user:
                return func(self, user=user, *args, **kw)

            pi = cherrypy.request.path_info
            raise cherrypy.HTTPRedirect("%s?redirect=%s" % (login_at, pi))

        wrap.__name__ = func.__name__
        r = route(path, name)
        return r(wrap)

    return decor

def json_response(data):
    cherrypy.response.headers['Content-Type'] = 'text/plain'
    return simplejson.dumps(data)

def ajax_error(message, details=None):
    d = {'error': message,
         'details': details}

    return json_response(d)

def contains_all(data, *params):
    ok = True
    for item in params:
        if not item in data:
            ok = False
            break

        if not data[item]:
            ok = False
            break

    return ok

class UserController(Controller):
    @authenticated_route('/key/:uuid/delete')
    def delete_key(self, user, uuid, **data):
        session = meta.get_session()
        key = session.query(PublicKey). \
              filter_by(uuid=uuid).first()
        d = key.as_dict()
        key.delete()
        return json_response(d)

    @authenticated_route('/change-password')
    def change_password(self, user, **data):
        if contains_all(data, 'password', 'confirm'):
            user.password = data['password']
            user.save()
            return json_response(user.as_dict())

        msg = 'you must provide a password and a confirmation'
        return ajax_error(msg, ValueError(msg))

    @authenticated_route('/add-key')
    def add_key(self, user, **data):
        if contains_all(data, 'key', 'description'):
            desc = data['description']
            key_data = data['key']
            key = user.add_public_key(desc, key_data)
            return json_response(key.as_dict())

        msg = 'you must provide a description and a key'
        return ajax_error(msg, ValueError(msg))

    @authenticated_route('/account')
    def manage_account(self, user, **data):
        return template.render_html('user/account.html', {'user': user})

    @authenticated_route('/:username/:reponame')
    def repository_page(self, user, username, reponame, **data):
        session = meta.get_session()
        repository = session.query(GitRepository). \
                         filter_by(name=reponame, owner=user).first()
        if not repository:
            return template.render_html('repository/not_found.html', {'reponame': reponame})

        return template.render_html('repository/page.html',
                                    {'repository': repository,
                                     'os_user': os.getenv('USER'),
                                     'local_address': cherrypy.config['server.socket_host']})

    @route('/new')
    def new_user(self, **data):
        needed = set(('email', 'username', 'password'))
        if 'email' not in data:
            data['email'] = ''

        if 'username' not in data:
            data['username'] = ''

        for k in data.keys():
            if k not in ('name', 'username', 'email', 'password'):
                del data[k]
            else:
                data[k] = unicode(data[k], 'utf-8')

        if not needed.difference(set(data.keys())):
            try:
                user = User.create(**data)
                cherrypy.session['user_id'] = user.id
                raise cherrypy.HTTPRedirect('/user/account')

            except IntegrityError, e:
                data['error'] = 'the username already exists'

        return template.render_html('user/register.html', data)

    @route('/logout')
    def logout(self, **data):
        if 'user_id' in cherrypy.session:
            del cherrypy.session['user_id']

        raise cherrypy.HTTPRedirect('/')

class HackLabController(Controller):
    @route('/explore/:username/*(path)')
    def explore(self, username, path, **data):
        path = path.split("/")
        reponame = path.pop(0)

        session = meta.get_session()
        user = session.query(User).filter_by(username=username).first()
        if not user:
            cherrypy.response.status = 404
            return template.render_html('user/not_found.html',
                                        {'username': username})

        repo = session.query(GitRepository). \
               filter_by(owner=user, name=reponame).first()
        if not repo:
            cherrypy.response.status = 404
            return template.render_html('repository/not_found.html',
                                        {'reponame': reponame})

        d = repo.list_dir()
        return json_response(d)

    @route('/')
    def index(self):
        raise cherrypy.HTTPRedirect('/login')

    @authenticated_route('/repository/new')
    def new_repository(self, user, **kw):
        if contains_all(kw, 'name'):
            name = kw['name']
            description = kw.get('description', '')
            repository = user.create_repository(name=name,
                                                description=description)
            raise cherrypy.HTTPRedirect(repository.get_permalink())

        return template.render_html('repository/new.html', {'user': user})

    @authenticated_route('/repository/new/ajax')
    def new_repository_ajax(self, user, **kw):
        if contains_all(kw, 'name'):
            name = kw['name']
            description = kw.get('description', '')
            repository = user.create_repository(name=name,
                                                description=description)
            return json_response(repository.as_dict())

        return ajax_error('missing repository name')

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
                cherrypy.session['user_id'] = user.id
                raise cherrypy.HTTPRedirect(redirect_to)

            except User.NotFound, e:
                context['not_registered'] = unicode(email)

            except User.WrongPassword, e:
                context['wrong_password'] = unicode(e)

        return template.render_html('user/login.html', context)

    @authenticated_route('/dashboard')
    def dashboard(self, user):
        return template.render_html('dashboard.html', {'user': user})
