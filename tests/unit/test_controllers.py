# -*- coding: utf-8 -*-

from mox import Mox
from nose.tools import assert_equals
from hacklab import controllers

class TestHackLab:
    def test_index_calls_render_html(self):
        mox = Mox()

        mox.StubOutWithMock(controllers, 'template')

        controllers.template.render_html('index.html'). \
                    AndReturn('supposed-to-be-the-rendered-html')

        ctrl = controllers.HackLabController()

        mox.ReplayAll()
        try:
            expected_return = 'supposed-to-be-the-rendered-html'
            got = ctrl.index()
            assert_equals(got, expected_return)
            mox.VerifyAll()
        finally:
            mox.UnsetStubs()
