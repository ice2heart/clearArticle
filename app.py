#!/usr/bin/env python
# -*- coding: utf-8 -*-
# need cssselect, lxml, requests

lenta_class = 'b-text'

import requests
import lxml.html as html
from lxml.html.clean import clean_html
import argparse
from urlparse import urlparse
import os
import codecs
import json


def perror(text):
    print('[ERROR] : ' + text)


def pinfo(text):
    print('[INFO] : ' + text)


def argParser():

    parser = argparse.ArgumentParser(description=u"Симплификатор статей %(prog)s",
                                     epilog=u"Эпилог программы %(prog)s")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help=u"Выводить подробное описание действий", default=False)
    parser.add_argument('url',
                        help='Article URL',)
    parser.add_argument('--parser', '-p',
                        help=u'Тип парсера для сайта', default='Auto')
    return parser.parse_args()


class Uploader():

    """docstring for Uploader"""

    def __init__(self, url):
        self.url = url

    def domain(self):
        parsed_uri = urlparse(self.url)
        domain = parsed_uri.netloc
        if domain.startswith('www.'):
            domain = domain[4:]
        return domain

    def path(self):
        parsed_uri = urlparse(self.url)
        path = '/%s%s' % (parsed_uri.netloc, parsed_uri.path)
        pinfo(path)
        return path

    def get(self):
        try:
            request = requests.get(self.url)
        except Exception, error:
            perror(str(error))
            return ''
        if request.url == 'http://bash.im/':
            perror('its main page')
            return ''
        if request.status_code is not 200:
            perror('status code is not 200: %s' % request.status_code)
            return ''
        pinfo('Request info code %d reason %s, url %s' % (request.status_code,
                                                          request.reason, request.url))
        return clean_html(request.text)


class Scheme():

    def __init__(self, name, url):
        self.name = name
        self.url = url
        with open('schemes.json') as in_file:
            self.schemes = json.load(in_file)

    def scheme(self):
        if self.name == 'Auto':
            if self.url in self.schemes:
                param = self.schemes[self.url]
                return param
            else:
                return {'type': 'xpath', 'param': '//p',
                        'title_type': 'xpath', 'title_param': '//h1'}
        if self.name in self.schemes:
            pinfo('find in domain name')
            return self.schemes[self.name]
        perror('unknown scheme for site ' + self.url)


class Parser:

    """docstring for Parser """

    def __init__(self, data, extractor):
        self.data = data
        self.extractor = extractor

    def parse(self):
        page = html.document_fromstring(self.data)
        raw_text = ''
        if self.extractor['type'] == 'xpath':
            bloks = page.xpath(self.extractor['param'])

        for div in bloks:
            raw_text += div.text_content()
            for ch in div:
                if ch.tag == 'a':
                    raw_text += ' [%s] ' % ch.get('href')
        raw_text = raw_text.strip(' \t\r\n')

        title = ''
        if self.extractor['title_type'] == 'xpath':
            bloks = page.xpath(self.extractor['title_param'])

        for blok in bloks:
            title += blok.text_content()
        return {'text': raw_text, 'title': title}


class Formater:

    """docstring for Formater"""

    def __init__(self, raw_text):
        self.raw_text = raw_text

    def format(self):
        format_text = ''
        for line in self.raw_text['text'].split('\n'):
            words = line.split()
            line = ''
            for word in words:
                if len(line) + len(word) <= 80:
                    line += word + ' '
                else:
                    format_text += line + '\n'
                    line = word + ' '
            format_text += line + '\n\n'
        self.raw_text['text'] = format_text
        return self.raw_text


class Saver:

    def __init__(self, format_text, path):
        self.text = format_text
        self.path = path

    def make_path(self):
        path_parts = self.path.split('/')
        if len(path_parts[-1]) is 0:
            self.path += 'page'
        dir_path = os.getcwd() + '/'.join(path_parts[0:-1])
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    def save(self):
        self.make_path()
        with codecs.open(os.getcwd() + self.path + '.txt', 'w', 'utf-8') as out_file:
            out_line = u'%(title)s\n\n%(text)s' % self.text
            out_file.write(out_line)


def main():
    options = argParser()
    uploader = Uploader(options.url)
    scheme = Scheme(options.parser, uploader.domain())
    parser = Parser(uploader.get(), scheme.scheme())
    formater = Formater(parser.parse())
    saver = Saver(formater.format(), uploader.path())
    saver.save()

if __name__ == "__main__":
    main()
