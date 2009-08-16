# -*- coding: utf-8 -*-
import yaml
import cherrypy
from os.path import dirname, abspath, join
from hacklab.controllers import HackLab
from sponge.core import ConfigValidator, SpongeConfig

current_dir = abspath(dirname(__file__))
root_dir = join(current_dir, '..', '..')
settings_path = join(root_dir, 'settings.yml')
yml = yaml.load(open(settings_path).read())

SpongeConfig(cherrypy.config, ConfigValidator(yml)).setup_all(root_dir)

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
