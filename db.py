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

import yaml
import cherrypy
from os.path import dirname, abspath, join
from sponge.core import ConfigValidator, SpongeConfig

current_dir = abspath(dirname(__file__))
settings_path = join(current_dir, 'settings.yml')
yml = yaml.load(open(settings_path).read())

SpongeConfig(cherrypy.config, ConfigValidator(yml)).setup_all(current_dir)

from hacklab.models import *
from hacklab.models.meta import get_engine
from hacklab.models.base import metadata

engine = get_engine(echo=True)

def create_all():
    metadata.create_all(engine)

def drop_all():
    metadata.drop_all(engine)
