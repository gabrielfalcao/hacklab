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

from cherrypy import config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoped_session

__session__ = None
__engine__ = None
_MODELS = {}

class UndefinedModel(Exception):
    pass

def get_model(name):
    try:
        return _MODELS[name]
    except KeyError:
        raise UndefinedModel, "The model %s does not exist, " \
              "perharps it hasn't been imported" % name

def get_engine(**kw):
    engine_string = config['sponge.extra']['database-engine']
    __engine__ = create_engine(engine_string, **kw)
    return __engine__

def get_session():
    global __session__
    if not __session__:
        engine = get_engine()
        __session__ = scoped_session(sessionmaker(bind=engine))
    return __session__()
