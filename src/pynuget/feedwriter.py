# -*- coding: utf-8 -*-
"""
"""

class FeedWriter(object):

    def __init__(self, id_):
        self.feed_id = id_
        self.base_url = 'TBD'

    def write(self):
        raise NotImplementedError

    def write_to_output(self):
        raise NotImplementedError

    def begin_feed(self):
        raise NotImplementedError

    def add_entry(self):
        raise NotImplementedError

    def add_entry_meta(self):
        raise NotImplementedError

    def render_meta_boolean(self):
        raise NotImplementedError

    def format_date(self):
        raise NotImplementedError

    def render_dependencies(self):
        raise NotImplementedError

    def format_target_framework(self):
        raise NotImplementedError

    def add_with_attributes(self):
        raise NotImplementedError

    def add_meta(self):
        raise NotImplementedError
