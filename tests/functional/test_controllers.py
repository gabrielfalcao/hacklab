# -*- coding: utf-8 -*-
import yaml
import cherrypy
from os.path import dirname, abspath, join
from hacklab.controllers import HelloWorldController
from sponge.core import ConfigValidator, SpongeConfig

current_dir = abspath(dirname(__file__))
root_dir = join(current_dir, '..', '..')
settings_path = join(root_dir, 'settings.yml')
yml = yaml.load(open(settings_path).read())

SpongeConfig(cherrypy.config, ConfigValidator(yml)).setup_all(root_dir)

class TestHelloWorldController:
    def test_index_renders_some_congratulations(self):
        ctrl = HelloWorldController()
        html = ctrl.index()

        assert 'Congratulations!' in html, "The html rendered by " \
               "HelloWorldController's should have some " \
               "congratulation message."
