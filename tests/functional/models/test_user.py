# -*- coding: utf-8 -*-
# Copyright (C) <2009>  John Doe <john@doe.com>
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
import sha
import md5
from nose.tools import with_setup, assert_equals
from hacklab.models import User, meta

from db import create_all, drop_all

@with_setup(create_all, drop_all)
def test_can_create_user():
    "User.create() creates and persists a new user"
    User.create(name=u'John Doe',
                email=u'john@doe.com',
                password=u'some-password')

    Session = meta.get_session()
    session = Session()
    users = session.query(User).all()
    assert_equals(len(users), 1)
    user = users[0]
    assert_equals(user.name, u'John Doe')
    assert_equals(user.email, u'john@doe.com')

@with_setup(create_all, drop_all)
def test_new_user_has_hashed_password():
    "User.create() creates a user with hashed password"
    User.create(name=u'John Doe',
                email=u'john@doe.com',
                password=u'some-password')

    Session = meta.get_session()
    session = Session()
    user = session.query(User).first()

    concatenated = 'john@doe.com+some-password'
    expected_password = "hash:%s" % sha.new(concatenated).hexdigest()

    assert_equals(user.password, expected_password)

@with_setup(create_all, drop_all)
def test_user_can_get_gravatar_url():
    "User().get_gravatar() should fetch user's gravatar"

    user = User.create(name=u'John Doe',
                       email=u'john@doe.com',
                       password=u'some-password')

    email_md5 = md5.new('john@doe.com').hexdigest()
    expected_url = u'http://www.gravatar.com/avatar/%s.jpg' % email_md5
    assert_equals(user.get_gravatar(), expected_url)

