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

import os
import md5
import sha
import uuid
import string
import shutil
import cleese
import cherrypy

from sponge.core.io import FileSystem
from sponge.helpers import slugify
from sponge import template

from hacklab.models import meta


ENTRY_TEMPLATE = string.Template(u'command="hacklab-verify ${repos}",' \
                                 'no-port-forwarding,' \
                                 'no-X11-forwarding,' \
                                 'no-agent-forwarding,' \
                                 'no-pty ${key}')

class ObjectNotFound(Exception):
    pass

class Repository(object):
    NotFound = ObjectNotFound
    fs = FileSystem()

    def as_dict(self):
        items = {}
        for attrname in dir(self):
            if attrname.startswith("_"):
                continue

            attr = getattr(self, attrname)
            if isinstance(attr, (basestring, int, float)):
                items[attrname] = attr
            if isinstance(attr, list):
                items[attrname] = [x.as_dict() for x in attr]

        return items

    @classmethod
    def create(cls, **kwargs):
        instance = cls()
        for k,v in kwargs.items():
            setattr(instance, k, v)

        instance.save()
        return instance

    def delete(self):
        session = meta.get_session()
        session.query(self.__class__).filter_by(id=self.id,
                                                uuid=self.uuid).delete()

    def save(self):
        if not self.uuid:
            self.uuid = unicode(uuid.uuid4())

        session = meta.get_session()

        if session.object_session(self):
            session = session.object_session(self)
            session.expunge(self)

        session.add(self)

class UserRepository(Repository):
    class WrongPassword(Exception):
        pass

    def add_public_key(self, description, data):
        PublicKey = meta.get_model('PublicKey')
        key = PublicKey(owner=self,
                        description=unicode(description),
                        data=unicode(data))
        key.save()
        self.update_authorized_keys()
        return key

    def create_repository(self, name, description):
        GitRepository = meta.get_model('GitRepository')

        title = unicode(name)
        repo = GitRepository(name=title,
                             slug=slugify(title),
                             description=unicode(description),
                             owner=self)
        repo.save()

        return repo

    def get_repository_dir(self, name=''):
        root = cherrypy.config['sponge.root']
        repo_dir = cherrypy.config['sponge.extra']['repositories-dir']
        repository_base = self.fs.join(root, repo_dir)
        base = self.fs.abspath(self.fs.join(repository_base,
                                            self.username))
        if name:
            return self.fs.join(base, "%s.git" % name)
        return base

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

    @property
    def total_of_keys(self):
        cls = meta.get_model('PublicKey')
        session = meta.get_session()
        total = session.query(cls).filter_by(owner=self).count()
        return total

    def save(self):
        if not self.password.startswith("hash:"):
            self.password = self.make_hashed_password(self.email,
                                                      self.password)

        super(UserRepository, self).save()
        repodir = self.get_repository_dir()
        if not self.fs.exists(repodir):
            self.fs.mkdir(repodir)

        self.update_authorized_keys()

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

    @classmethod
    def update_authorized_keys(cls):
        temp_filename = "/tmp/hacklab.%s.keys" % unicode(uuid.uuid4())
        temp_file = FileSystem.open(temp_filename, 'w')
        session = meta.get_session()
        users = session.query(cls).all()
        data = []
        for user in users:
            for key in user.keys:
                row = ENTRY_TEMPLATE.substitute({'repos': user.username,
                                                 'key': key.data})
                data.append(row)

        temp_file.write("\n".join(data))
        temp_file.close()
        shutil.copy(temp_filename,
                    os.path.expanduser('~/.ssh/authorized_keys'))
        os.remove(temp_filename)

class GitRepoRepository(Repository):
    def get_permalink(self):
        return template.make_url('/user/%s/%s' % (self.owner.username,
                                                  self.slug))

    def save(self):
        if not self.slug:
            self.slug = slugify(self.name)

        super(GitRepoRepository, self).save()
        repodir = self.owner.get_repository_dir(self.slug)
        if not self.fs.exists(repodir):
            self.fs.mkdir(repodir)

        self.fs.pushd(repodir)
        exe = cleese.Executer('git init --bare')
        exe.execute()

        self.fs.popd()
