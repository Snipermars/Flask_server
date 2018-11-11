# !/usr/bin/python3.5
# -*- coding: utf-8 -*-
"""
@ProjectDistribution:
@Time: 2018/11/1 14:49
@Author: Marus
@Function:Regex_class.py
"""

from werkzeug.routing import  BaseConverter
class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

