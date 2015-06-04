#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
import app
import re


class IntegrationTestCase(unittest.TestCase):

    def runTest(self):
        tests = [{'url': 'http://bash.im/quote/3121', 'parse': 'Auto'},
                 {'url': 'http://lenta.ru/news/2015/05/28/ukrdebtact/',
                     'parse': 'lenta.ru'},
                 {'url': 'http://lenta.ru/news/2015/05/28/gazprom_isk/',
                     'parse': 'Auto'},
                 {'url': 'http://www.e1.ru/news/spool/news_id-424387-section_id-11.html',
                     'parse': 'e1.ru'},
                 {'url': 'http://www.e1.ru/news/spool/news_id-424428.html',
                  'parse': 'Auto'}, ]
        for test in tests:
            u = app.Uploader(test['url'])
            s = app.Scheme(test['parse'], u.domain())
            p = app.Parser(u.get(), s.scheme())
            f = app.Formater(p.parse())
            r = f.format()
            result = re.sub(r'\s+', ' ', r['text'])
            #result = f.format()
            print r['title']
            print result
            self.assertTrue(len(result) > 0)


class ConnectionErrorTestCase(unittest.TestCase):

    def runTest(self):
        tests = [
            {'url': 'http://bash1234.im/quote/3121', 'parse': '//div[@class="text"]'}, ]
        for test in tests:
            u = app.Uploader(test['url'])
            self.assertTrue(len(u.get()) == 0)


class UnknownSiteTestCate(unittest.TestCase):

    def runTest(self):
        tests = [{'url': 'http://ura.ru/articles/1036264964', 'parse': 'Auto'},
                 {'url': 'http://66.ru/bank/news/172774/', 'parse': 'Auto'},
                 {'url': 'https://news.mail.ru/politics/22223590/',
                     'parse': 'Auto'},
                 {'url': 'http://lifenews.ru/news/154988', 'parse': 'Auto'},
                 {'url': 'http://www.gazeta.ru/social/2015/06/02/6742709.shtml', 'parse': 'Auto'}]
        for test in tests:
            u = app.Uploader(test['url'])
            s = app.Scheme(test['parse'], u.domain())
            p = app.Parser(u.get(), s.scheme())
            f = app.Formater(p.parse())
            r = f.format()
            print r['title']
            result = r['text']
            #print result
            self.assertTrue(len(result) > 0)


if __name__ == '__main__':
    unittest.main()
