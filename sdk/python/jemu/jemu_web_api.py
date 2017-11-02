from __future__ import print_function

import os

import requests

API_URL = 'https://us-central1-jemu-web-app.cloudfunctions.net/api'


class AuthorizationError(Exception):
    pass


class UnInitializedError(Exception):
    pass


class JemuWebApi(object):
    def __init__(self, api_url=API_URL, jemu_token=None):
        self._api_url = api_url
        self._token = jemu_token or os.environ['JEMU_TOKEN']
        self._headers = {'Authorization': 'Bearer ' + self._token}
        self._user_uid = None
        self.init()

    def init(self):
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

    def create_emulator(self, fw_filename, fw_bin_data, dest):
        self.upload_file(fw_filename, fw_bin_data)
