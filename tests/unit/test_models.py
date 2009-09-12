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
from hacklab import models
from nose.tools import assert_equals

def test_user_representation():
    "unicode(User()) should represent the class correctly"
    user = models.User(name='John Doe')
    assert_equals(unicode(user), u"<User 'John Doe'>")

def test_gitrepos_representation():
    "unicode(GitRepository()) should represent the class correctly"
    user = models.User(username='john.doe')
    user.get_repository_dir = lambda x: '/some/path/to/%s' % x
    repo = models.GitRepository(slug='foo-repository', owner=user)
    assert_equals(unicode(repo), u"<GitRepository at '/some/path/to/foo-repository'>")

def test_key_representation():
    "unicode(PublicKey()) should represent the class correctly"
    user = models.User(username='john.doe')
    key = models.PublicKey(description='Laptop key', owner=user)
    assert_equals(unicode(key), u"<SSHPublicKey 'Laptop key' of the user 'john.doe'>")
