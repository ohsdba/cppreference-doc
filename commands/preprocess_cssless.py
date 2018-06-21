#   Copyright (C) 2018  Monika Kairaityte <monika@kibit.lt>
#
#   This file is part of cppreference-doc
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see http://www.gnu.org/licenses/.

from premailer import Premailer
import cssutils
from lxml import html
from lxml import etree
from io import StringIO
from lxml.etree import strip_elements
import logging
import os
import warnings
import io

def preprocess_html_merge_cssless(src_path, dst_path):
    with open(src_path, 'r') as a_file:
        content = a_file.read()
        parser = etree.HTMLParser()
        stripped = content.strip()
        root = etree.fromstring(stripped, parser)

    output = preprocess_html_merge_css(root, src_path)

    head = os.path.dirname(dst_path)
    os.makedirs(head, exist_ok=True)

    with open(dst_path, 'wb') as a_file:
        root.getroottree().write(a_file, pretty_print=True, method="html",
                                 encoding='utf-8')
    return output.getvalue()

def preprocess_html_merge_css(root, src_path):
    log = logging.Logger('ignore')
    output = io.StringIO()
    handler = logging.StreamHandler(stream=output)
    formatter = logging.Formatter('%(levelname)s, %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    # cssutils_logging_handler of Premailer.__init__ is insufficient to silence
    # warnings to stderr in non-verbose mode
    cssutils.log.setLog(log)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        premailer = Premailer(root, base_url=src_path,
                              disable_link_rewrites=True, remove_classes=True)
        root = premailer.transform().getroot()

    # completely remove content of style tags and tags
    nondata_tags = ['style']
    strip_elements(root, *nondata_tags)

    return output
