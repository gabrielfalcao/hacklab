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
from mox import Mox
from nose.tools import assert_equals, with_setup
from hacklab.models import repositories as rep

old_config = {}
def setup_cherrypy():
    for key in ('sponge.root', 'sponge.extra',):
        value = cherrypy.config.get(key)
        if value:
            old_config[key] = value

    cherrypy.config['sponge.root'] = '/root/path/'
    cherrypy.config['sponge.extra'] = {}
    cherrypy.config['sponge.extra']['repositories-dir'] = 'repo-dir'

def teardown_cherrypy():
    del cherrypy.config['sponge.root']
    del cherrypy.config['sponge.extra']
    cherrypy.config.update(old_config)

def test_get_gravatar():
    "UserRepository().get_gravatar() should return user's' gravatar url."
    mocker = Mox()

    mocker.StubOutWithMock(rep, 'md5')

    md5_mock = mocker.CreateMockAnything()
    md5_mock.hexdigest().AndReturn('should-be-md5-of-email')

    rep.md5.new('some@email.com').AndReturn(md5_mock)

    class UserStub(rep.UserRepository):
        email = 'some@email.com'

    user = UserStub()
    mocker.ReplayAll()
    expected = 'http://www.gravatar.com/avatar/should-be-md5-of-email.jpg'
    try:
        assert_equals(user.get_gravatar(), expected)
        mocker.VerifyAll()
    finally:
        mocker.UnsetStubs()

@with_setup(setup_cherrypy, teardown_cherrypy)
def test_get_repository_dir():
    "UserRepository().get_repository_dir() returns user's repository dir."
    mocker = Mox()

    class UserStub(rep.UserRepository):
        username = 'some-username'
        fs = mocker.CreateMockAnything()

    UserStub.fs.join('/root/path/', 'repo-dir'). \
        AndReturn('should-be-relative-path')

    UserStub.fs.join('should-be-relative-path', 'some-username'). \
        AndReturn('should-be-relative-username-repos-path')

    UserStub.fs.abspath('should-be-relative-username-repos-path'). \
        AndReturn('should-be-absolute-path-to-user-repo')

    user = UserStub()
    mocker.ReplayAll()
    assert_equals(user.get_repository_dir(),
                  'should-be-absolute-path-to-user-repo')
    mocker.VerifyAll()
