# -*- coding: utf-8 -*-
from syrinx.models import (AdminUser, Followee, Follower, List, LocalUser,
    Notice, PrivateNotice, RemoteUser, TwitterUser, User, UserConfig,)

import unittest2 as unittest


class UserTest(unittest.TestCase):
    """Tests for the User object.
    """

    def test_user(self):
        tuxie = User(username='tuxie', location=u'Montevideo, UY')
        tuxie.save()

    def test_remote_user(self):
        tuxie = RemoteUser(username='tuxie', server='identi.ca',
                           name=u'Alvaro Mouriño')
        tuxie.save()

    def test_local_user(self):
        tuxie = LocalUser(username='tuxie', password='passwd',
                          first_name=u'Alvaro', last_name=u'Mouriño',
                          email='alvaro@mourino.net',
                          web='http://alvaro.com.uy')
        tuxie.save()

    def test_user_config(self):
        conf = UserConfig()
        conf.save()

    def test_admin_user(self):
        tuxie = LocalUser(username='tuxie', password='passwd',
                          first_name=u'Alvaro', last_name=u'Mouriño',
                          email='alvaro@mourino.net',
                          web='http://alvaro.com.uy')
        tuxie.save()
        admin = AdminUser(user=tuxie, is_root=True)
        admin.save()

    def test_twitter_user(self):
        twitter = TwitterUser(username='syrinx', password='5yr1nX')
        twitter.save()

    def test_follow(self):
        tuxie = LocalUser(username='tuxie', password='passwd',
                          first_name=u'Alvaro', last_name=u'Mouriño',
                          email='alvaro@mourino.net',
                          web='http://alvaro.com.uy')
        tuxie.save()
        omar = LocalUser(username='omar', password='passwd',
                          first_name=u'Omar', last_name=u'Gutiérrez',
                          email='omar@gmail.com')
        omar.save()
        niko = RemoteUser(username='nikola', server='twitter.com',
                          name=u'Nikola Šarčević')
        niko.save()
        anon = LocalUser(username='anon', password='passwd',
                         first_name=u'Anonymous', email='anon@mailinator.com')
        anon.save()
        wiki = RemoteUser(username='wikileaks', server='identi.ca',
                          name=u'Wikileaks')
        wiki.save()

        # tuxie.following.add(omar)
        # tuxie.following['%s@%s' % (omar.username, omar.server)] = omar
        tuxie.add_following(omar)
        tuxie.add_following(niko)
        tuxie.add_following(anon)
        tuxie.add_following(wiki)
        tuxie.add_following(wiki)

        anon.add_following(omar)

        wiki.add_following(tuxie)

    def test_list(self):
        tuxie = LocalUser(username='tuxie', password='passwd',
                          first_name=u'Alvaro', last_name=u'Mouriño',
                          email='alvaro@mourino.net',
                          web='http://alvaro.com.uy')
        tuxie.save()
        omar = LocalUser(username='omar', password='passwd',
                          first_name=u'Omar', last_name=u'Gutiérrez',
                          email='omar@gmail.com')
        omar.save()
        niko = RemoteUser(username='nikola', server='twitter.com',
                          name=u'Nikola Šarčević')
        niko.save()
        userlist = List(name='millencolin', members=[tuxie, omar, niko])
        userlist.save()

    def test_notice(self):
        notice1 = Notice(content=u'Hello')
        notice2 = Notice(content=u'Hallo')
        notice3 = Notice(content=u'Hola')
        tuxie = LocalUser(username='tuxie', password='passwd',
                          first_name=u'Alvaro', last_name=u'Mouriño',
                          email='alvaro@mourino.net',
                          web='http://alvaro.com.uy',
                          notices=[notice1, notice2])
        tuxie.save()
        tuxie.notices.add(notice3)

    def test_private_notice(self):
        pass


if __name__ == '__main__':
    unittest.main()
