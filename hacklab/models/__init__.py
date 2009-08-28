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
import cherrypy

from sqlalchemy import Column, Unicode
from sqlalchemy import ForeignKey, Integer
from sqlalchemy.orm import relation, backref

from sponge.core.io import FileSystem
from hacklab.models.meta import get_session
from hacklab.models.base import Model
from hacklab.models import repositories as repo

class User(Model, repo.Repository):
    __tablename__ = 'users'
    name = Column(Unicode, nullable=False)
    username = Column(Unicode, nullable=False, unique=True)
    email = Column(Unicode, nullable=False, unique=True)
    password = Column(Unicode, nullable=False)

    fs = FileSystem()

    class WrongPassword(Exception):
        pass

    def add_public_key(self, description, data):
        self.keys.append(PublicKey(description=unicode(description),
                                   data=unicode(data)))
        self.save()

    def get_repository_dir(self):
        root = cherrypy.config['sponge.root']
        repo_dir = cherrypy.config['sponge.extra']['repositories-dir']
        repository_base = self.fs.abspath(self.fs.join(root, repo_dir))
        return self.fs.abspath(self.fs.join(repository_base, self.username))

    def get_gravatar(self):
        md5_email = md5.new(self.email).hexdigest()
        return 'http://www.gravatar.com/avatar/%s.jpg' % md5_email

    @classmethod
    def make_hashed_password(cls, email, password):
        base = "%s+%s" % (email, password)
        return u"hash:%s" % sha.new(base).hexdigest()

    def save(self, *args, **kw):
        if not self.password.startswith("hash:"):
            self.password = self.make_hashed_password(self.email,
                                                      self.password)

        super(User, self).save(*args, **kw)
        repodir = self.get_repository_dir()
        # after having a uuid, then
        if not self.fs.exists(repodir):
            self.fs.mkdir(repodir)

    @classmethod
    def authenticate(cls, email, password):
        Session = get_session()
        session = Session()
        user = session.query(cls).filter_by(email=unicode(email)).first()
        if not user:
            raise cls.NotFound, \
                  'User with email %s is not yet registered' % email

        password = cls.make_hashed_password(email, password)

        if user.password == password:
            return user
        else:
            raise cls.WrongPassword, 'The password is wrong'

    def __repr__(self):
        return "<User '%s'>" % self.name

class GitRepository(Model, repo.Repository):
    __tablename__ = 'repositories'
    name = Column(Unicode, nullable=False)
    description = Column(Unicode)
    slug = Column(Unicode, nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'))
    owner = relation(User, backref=backref('repositories', order_by=name))

    def __repr__(self):
        return "<GitRepository at '%s'>" % self.path

class PublicKey(Model, repo.Repository):
    __tablename__ = 'ssh_public_keys'
    description = Column(Unicode)
    data = Column(Unicode)
    user_id = Column(Integer, ForeignKey('users.id'))
    owner = relation(User, backref=backref('keys', order_by=description))

    def __repr__(self):
        return "<SSHPublicKey at '%s'>" % self.path

