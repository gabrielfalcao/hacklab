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
from nose.tools import with_setup
from nose.tools import assert_equals
from nose.tools import assert_raises
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

def test_get_permalink():
    "GitRepoRepository().get_permalink() should return repo's url."
    mocker = Mox()

    mocker.StubOutWithMock(rep, 'template')
    class GitRepoStub(rep.GitRepoRepository):
        slug = 'should-be-slug'
        class owner:
            username = 'should-be-username'


    git = GitRepoStub()

    rep.template.make_url('/user/should-be-username/should-be-slug'). \
        AndReturn('should-be-permalink')


    mocker.ReplayAll()
    try:
        got = git.get_permalink()
        assert_equals(got, 'should-be-permalink')
        mocker.VerifyAll()
    finally:
        mocker.UnsetStubs()

def test_save_if_repo_dir_does_not_exist():
    "GitRepoRepository().save() when dir does not exist."
    mocker = Mox()

    owner_mock = mocker.CreateMockAnything()
    fs_mock = mocker.CreateMockAnything()

    mocker.StubOutWithMock(rep, 'cleese')
    mocker.StubOutWithMock(rep, 'meta')
    mocker.StubOutWithMock(rep, 'uuid')

    class GitRepoStub(rep.GitRepoRepository):
        uuid = None
        title = 'brand new slug'
        slug = None
        owner = owner_mock
        fs = fs_mock

    git = GitRepoStub()

    owner_mock.get_repository_dir('brand-new-slug'). \
        AndReturn('should-be-repo-dir')

    fs_mock.exists('should-be-repo-dir'). \
        AndReturn(True)


    rep.uuid.uuid4().AndReturn('should-be-a-new-uuid')
    session_mock = mocker.CreateMockAnything()
    session_mock.object_session(git).AndReturn(True)
    session_mock.object_session(git).AndReturn(session_mock)
    session_mock.expunge(git)
    session_mock.add(git)
    session_mock.commit()
    session_mock.expire(git)
    rep.meta.get_session().AndReturn(session_mock)

    fs_mock.pushd('should-be-repo-dir')
    fs_mock.popd()

    executer_mock = mocker.CreateMockAnything()
    executer_mock.execute()

    rep.cleese.Executer('git init --bare'). \
        AndReturn(executer_mock)

    mocker.ReplayAll()
    try:
        git.save()
        mocker.VerifyAll()
    finally:
        mocker.UnsetStubs()

def test_save_if_repo_dir_already_exists():
    "GitRepoRepository().save() when dir already exists."
    mocker = Mox()

    owner_mock = mocker.CreateMockAnything()
    fs_mock = mocker.CreateMockAnything()

    mocker.StubOutWithMock(rep, 'cleese')
    mocker.StubOutWithMock(rep, 'meta')
    mocker.StubOutWithMock(rep, 'uuid')

    class GitRepoStub(rep.GitRepoRepository):
        uuid = None
        title = 'brand new slug'
        slug = None
        owner = owner_mock
        fs = fs_mock

    git = GitRepoStub()

    owner_mock.get_repository_dir('brand-new-slug'). \
        AndReturn('should-be-repo-dir')

    fs_mock.exists('should-be-repo-dir'). \
        AndReturn(False)


    rep.uuid.uuid4().AndReturn('should-be-a-new-uuid')
    session_mock = mocker.CreateMockAnything()
    session_mock.object_session(git).AndReturn(True)
    session_mock.object_session(git).AndReturn(session_mock)
    session_mock.expunge(git)
    session_mock.add(git)
    session_mock.commit()
    session_mock.expire(git)
    rep.meta.get_session().AndReturn(session_mock)

    fs_mock.mkdir('should-be-repo-dir')
    fs_mock.pushd('should-be-repo-dir')
    fs_mock.popd()

    executer_mock = mocker.CreateMockAnything()
    executer_mock.execute()

    rep.cleese.Executer('git init --bare'). \
        AndReturn(executer_mock)

    mocker.ReplayAll()
    try:
        git.save()
        mocker.VerifyAll()
    finally:
        mocker.UnsetStubs()
