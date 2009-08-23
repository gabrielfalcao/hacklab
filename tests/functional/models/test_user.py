# -*- coding: utf-8 -*-
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
from nose.tools import with_setup, assert_equals
from hacklab.models import User, meta

from db import create_all, drop_all

@with_setup(create_all, drop_all)
def test_can_create_user():
    User.create(name=u'Gabriel Falcão',
                email=u'gabriel@nacaolivre.org',
                password=u'should-be-hash-sha1')

    Session = meta.get_session()
    session = Session()
    users = session.query(User).all()
    assert_equals(len(users), 1)
    user = users[0]
    assert_equals(user.name, u'Gabriel Falcão')
    assert_equals(user.email, u'gabriel@nacaolivre.org')
    assert_equals(user.password, u'should-be-hash-sha1')
