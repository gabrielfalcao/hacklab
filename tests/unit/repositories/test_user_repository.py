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
from hacklab.models import repositories as rep

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
        pass
