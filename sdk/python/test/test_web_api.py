"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from __future__ import print_function

import unittest

from jemu.jemu_web_api import JemuWebApi, UnInitializedError


class TestWebApi(unittest.TestCase):
    def setUp(self):
        self.api = JemuWebApi()

    def tearDown(self):
        pass

    def test_init(self):
        self.assertIsNotNone(self.api._user_uid)

    def test_uninit_upload_file(self):
        self.api._user_uid = None
        with self.assertRaises(UnInitializedError):
            self.api.upload_file('test_file', b'SOME_BINARY_DATA')

    def test_upload_file(self):
        self.api.upload_file('test_file.bin', b'SOME_BINARY_DATA')
