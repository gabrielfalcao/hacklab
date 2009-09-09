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
from nose.tools import assert_equals
from hacklab import controllers

def test_json_response_should_serialize_through_simplejson():
    "json_response() should serialize data with simplejson"
    mocker = Mox()

    mocker.StubOutWithMock(controllers, 'simplejson')
    controllers.simplejson.dumps('should-be-data'). \
        AndReturn('should-be-jsonified-data')

    mocker.ReplayAll()
    try:
        got = controllers.json_response('should-be-data')
        assert_equals(got, 'should-be-jsonified-data')
        assert_equals(cherrypy.response.headers['Content-Type'],
                      'text/plain')
        mocker.VerifyAll()
    finally:
        mocker.UnsetStubs()

def test_json_response_should_change_response_content_type():
    "json_response() should change response content-type to text/plain"
    controllers.json_response('should-be-data')
    assert_equals(cherrypy.response.headers['Content-Type'],
                  'text/plain')

def test_ajax_error_serializes_message_into_json_data():
    "ajax_error() should serialize message within json"

    got = controllers.ajax_error('something went wrong')
    assert_equals(got,
                  '{"details": null, "error": ' \
                  '"something went wrong"}')

def test_ajax_error_serializes_details_into_json_data():
    "ajax_error() should serialize details within json"

    got = controllers.ajax_error('something went wrong',
                                 'the test must not break')
    assert_equals(got,
                  '{"details": "the test must not break", ' \
                  '"error": "something went wrong"}')
