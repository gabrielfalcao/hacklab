# -*- coding: utf-8 -*-
import cherrypy
from mox import Mox
from nose.tools import assert_equals
from hacklab import controllers

class TestHelloWorldController:
    def test_index_calls_render_html(self):
        mox = Mox()

        mox.StubOutWithMock(controllers, 'template')

        controllers.template.render_html('index.html'). \
                    AndReturn('supposed-to-be-the-rendered-html')

        ctrl = controllers.HelloWorldController()

        mox.ReplayAll()
        try:
            expected_return = 'supposed-to-be-the-rendered-html'
            got = ctrl.index()
            assert_equals(got, expected_return)
            mox.VerifyAll()
        finally:
            mox.UnsetStubs()

    def test_custom_page_passes_play_action(self):
        mox = Mox()

        mox.StubOutWithMock(controllers, 'template')
        controllers.template.render_html('custom.html', {'action': 'play'})
        ctrl = controllers.HelloWorldController()

        mox.ReplayAll()
        try:
            ctrl.custom_page('play')
            mox.VerifyAll()
        finally:
            mox.UnsetStubs()

    def test_custom_page_passes_work_action(self):
        mox = Mox()

        mox.StubOutWithMock(controllers, 'template')
        controllers.template.render_html('custom.html', {'action': 'work'})
        ctrl = controllers.HelloWorldController()

        mox.ReplayAll()
        try:
            ctrl.custom_page('work')
            mox.VerifyAll()
        finally:
            mox.UnsetStubs()

    def test_custom_page_returns_invalid_action(self):
        ctrl = controllers.HelloWorldController()

        got = ctrl.custom_page('blabla')
        assert_equals(got, 'Invalid action: blabla')

class TestAjaxController:
    def test_get_ajax_time_returns_date(self):
        mox = Mox()

        mox.StubOutWithMock(controllers, 'datetime')

        dt_mock = mox.CreateMockAnything()
        controllers.datetime.now().AndReturn(dt_mock)

        dt_mock.strftime('%Y-%m-%d').AndReturn('should-be-date')
        ctrl = controllers.AjaxController()

        mox.ReplayAll()
        try:
            expected_return = '{"time": "should-be-date"}'
            got = ctrl.get_ajax_time('date')
            assert_equals(got, expected_return)
            mox.VerifyAll()
        finally:
            mox.UnsetStubs()

    def test_get_ajax_time_returns_time(self):
        mox = Mox()

        mox.StubOutWithMock(controllers, 'datetime')

        dt_mock = mox.CreateMockAnything()
        controllers.datetime.now().AndReturn(dt_mock)

        dt_mock.strftime('%H:%M:%S').AndReturn('should-be-time')
        ctrl = controllers.AjaxController()

        mox.ReplayAll()
        try:
            expected_return = '{"time": "should-be-time"}'
            got = ctrl.get_ajax_time('time')
            assert_equals(got, expected_return)
            mox.VerifyAll()
        finally:
            mox.UnsetStubs()

    def test_get_ajax_time_returns_date_and_time(self):
        mox = Mox()

        mox.StubOutWithMock(controllers, 'datetime')

        dt_mock = mox.CreateMockAnything()
        controllers.datetime.now().AndReturn(dt_mock)

        dt_mock.strftime('%Y-%m-%d - %H:%M:%S'). \
                AndReturn('should-be-date-and-time')
        ctrl = controllers.AjaxController()

        mox.ReplayAll()
        try:
            expected_return = '{"time": "should-be-date-and-time"}'
            got = ctrl.get_ajax_time('date_and_time')
            assert_equals(got, expected_return)
            mox.VerifyAll()
        finally:
            mox.UnsetStubs()

    def test_get_ajax_time_returns_bad_request_on_wrong_parameter(self):
        mox = Mox()

        mox.StubOutWithMock(controllers, 'datetime')

        controllers.datetime.now()

        ctrl = controllers.AjaxController()

        mox.ReplayAll()
        try:
            expected_return = 'invalid format, should be in: date, date_and_time, time'
            got = ctrl.get_ajax_time('any')
            assert_equals(cherrypy.response.status, 400)
            assert_equals(got, expected_return)
            mox.VerifyAll()
        finally:
            mox.UnsetStubs()
