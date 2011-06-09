# -*- coding: utf-8 -*-
from syrinx.models import (AdminUser, LocalUser, Notice, PrivateNotice,
    RemoteUser, TwitterUser, User, UserConfig, UserList)

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
        config = UserConfig(protected=False, email_notification=True)
        tuxie = LocalUser(username='tuxie', password='passwd',
                          first_name=u'Alvaro', last_name=u'Mouriño',
                          email='alvaro@mourino.net',
                          web='http://alvaro.com.uy', user_config=config)
        tuxie.save()

    def test_admin_user(self):
        admin = AdminUser(is_root=True)
        tuxie = LocalUser(username='tuxie', password='passwd',
                          first_name=u'Alvaro', last_name=u'Mouriño',
                          email='alvaro@mourino.net',
                          web='http://alvaro.com.uy', user_admin=admin)
        tuxie.save()

    def test_twitter_user(self):
        twitter = TwitterUser(username='syrinx', password='5yr1nX')
        tuxie = LocalUser(username='tuxie', password='passwd',
                          first_name=u'Alvaro', last_name=u'Mouriño',
                          email='alvaro@mourino.net',
                          web='http://alvaro.com.uy', twitter_user=twitter)
        tuxie.save()

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
        # tuxie.add_following(omar)
        tuxie.follow(omar)
        tuxie.follow(niko)
        tuxie.follow(anon)
        tuxie.follow(wiki)
        tuxie.follow(wiki)

        anon.follow(omar)

        wiki.follow(tuxie)

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
        userlist = UserList(name='millencolin')
        tuxie.add_list(userlist)
        tuxie.add_to_list(userlist, omar)
        tuxie.add_to_list(userlist, niko)

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
        tuxie.post_notice(notice3)

    def test_private_notice(self):
        tuxie = LocalUser(username='tuxie', password='passwd',
                          first_name=u'Alvaro', last_name=u'Mouriño',
                          email='alvaro@mourino.net',
                          web='http://alvaro.com.uy')
        tuxie.save()
        niko = RemoteUser(username='nikola', server='twitter.com',
                          name=u'Nikola Šarčević')
        niko.save()
        notice1 = PrivateNotice(content=u'Hello', recipient=niko)
        notice2 = PrivateNotice(content=u'Hallo', recipient=niko)
        tuxie.send_private_notice(notice1)
        tuxie.send_private_notice(notice2)


if __name__ == '__main__':
    unittest.main()
