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
from uuid import uuid4
from sqlalchemy import MetaData, Column, Integer, Unicode
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.ext.declarative import declarative_base

from hacklab.models import meta

metadata = MetaData()

class MetaBaseModel(DeclarativeMeta):
    def __init__(cls, classname, bases, dict_):
        dict_['id'] = Column(Integer, primary_key=True)
        dict_['uuid'] = Column(Unicode, unique=True)
        return DeclarativeMeta.__init__(cls, classname, bases, dict_)

class BaseModel(object):
    def save(self):
        self.uuid = unicode(uuid4())
        Session = meta.get_session()
        session = Session()
        session.add(self)
        session.commit()
        session.flush()

Model = declarative_base(cls=BaseModel,
                         metadata=metadata,
                         metaclass=MetaBaseModel)
