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

from sqlalchemy import Column, Integer, Unicode
from hacklab.models.base import Model
from hacklab.models.repositories import Repository

# class GitRepository(Entity, Repository):
#     id = Field(Integer, primary_key=True)
#     name = Field(Unicode, required=True)
#     being_updated = Field(Boolean)
#     is_ready = Field(Boolean)
#     path = Field(Unicode, required=True)
#     owner = OneToMany('User', required=True)

#     def __repr__(self):
#         return "<GitRepository at '%s'>" % self.path

class User(Model, Repository):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(Unicode)
    email = Column(Unicode)
    password = Column(Unicode)

    def __repr__(self):
        return "<User '%s'>" % self.name
