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

from sqlalchemy import Column, Unicode
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import relation, backref

from hacklab.models.base import Model
from hacklab.models.repositories import Repository
from hacklab.models.repositories import UserRepository

class User(Model, UserRepository):
    __tablename__ = 'users'
    name = Column(Unicode, nullable=False)
    username = Column(Unicode, nullable=False, unique=True)
    email = Column(Unicode, nullable=False, unique=True)
    password = Column(Unicode, nullable=False)

    def __unicode__(self):
        return "<User '%s'>" % self.name

class GitRepository(Model, Repository):
    __tablename__ = 'repositories'
    name = Column(Unicode, nullable=False)
    description = Column(Unicode)
    slug = Column(Unicode, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    owner = relation(User, backref=backref('repositories', order_by=name))

    def __unicode__(self):
        return "<GitRepository at '%s'>" % self.path

class PublicKey(Model, Repository):
    __tablename__ = 'ssh_public_keys'
    description = Column(Unicode)
    data = Column(Unicode)
    user_id = Column(Integer, ForeignKey('users.id'))
    owner = relation(User, backref=backref('keys', order_by=description))

    def __unicode__(self):
        return "<SSHPublicKey at '%s'>" % self.path

