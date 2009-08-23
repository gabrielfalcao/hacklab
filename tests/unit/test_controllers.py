# -*- coding: utf-8 -*-
import cherrypy
from nose.tools import assert_raises
from hacklab import controllers

class TestHackLab:
    def test_index_calls_render_html(self):

        ctrl = controllers.HackLabController()
        assert_raises(cherrypy.HTTPRedirect, ctrl.index)
