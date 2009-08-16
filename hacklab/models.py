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

from elixir import Entity, ManyToOne, OneToMany, Field
from elixir import Unicode, Integer, Boolean
from elixir import metadata, setup_all

class Repository(Entity):
    id = Field(Integer, primary_key=True)
    name = Field(Unicode)
    being_updated = Field(Boolean)
    is_ready = Field(Boolean)
    path = Field(Unicode)
    owner = OneToMany('User')

    def __repr__(self):
        return "<Repository at '%s'>" % self.path

class User(Entity):
    id = Field(Integer, primary_key=True)
    name = Field(Unicode)
    email = Field(Unicode)
    password = Field(Unicode)
    repositories = ManyToOne(Repository)

    def __repr__(self):
        return "<User '%s'>" % self.user

metadata.bind = "sqlite:///database_hacklab.sqlite"
setup_all()
