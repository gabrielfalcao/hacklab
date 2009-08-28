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
import cherrypy

from os.path import exists, abspath, join
from nose.tools import with_setup, assert_equals, assert_raises
from hacklab.models import User, meta

from db import create_all, drop_all

root = cherrypy.config['sponge.root']
repo_dir = cherrypy.config['sponge.extra']['repositories-dir']
repository_base = abspath(join(root, repo_dir))

@with_setup(create_all, drop_all)
def test_can_create_user():
    "User.create() creates and persists a new user"
    User.create(name=u'John Doe',
                username=u'john.doe',
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
                username=u'john.doe',
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
                       username=u'john.doe',
                       email=u'john@doe.com',
                       password=u'some-password')

    email_md5 = md5.new('john@doe.com').hexdigest()
    expected_url = u'http://www.gravatar.com/avatar/%s.jpg' % email_md5
    assert_equals(user.get_gravatar(), expected_url)

@with_setup(create_all, drop_all)
def test_can_authenticate_user():
    "User.authenticate(email, passwd) should fetch a valid user"

    User.create(name=u'Foo Bar',
                username=u'john.doe',
                email=u'foo@bar.com',
                password=u'my-password')


    user = User.authenticate('foo@bar.com', 'my-password')
    assert_equals(user.name, 'Foo Bar')
    assert_equals(user.email, 'foo@bar.com')

@with_setup(create_all, drop_all)
def test_authenticate_raises_not_found():
    "User.authenticate raises User.NotFound when not found"

    assert_raises(User.NotFound,
                  User.authenticate, 'not@database.local', 'my-password')

@with_setup(create_all, drop_all)
def test_authenticate_raises_wrong_password():
    "User.authenticate raises User.WrongPassword when password is wrong"

    User.create(name=u'Auth User',
                username=u'john.doe',
                email=u'auth@user.com',
                password=u'my-password')

    assert_raises(User.WrongPassword,
                  User.authenticate, 'auth@user.com', 'wrong-password')

@with_setup(create_all, drop_all)
def test_create_will_make_a_repository_dir_for_user():
    "User.create() makes a repository base dir for user"

    user = User.create(name=u'Auth User',
                       username=u'john.doe',
                       email=u'auth@user.com',
                       password=u'my-password')

    expected = join(repository_base, "john.doe")
    msg = "After creating a user of uuid %s, the path %s " \
          "should exist in filesystem" % (user.uuid, expected)
    assert exists(expected), msg

@with_setup(create_all, drop_all)
def test_user_get_repository_dir():
    "User().get_repository_dir() give full path to user's root dir"

    user = User.create(name=u'Auth User',
                       username=u'john.doe',
                       email=u'auth@user.com',
                       password=u'my-password')

    expected = abspath(join(repository_base, "john.doe"))
    got = user.get_repository_dir()
    assert_equals(got, expected)

@with_setup(create_all, drop_all)
def test_can_add_keys_to_user():
    "User().keys.add_public_key(description, content) adds a ssh pub key to user"

    user = User.create(name=u'SSH User',
                       username=u'john.doe',
                       email=u'auth@user.com',
                       password=u'my-password')

    user.add_public_key("laptop key", "ssh-rsa aAbBcCdD1e2f3g4h5I== john@doe.net")
    assert_equals(user.keys[0].description, "laptop key")
    assert_equals(user.keys[0].data, "ssh-rsa aAbBcCdD1e2f3g4h5I== john@doe.net")

