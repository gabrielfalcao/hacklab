# -*- coding: utf-8 -*-
from hacklab.controllers import HackLab

class TestHackLab:
    def test_index_renders_proper_javascript_includes(self):
        ctrl = HackLab()
        html = ctrl.index()

        expected = '<script src="/media/js/jquery.js" type="text/javascript"></script>\n' \
           '    <script src="/media/js/jquery.ui.js" type="text/javascript"></script>\n' \
           '    <script src="/media/js/jquery.lowpro.js" type="text/javascript"></script>\n' \
           '    <script src="/media/js/hacklab.js" type="text/javascript"></script>\n' \
           '    <script src="/media/js/hacklab.base.js" type="text/javascript"></script>'

        assert expected in html
