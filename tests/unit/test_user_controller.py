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
from mox import Mox
from nose.tools import assert_equals
from hacklab import controllers

def test_delete_key():
    "delete_key() fetches user from db and delete"
    mocker = Mox()

    mocker.StubOutWithMock(controllers, 'models')
    mocker.StubOutWithMock(controllers, 'cherrypy')

    user_mock = mocker.CreateMockAnything()
    key_mock = mocker.CreateMockAnything()
    key_mock.as_dict().AndReturn(dict(should_be='a dict'))
    key_mock.delete()

    controllers.cherrypy.session = {'user_id': 'should-be-user-id'}

    controllers.models.User = mocker.CreateMockAnything()
    controllers.models.PublicKey = mocker.CreateMockAnything()

    controllers.models.User.get_by(id='should-be-user-id').AndReturn(user_mock)
    controllers.models.PublicKey.get_by(uuid='should-be-key-uuid').AndReturn(key_mock)

    ctrl = controllers.UserController()
    mocker.ReplayAll()
    try:
        got = ctrl.delete_key(uuid='should-be-key-uuid')
        assert_equals(got, '{"should_be": "a dict"}')
        mocker.VerifyAll()
    finally:
        mocker.UnsetStubs()


