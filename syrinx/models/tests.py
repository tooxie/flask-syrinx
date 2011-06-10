# -*- coding: utf-8 -*-
from syrinx import app
from syrinx.models import (AdminUser, LocalUser, Notice, PrivateNotice,
    RemoteUser, TwitterUser, User, UserConfig, UserList)

import unittest2 as unittest


class ModelTestsBase:
    """Testing models.
    """

    def get_backend(self):
        return self.BACKEND

    def test_user(self):
        tuxie = User(username='tuxie', location=u'Montevideo, UY')
        tuxie.save(backend=self.get_backend())

    def test_remote_user(self):
        tuxie = RemoteUser(username='tuxie', server='identi.ca',
                           name=u'Alvaro Mouriño')
        tuxie.save(backend=self.get_backend())

    def test_local_user(self):
        tuxie = LocalUser(username='tuxie', password='passwd',
                          first_name=u'Alvaro', last_name=u'Mouriño',
                          email='alvaro@mourino.net',
                          web='http://alvaro.com.uy')
        tuxie.save(backend=self.get_backend())

    def test_user_config(self):
        config = UserConfig(protected=False, email_notification=True)
        tuxie = LocalUser(username='tuxie', password='passwd',
                          first_name=u'Alvaro', last_name=u'Mouriño',
                          email='alvaro@mourino.net',
                          web='http://alvaro.com.uy', user_config=config)
        tuxie.save(backend=self.get_backend())

    def test_admin_user(self):
        admin = AdminUser(is_root=True)
        tuxie = LocalUser(username='tuxie', password='passwd',
                          first_name=u'Alvaro', last_name=u'Mouriño',
                          email='alvaro@mourino.net',
                          web='http://alvaro.com.uy', user_admin=admin)
        tuxie.save(backend=self.get_backend())

    def test_twitter_user(self):
        twitter = TwitterUser(username='syrinx', password='5yr1nX')
        tuxie = LocalUser(username='tuxie', password='passwd',
                          first_name=u'Alvaro', last_name=u'Mouriño',
                          email='alvaro@mourino.net',
                          web='http://alvaro.com.uy', twitter_user=twitter)
        tuxie.save(backend=self.get_backend())

    def test_follow(self):
        tuxie = LocalUser(username='tuxie', password='passwd',
                          first_name=u'Alvaro', last_name=u'Mouriño',
                          email='alvaro@mourino.net',
                          web='http://alvaro.com.uy')
        tuxie.save(backend=self.get_backend())
        omar = LocalUser(username='omar', password='passwd',
                          first_name=u'Omar', last_name=u'Gutiérrez',
                          email='omar@gmail.com')
        omar.save(backend=self.get_backend())
        niko = RemoteUser(username='nikola', server='twitter.com',
                          name=u'Nikola Šarčević')
        niko.save(backend=self.get_backend())
        anon = LocalUser(username='anon', password='passwd',
                         first_name=u'Anonymous', email='anon@mailinator.com')
        anon.save(backend=self.get_backend())
        wiki = RemoteUser(username='wikileaks', server='identi.ca',
                          name=u'Wikileaks')
        wiki.save(backend=self.get_backend())

        # tuxie.following.add(omar)
        # tuxie.following['%s@%s' % (omar.username, omar.server)] = omar
        # tuxie.add_following(omar)
        tuxie.follow(omar, backend=self.get_backend())
        tuxie.follow(niko, backend=self.get_backend())
        tuxie.follow(anon, backend=self.get_backend())
        tuxie.follow(wiki, backend=self.get_backend())
        tuxie.follow(wiki, backend=self.get_backend())

        anon.follow(omar, backend=self.get_backend())

        # Remote users lack 'follow' method.
        self.assertFalse(callable(getattr(wiki, 'follow', None)))

    def test_list(self):
        tuxie = LocalUser(username='tuxie', password='passwd',
                          first_name=u'Alvaro', last_name=u'Mouriño',
                          email='alvaro@mourino.net',
                          web='http://alvaro.com.uy')
        tuxie.save(backend=self.get_backend())
        omar = LocalUser(username='omar', password='passwd',
                          first_name=u'Omar', last_name=u'Gutiérrez',
                          email='omar@gmail.com')
        omar.save(backend=self.get_backend())
        niko = RemoteUser(username='nikola', server='twitter.com',
                          name=u'Nikola Šarčević')
        niko.save(backend=self.get_backend())
        userlist = UserList(name='millencolin')
        tuxie.add_list(userlist, backend=self.get_backend())
        tuxie.add_to_list(userlist, omar, backend=self.get_backend())
        tuxie.add_to_list(userlist, niko, backend=self.get_backend())

    def test_notice(self):
        notice1 = Notice(content=u'Hello')
        notice2 = Notice(content=u'Hallo')
        notice3 = Notice(content=u'Hola')
        tuxie = LocalUser(username='tuxie', password='passwd',
                          first_name=u'Alvaro', last_name=u'Mouriño',
                          email='alvaro@mourino.net',
                          web='http://alvaro.com.uy')
        tuxie.save(backend=self.get_backend())
        tuxie.post_notice(notice1, backend=self.get_backend())
        tuxie.post_notice(notice2, backend=self.get_backend())
        tuxie.post_notice(notice3, backend=self.get_backend())
        self.assertEquals(len(tuxie.notices), 3)

    def test_private_notice(self):
        tuxie = LocalUser(username='tuxie', password='passwd',
                          first_name=u'Alvaro', last_name=u'Mouriño',
                          email='alvaro@mourino.net',
                          web='http://alvaro.com.uy')
        tuxie.save(backend=self.get_backend())
        niko = RemoteUser(username='nikola', server='twitter.com',
                          name=u'Nikola Šarčević')
        niko.save(backend=self.get_backend())
        notice1 = PrivateNotice(content=u'Hello', recipient=niko)
        notice2 = PrivateNotice(content=u'Hallo', recipient=niko)
        tuxie.send_private_notice(notice1, backend=self.get_backend())
        tuxie.send_private_notice(notice2, backend=self.get_backend())
        self.assertEquals(len(tuxie.private_notices), 2)


# class ConsoleBackendTests(ModelTestsBase, unittest.TestCase):
#
#     BACKEND = 'syrinx.models.backends.console.ModelBackend'


class DummyBackendTests(ModelTestsBase, unittest.TestCase):

    BACKEND = 'syrinx.models.backends.dummy.ModelBackend'


if __name__ == '__main__':
    unittest.main()
