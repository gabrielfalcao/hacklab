# -*- coding: utf-8 -*-
import types
import cherrypy
from hacklab.models import User
from hacklab.models.meta import get_engine
from hacklab.models.meta import get_session
from hacklab.models.base import metadata

from nose.tools import with_setup
engine = get_engine(echo=False)

def setup_controller_tests():
    metadata.drop_all(engine)
    metadata.create_all(engine)
    cherrypy.session = {}

def teardown_controller_tests():
    metadata.drop_all(engine)
    del cherrypy.session

@with_setup(setup_controller_tests, teardown_controller_tests)
def test_user_can_be_deleted():
    "User().delete() should delete a user"
    session = get_session()

    assert session.query(User).count() is 0
    user = User.create(name=u'some-name',
                       username=u'some-username',
                       email=u'some@email.com',
                       password=u'some-password')
    assert session.query(User).count() is 1
    user.delete()
    assert session.query(User).count() is 0
