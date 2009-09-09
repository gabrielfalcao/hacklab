# -*- coding: utf-8 -*-
import types
import cherrypy
from hacklab import controllers
from nose.tools import assert_raises
from nose.tools import assert_equals
from nose.tools import with_setup

from hacklab.models import *
from hacklab.models.meta import get_engine
from hacklab.models.base import metadata

engine = get_engine(echo=False)

def setup_controller_tests():
    metadata.drop_all(engine)
    metadata.create_all(engine)

    cherrypy.session = {}

def teardown_controller_tests():
    metadata.drop_all(engine)
    del cherrypy.session

def test_authenticated_route_returns():
    "authenticated_route() returns a function"
    got = controllers.authenticated_route('/some-path')
    assert isinstance(got, types.FunctionType)

def test_authenticated_returns_route_tuple():
    "authenticated_route() decorated function returns routed tuple"
    @controllers.authenticated_route('/some-path')
    def my_function():
        pass

    assert isinstance(my_function, tuple)
    assert len(my_function) is 2
    assert isinstance(my_function[0], types.FunctionType)
    assert isinstance(my_function[1], tuple)

@with_setup(setup_controller_tests, teardown_controller_tests)
def test_authenticated_route_raises_redirect_when_no_userid_in_session():
    "authenticated_route() raises redirect when session have no user_id"
    @controllers.authenticated_route('/some-path')
    def my_function(user):
        return "my return"

    assert_raises(cherrypy.HTTPRedirect, my_function[0], 'my-user')

@with_setup(setup_controller_tests, teardown_controller_tests)
def test_authenticated_route_raises_redirect_when_user_doesnt_exist():
    "authenticated_route() raises redirect when user does not exist"
    cherrypy.session['user_id'] = 9999
    @controllers.authenticated_route('/some-path')
    def my_function(user):
        return "my return"

    assert_raises(cherrypy.HTTPRedirect, my_function[0], 'my-user')


@with_setup(setup_controller_tests, teardown_controller_tests)
def test_authenticated_route_goes_fine_if_user_exists():
    "authenticated_route() execute the method with user as first param"
    user = User.create(name=u'some-name',
                       username=u'some-user',
                       email=u'some@email.com',
                       password=u'some-password')

    cherrypy.session['user_id'] = user.id
    class SomeController(object):
        @controllers.authenticated_route('/some-path')
        def my_function(self, user, *args, **kw):
            return "user: %s" % user.name

    got = SomeController.my_function[0](None)
    assert_equals(got, 'user: some-name')
