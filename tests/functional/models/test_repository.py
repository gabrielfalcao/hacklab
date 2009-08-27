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

import cherrypy

from os.path import abspath, join
from nose.tools import with_setup, assert_equals
from hacklab.models import GitRepository, User, meta

from db import create_all, drop_all

root = cherrypy.config['sponge.root']
repo_dir = cherrypy.config['sponge.extra']['repositories-dir']
repository_base = abspath(join(root, repo_dir))

@with_setup(create_all, drop_all)
def test_can_create_repository():
    "GitRepository.create() creates and persists a new repository"

    gabriel = User.create(name=u'Gabriel Falcão',
                          username=u'gabriel.falcao',
                          email=u'gabriel@nacaolivre.org',
                          password=u'some-passwd')

    GitRepository.create(name=u'Hacklab Contributions',
                         description=u'Some description...',
                         owner=gabriel,
                         slug=u"hacklab-contrib")

    Session = meta.get_session()
    session = Session()
    repositories = session.query(GitRepository).all()
    assert_equals(len(repositories), 1)
    repository = repositories[0]
    assert_equals(repository.name, u'Hacklab Contributions')
    assert_equals(repository.description, u'Some description...')
    assert_equals(repository.slug, u'hacklab-contrib')
    assert_equals(repository.owner.username, 'gabriel.falcao')

