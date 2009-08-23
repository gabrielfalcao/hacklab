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
import md5
import sha

from sqlalchemy import Column, Boolean, Unicode
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import relation, backref

from hacklab.models.base import Model
from hacklab.models import repositories as repo

class User(Model, repo.Repository):
    __tablename__ = 'users'
    name = Column(Unicode, nullable=False)
    email = Column(Unicode, nullable=False, unique=True)
    password = Column(Unicode, nullable=False)

    def get_gravatar(self):
        md5_email = md5.new(self.email).hexdigest()
        return 'http://www.gravatar.com/avatar/%s.jpg' % md5_email

    def save(self, *args, **kw):
        if not self.password.startswith("hash:"):
            base = "%s+%s" % (self.email, self.password)
            self.password = u"hash:%s" % sha.new(base).hexdigest()

        super(User, self).save(*args, **kw)

    def __repr__(self):
        return "<User '%s'>" % self.name

class GitRepository(Model, repo.Repository):
    __tablename__ = 'repositories'
    name = Column(Unicode, nullable=False)
    being_updated = Column(Boolean)
    is_ready = Column(Boolean)
    path = Column(Unicode, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    owner = relation(User, backref=backref('repositories', order_by=name))

    def __repr__(self):
        return "<GitRepository at '%s'>" % self.path

