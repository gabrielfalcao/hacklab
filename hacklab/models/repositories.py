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
import re
import os
import md5
import sha
import time
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

def serializable(func_or_name=None):
    if isinstance(func_or_name, basestring):
        def wrap(func):
            func.serializable = func_or_name
            return func
        return wrap

    func_or_name.serializable = func_or_name.__name__
    return func_or_name

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
            if hasattr(attr, 'serializable'):
                items[attr.serializable] = apply(attr)

            if isinstance(attr, list):
                items[attrname] = [x.as_dict() for x in attr]

        return items

    @classmethod
    def get_by(cls, **kw):
        return cls.fetch_by(**kw).first()

    @classmethod
    def fetch_by(cls, **kw):
        session = meta.get_session()
        return session.query(cls).filter_by(**kw)

    @classmethod
    def create(cls, **kwargs):
        instance = cls()
        for k,v in kwargs.items():
            setattr(instance, k, v)

        instance.save()
        return instance

    def delete(self):
        session = meta.get_session()
        session.delete(self)

    def save(self):
        if not self.uuid:
            self.uuid = unicode(uuid.uuid4())

        session = meta.get_session()
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
        repo = GitRepository.create(
            name=title,
            slug=slugify(title),
            description=unicode(description),
            owner=self
        )

        return repo

    @serializable
    def get_repository_dir(self, name=''):
        root = cherrypy.config['sponge.root']
        repo_dir = cherrypy.config['sponge.extra']['repositories-dir']
        repository_base = self.fs.join(root, repo_dir)
        base = self.fs.abspath(self.fs.join(repository_base,
                                            self.username))
        if name:
            return self.fs.join(base, "%s.git" % name)
        return base

    @serializable
    def get_gravatar(self):
        md5_email = md5.new(self.email).hexdigest()
        return 'http://www.gravatar.com/avatar/%s.jpg' % md5_email

    @classmethod
    def make_hashed_password(cls, email, password):
        base = "%s+%s" % (email, password)
        return u"hash:%s" % sha.new(base).hexdigest()

    @property
    @serializable
    def total_of_repositories(self):
        cls = meta.get_model('GitRepository')
        session = meta.get_session()
        total = session.query(cls).filter_by(owner=self).count()
        return total

    @property
    @serializable
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
    @serializable
    def get_permalink(self):
        return template.make_url('/user/%s/%s' % (self.owner.username,
                                                  self.slug))
    @serializable
    def get_dir(self):
        return self.owner.get_repository_dir(self.slug)

    def _run_sync(self, command):
        exe = cleese.Executer(command)
        exe.execute()
        while not exe.poll():
            time.sleep(0.1)

        return exe.result.log.strip('\n')

    def list_dir(self, object_hash='HEAD', parent=None):
        data = self._run_sync('git ls-tree %s' % object_hash)
        return self.parse_data(data, parent=parent)

    def get_blob(self, object_hash):
        data = self._run_sync('git show %s' % object_hash)
        return data


    def parse_data(self, data, parent=None):
        d = []
        for line in data.splitlines():
            line = re.sub(r'\s+', ' ', line)
            mode, kind, ohash, name = line.split(" ")
            childs = kind == 'tree' and self.list_dir(ohash, parent=name) or {}
            if parent:
                url = os.path.join(parent, kind, name)
            else:
                url = os.path.join(kind, name)

            d.append(dict(mode=mode,
                          url=url,
                          parent_name=parent,
                          type=kind,
                          children=childs,
                          hash=ohash,
                          name=name))
        return d

    def save(self):
        if not self.slug:
            self.slug = slugify(self.name)

        super(GitRepoRepository, self).save()
        repodir = self.get_dir()
        if not self.fs.exists(repodir):
            self.fs.mkdir(repodir)

        self.fs.pushd(repodir)
        exe = cleese.Executer('git init --bare')
        exe.execute()

        self.fs.popd()
