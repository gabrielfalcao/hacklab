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

def test_get_gravatar():
    "UserRepository().get_gravatar() should return user's gravatar url."
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


def test_add_public_key_appends_pubkeymodel():
    "UserRepository().add_public_key() should add PublicKey to user.keys"
    mocker = Mox()

    mocker.StubOutWithMock(rep, 'meta')

    pubkey_model_mock = mocker.CreateMockAnything()
    pubkey_model_mock(description=u'my description',
                      data=u'my-ssh-key-data'). \
        AndReturn('should-be-pubkey-model-object')
    rep.meta.get_model('PublicKey').AndReturn(pubkey_model_mock)

    class UserStub(rep.UserRepository):
        keys = []
        def save(self):
            pass

    user = UserStub()
    mocker.ReplayAll()
    expected = 'http://www.gravatar.com/avatar/should-be-md5-of-email.jpg'
    try:
        user.add_public_key('my description', 'my-ssh-key-data')
        assert_equals(user.keys[0], 'should-be-pubkey-model-object')
        mocker.VerifyAll()
    finally:
        mocker.UnsetStubs()

def test_add_public_key_saves_the_model():
    "UserRepository().add_public_key() should save the model"
    mocker = Mox()

    mocker.StubOutWithMock(rep, 'meta')

    pubkey_model_mock = mocker.CreateMockAnything()
    pubkey_model_mock(description=u'my description',
                      data=u'my-ssh-key-data'). \
        AndReturn('should-be-pubkey-model-object')
    rep.meta.get_model('PublicKey').AndReturn(pubkey_model_mock)

    class UserStub(rep.UserRepository):
        keys = []
        save = mocker.CreateMockAnything()

    UserStub.save()
    user = UserStub()
    mocker.ReplayAll()
    expected = 'http://www.gravatar.com/avatar/should-be-md5-of-email.jpg'
    try:
        user.add_public_key('my description', 'my-ssh-key-data')
        assert_equals(user.keys[0], 'should-be-pubkey-model-object')
        mocker.VerifyAll()
    finally:
        mocker.UnsetStubs()

def test_make_hashed_password():
    "UserRepository.make_hashed_password() make a hash with user data"
    mocker = Mox()

    mocker.StubOutWithMock(rep, 'sha')

    sha_mock = mocker.CreateMockAnything()
    sha_mock.hexdigest().AndReturn('should-be-email+password-hash')

    rep.sha.new('some@email.com+some-password').AndReturn(sha_mock)

    mocker.ReplayAll()
    expected = 'hash:should-be-email+password-hash'
    try:
        got = rep.UserRepository.make_hashed_password('some@email.com',
                                                      'some-password')
        assert_equals(got, expected)
        mocker.VerifyAll()
    finally:
        mocker.UnsetStubs()

@with_setup(setup_cherrypy, teardown_cherrypy)
def test_save_hashes_password_if_does_not_start_with_hash():
    "UserRepository().save() should replace the password with a hash"
    mocker = Mox()
    mocker.StubOutWithMock(rep, 'meta')
    class UserStub(rep.UserRepository):
        fs = mocker.CreateMockAnything()
        username = 'my-username'
        email = 'my@email.com'
        uuid = 'my-uuid'
        password = 'does not start with hash:'
        make_hashed_password = mocker.CreateMockAnything()
        def get_repository_dir(self):
            return '/my/repo/dir'

    UserStub.fs.exists('/my/repo/dir').AndReturn(True)
    UserStub.make_hashed_password('my@email.com',
                                  'does not start with hash:'). \
        AndReturn('my-hash')

    user = UserStub()

    session_mock = mocker.CreateMockAnything()
    session_mock.add(user)
    session_mock.commit()

    rep.meta.get_session().AndReturn(session_mock)

    mocker.ReplayAll()
    try:
        user.save()
        assert_equals(user.password, 'my-hash')
        mocker.VerifyAll()
    finally:
        mocker.UnsetStubs()

@with_setup(setup_cherrypy, teardown_cherrypy)
def test_save_doesnt_touch_password_if_already_hashed():
    "UserRepository().save() should not touch a already hashed password"
    mocker = Mox()
    mocker.StubOutWithMock(rep, 'meta')
    class UserStub(rep.UserRepository):
        fs = mocker.CreateMockAnything()
        username = 'my-username'
        email = 'my@email.com'
        uuid = 'my-uuid'
        password = 'hash:my-hash'
        make_hashed_password = mocker.CreateMockAnything()
        def get_repository_dir(self):
            return '/my/repo/dir'

    UserStub.fs.exists('/my/repo/dir').AndReturn(True)

    user = UserStub()

    session_mock = mocker.CreateMockAnything()
    session_mock.add(user)
    session_mock.commit()

    rep.meta.get_session().AndReturn(session_mock)

    mocker.ReplayAll()
    try:
        user.save()
        assert_equals(user.password, 'hash:my-hash')
        mocker.VerifyAll()
    finally:
        mocker.UnsetStubs()

@with_setup(setup_cherrypy, teardown_cherrypy)
def test_save_should_create_user_repo_dir():
    "UserRepository().save() creates user's repository if it does not exist"
    mocker = Mox()
    mocker.StubOutWithMock(rep, 'meta')
    class UserStub(rep.UserRepository):
        fs = mocker.CreateMockAnything()
        username = 'my-username'
        email = 'my@email.com'
        uuid = 'my-uuid'
        password = 'hash:my-hash'
        make_hashed_password = mocker.CreateMockAnything()
        def get_repository_dir(self):
            return '/my/repo/dir'

    UserStub.fs.exists('/my/repo/dir').AndReturn(False)
    UserStub.fs.mkdir('/my/repo/dir')

    user = UserStub()

    session_mock = mocker.CreateMockAnything()
    session_mock.add(user)
    session_mock.commit()

    rep.meta.get_session().AndReturn(session_mock)

    mocker.ReplayAll()
    try:
        user.save()
        mocker.VerifyAll()
    finally:
        mocker.UnsetStubs()

def test_authenticate_returns_user_if_found():
    "UserRepository.authenticate() returns user object if is found"

    mocker = Mox()
    mocker.StubOutWithMock(rep, 'meta')

    class UserStub(rep.UserRepository):
        email = 'my@email.com'
        password = 'hash:my-hash'
        make_hashed_password = mocker.CreateMockAnything()

    UserStub.make_hashed_password('my@email.com', 'some-password'). \
        AndReturn('hash:my-hash')

    user = UserStub()

    session_mock = mocker.CreateMockAnything()
    session_mock.query(UserStub).AndReturn(session_mock)
    session_mock.filter_by(email=u'my@email.com').AndReturn(session_mock)
    session_mock.first().AndReturn(user)

    rep.meta.get_session().AndReturn(session_mock)

    mocker.ReplayAll()
    try:
        got = UserStub.authenticate('my@email.com', 'some-password')
        assert_equals(got, user)
        mocker.VerifyAll()
    finally:
        mocker.UnsetStubs()

def test_authenticate_raises_not_found():
    "UserRepository.authenticate() raises exception when user's not found"

    mocker = Mox()
    mocker.StubOutWithMock(rep, 'meta')

    class UserStub(rep.UserRepository):
        email = 'my@email.com'
        password = 'hash:my-hash'
        make_hashed_password = mocker.CreateMockAnything()

    session_mock = mocker.CreateMockAnything()
    session_mock.query(UserStub).AndReturn(session_mock)
    session_mock.filter_by(email=u'my@email.com').AndReturn(session_mock)
    session_mock.first().AndReturn(None)

    rep.meta.get_session().AndReturn(session_mock)

    mocker.ReplayAll()
    try:
        assert_raises(UserStub.NotFound,
                      UserStub.authenticate,
                      'my@email.com', 'some-password')
        mocker.VerifyAll()
    finally:
        mocker.UnsetStubs()

def test_authenticate_raises_wrong_password():
    "UserRepository.authenticate() raises exception with wrong password"


    mocker = Mox()
    mocker.StubOutWithMock(rep, 'meta')

    class UserStub(rep.UserRepository):
        email = 'my@email.com'
        password = 'hash:my-hash'
        make_hashed_password = mocker.CreateMockAnything()

    UserStub.make_hashed_password('my@email.com', 'wrong-password'). \
        AndReturn('hash:wrong-hash')

    user = UserStub()

    session_mock = mocker.CreateMockAnything()
    session_mock.query(UserStub).AndReturn(session_mock)
    session_mock.filter_by(email=u'my@email.com').AndReturn(session_mock)
    session_mock.first().AndReturn(user)

    rep.meta.get_session().AndReturn(session_mock)

    mocker.ReplayAll()
    try:
        assert_raises(UserStub.WrongPassword,
                      UserStub.authenticate,
                      'my@email.com', 'wrong-password')
        mocker.VerifyAll()
    finally:
        mocker.UnsetStubs()
