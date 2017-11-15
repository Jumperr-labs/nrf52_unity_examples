"""
:copyright: (c) 2017 by Jumper Labs Ltd.
:license: Apache 2.0, see LICENSE.txt for more details.
"""
from __future__ import print_function

import os
import sys
from time import sleep
import calendar
import time
import requests
import logging

API_URL = os.environ['JUMPER_API'] if 'JUMPER_API' in os.environ \
    else 'https://us-central1-jemu-web-app.cloudfunctions.net/api/v1'


class AuthorizationError(Exception):
    pass


class UnInitializedError(Exception):
    pass


class JemuWebApi(object):
    def __init__(self, jumper_token=None, api_url=API_URL):
        self._api_url = api_url
        self._token = jumper_token or os.environ['JUMPER_TOKEN']
        self._headers = {'Authorization': 'Bearer ' + self._token}
        self._user_uid = None
        self.init()

    def init(self):
        logging.getLogger("requests").setLevel(logging.WARNING)
        res = requests.get(self._api_url + '/hello', headers=self._headers)
        try:
            res.raise_for_status()
        except requests.HTTPError as e:
            if res.status_code == requests.codes['unauthorized']:
                raise AuthorizationError
            else:
                raise e

        self._user_uid = res.json()['userUid']

    def upload_file(self, filename, data):
        if self._user_uid is None:
            raise UnInitializedError

        headers = self._headers
        headers['Content-Type'] = 'application/octet-stream'
        res = requests.post(
            '{}/firmwares/{}/{}'.format(self._api_url, self._user_uid, filename),
            data=data,
            headers=headers
        )
        res.raise_for_status()

    def check_status(self, filename):
        if self._user_uid is None:
            raise UnInitializedError

        headers = self._headers
        headers['Content-Type'] = 'application/text'
        res = requests.get(
            '{}/firmwares/{}/{}/status'.format(self._api_url, self._user_uid, filename),
            headers=headers
        )
        return res

    def download_jemu(self, filename, local_filename):
        if self._user_uid is None:
            raise UnInitializedError

        headers = self._headers
        headers['Content-Type'] = 'application/octet-stream'
        res = requests.get(
            '{}/firmwares/{}/{}'.format(self._api_url, self._user_uid, filename),
            headers=headers)
        
        res = requests.get(res.text)

        with open(local_filename, 'wb') as f:
            for chunk in res.iter_content(chunk_size=1024): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    
        return True

    def create_emulator(self, fw_filename, fw_bin_data, dest):
        fw_filename = str(int(calendar.timegm(time.gmtime()))) + '_' + fw_filename
        self.upload_file(fw_filename, fw_bin_data)

        sys.stdout.write('Loading virtual device')
        sys.stdout.flush()
        status = 'Queded'
        while (status != 'Done'):
            status = self.check_status(fw_filename).text
            sys.stdout.write('.')
            sys.stdout.flush()
            sleep(0.25)
        
        sys.stdout.write(' Done\n')
        sys.stdout.flush()

        jemu_filename = os.path.splitext(fw_filename)[0]+'.jemu'

        self.download_jemu(jemu_filename, dest)

        # dest_st = os.stat(dest)
        os.chmod(dest, 0o777)