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
import uuid
import cherrypy

from sponge.core.io import FileSystem
from hacklab.models import meta

class ObjectNotFound(Exception):
    pass

class Repository(object):
    NotFound = ObjectNotFound
    fs = FileSystem()
    @classmethod
    def create(cls, **kwargs):
        instance = cls()
        for k,v in kwargs.items():
            setattr(instance, k, v)

        instance.save()
        return instance

    def save(self):
        if not self.uuid:
            self.uuid = unicode(uuid.uuid4())

        session = meta.get_session()
        session.add(self)
        session.commit()

class UserRepository(Repository):
    class WrongPassword(Exception):
        pass

    def add_public_key(self, description, data):
        PublicKey = meta.get_model('PublicKey')
        self.keys.append(PublicKey(description=unicode(description),
                                   data=unicode(data)))
        self.save()

    def get_repository_dir(self):
        root = cherrypy.config['sponge.root']
        repo_dir = cherrypy.config['sponge.extra']['repositories-dir']
        repository_base = self.fs.join(root, repo_dir)
        return self.fs.abspath(self.fs.join(repository_base,
                                            self.username))

    def get_gravatar(self):
        md5_email = md5.new(self.email).hexdigest()
        return 'http://www.gravatar.com/avatar/%s.jpg' % md5_email

    @classmethod
    def make_hashed_password(cls, email, password):
        base = "%s+%s" % (email, password)
        return u"hash:%s" % sha.new(base).hexdigest()

    @property
    def total_of_repositories(self):
        cls = meta.get_model('GitRepository')
        session = meta.get_session()
        total = session.query(cls).filter_by(owner=self).count()
        return total

    def save(self):
        if not self.password.startswith("hash:"):
            self.password = self.make_hashed_password(self.email,
                                                      self.password)

        super(UserRepository, self).save()
        repodir = self.get_repository_dir()
        # after having a uuid, then
        if not self.fs.exists(repodir):
            self.fs.mkdir(repodir)

    @classmethod
    def authenticate(cls, email, password):
        session = meta.get_session()
        user = session.query(cls).filter_by(email=unicode(email)).first()

        if not user:
            raise cls.NotFound, \
                  'User with email %s is not yet registered' % email

        password = cls.make_hashed_password(email, password)

        if user.password == password:
            return user
        else:
            raise cls.WrongPassword, 'The password is wrong'
