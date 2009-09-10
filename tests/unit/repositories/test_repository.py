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

def meta_stub(mocker):
    session = mocker.CreateMockAnything()
    meta = mocker.CreateMockAnything()
    meta.get_session().AndReturn(session)
    return meta, session

def test_repository_create_setattr():
    "Repository.create() should set given attributes in a new object"

    mocker = Mox()

    class ModelStub(rep.Repository):
        name = None
        email = None
        __setattr__ = mocker.CreateMockAnything()
        def save(self):
            pass

    ModelStub.__setattr__('name', 'John Doe')
    ModelStub.__setattr__('email', 'john@doe.net')

    mocker.ReplayAll()
    ModelStub.create(name='John Doe', email='john@doe.net')
    mocker.VerifyAll()

def test_repository_create_saves():
    "Repository.create() should save the object"

    mocker = Mox()

    class ModelStub(rep.Repository):
        name = None
        email = None
        save = mocker.CreateMockAnything()

    ModelStub.save()

    mocker.ReplayAll()
    ModelStub.create(name='John Doe', email='john@doe.net')
    mocker.VerifyAll()

def test_repository_create_returns_a_instance_of_model():
    "Repository.create() should return a instance of subclassed model"

    class ModelStub(rep.Repository):
        name = None
        email = None
        def save(self):
            pass

    got = ModelStub.create(name='John Doe', email='john@doe.net')

    assert isinstance(got, ModelStub)
    assert_equals(got.name, 'John Doe')
    assert_equals(got.email, 'john@doe.net')

def test_repository_save_adds_uuid():
    "Repository.save() should set a uuid to model if hasn't one yet"

    mocker = Mox()
    mocker.StubOutWithMock(rep, 'uuid')

    old_meta = rep.meta
    rep.meta, session_mock = meta_stub(mocker)

    rep.uuid.uuid4().AndReturn('some-uuid')

    class ModelStub(rep.Repository):
        uuid = None

    model = ModelStub()

    session_mock.object_session(model).AndReturn(False)
    session_mock.add(model)
    session_mock.commit()
    session_mock.expire(model)

    mocker.ReplayAll()
    try:
        model.save()
        assert_equals(model.uuid, 'some-uuid')
        mocker.VerifyAll()
    finally:
        mocker.UnsetStubs()
        rep.meta = old_meta

def test_repository_save_doesnt_touch():
    "Repository.save() shouldn't set a uuid if it already has one"

    mocker = Mox()

    old_meta = rep.meta
    rep.meta, session_mock = meta_stub(mocker)

    class ModelStub(rep.Repository):
        uuid = 'my-uuid'

    model = ModelStub()
    session_mock.object_session(model).AndReturn(False)
    session_mock.add(model)
    session_mock.commit()
    session_mock.expire(model)

    mocker.ReplayAll()
    try:
        model.save()
        assert_equals(model.uuid, 'my-uuid')
        mocker.VerifyAll()
    finally:
        rep.meta = old_meta

def test_repository_save_adds_object_to_session_and_commits():
    "Repository.save() should set add object to session, and commit."

    mocker = Mox()
    mocker.StubOutWithMock(rep, 'meta')

    class ModelStub(rep.Repository):
        uuid = None

    model = ModelStub()

    session_mock = mocker.CreateMockAnything()
    session_mock.object_session(model).AndReturn(False)
    session_mock.add(model)
    session_mock.commit()
    session_mock.expire(model)
    rep.meta.get_session().AndReturn(session_mock)

    mocker.ReplayAll()
    try:
        model.save()
        mocker.VerifyAll()
    finally:
        mocker.UnsetStubs()

def test_repository_delete_does_commit():
    "Repository.delete() should delete object and commit session."

    mocker = Mox()
    mocker.StubOutWithMock(rep, 'meta')

    class ModelStub(rep.Repository):
        id = 'should-be-id'
        uuid = 'should-be-uuid'

    model = ModelStub()

    query_mock = mocker.CreateMockAnything()
    query_mock.filter_by(id='should-be-id',
                         uuid='should-be-uuid').AndReturn(query_mock)
    query_mock.delete()

    session_mock = mocker.CreateMockAnything()
    session_mock.query(ModelStub).AndReturn(query_mock)
    session_mock.commit()

    rep.meta.get_session().AndReturn(session_mock)
    mocker.ReplayAll()
    try:
        model.delete()
        mocker.VerifyAll()
    finally:
        mocker.UnsetStubs()
