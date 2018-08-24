# Copyright 2017 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ------------------------------------------------------------------------------

# pylint: disable = attribute-defined-outside-init

import unittest
import logging
import operator  
import urllib.request
import urllib.error
import json
import pytest
from base64 import b64decode

import cbor

from intkey_message_factory import IntkeyMessageFactory



LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

WAIT = 300
INTKEY_PREFIX = '1cf126'


class TestIntkeySmoke(unittest.TestCase):
   

    def test_rest_api_valid_invalid_txns(self):

        self.verifier = IntkeyTestVerifier()

        populate, valid_txns, invalid_txns, valid_invalid_txns, invalid_valid_txns = self.make_txn_batches()

      
        batches = (
            populate,
            valid_invalid_txns
        )
  
        how_many_updates = 0

        for batch in batches:
            try:
                response=self.post_and_verify(batch, how_many_updates=0)
                assert response['data'][0]['status'] == "COMMITTED"
            except urllib.error.HTTPError as error:
                assert response.code == 400
                
    def test_rest_api_invalid_valid_txns(self):


            self.verifier = IntkeyTestVerifier()
    
            populate, valid_txns, invalid_txns, valid_invalid_txns, invalid_valid_txns = self.make_txn_batches()
            batches = (
                populate,
                invalid_valid_txns
            )
            how_many_updates = 0
    
            for batch in batches:
                try:
                    response=self.post_and_verify(batch, how_many_updates=0)
                    assert response['data'][0]['status'] == "COMMITTED"
                except urllib.error.HTTPError as error:
                    assert response.code == 400
    
    def test_rest_api_invalid_txns(self):


            self.verifier = IntkeyTestVerifier()
    
            populate, valid_txns, invalid_txns, valid_invalid_txns, invalid_valid_txns = self.make_txn_batches()
    
            batches = (
                populate,
                invalid_txns
            )
    
            how_many_updates = 0
    
            for batch in batches:
                try:
                    response=self.post_and_verify(batch, how_many_updates=0)
                    assert response['data'][0]['status'] == "COMMITTED"
                except urllib.error.HTTPError as error:
                    assert error.code == 300
    
    def test_rest_api_no_endpoint(self):


            self.verifier = IntkeyTestVerifier()
    
            populate, valid_txns, invalid_txns, valid_invalid_txns, invalid_valid_txns = self.make_txn_batches()
    
            batches = (
                populate,
                invalid_txns
            )
    
            how_many_updates = 0
    
            for batch in batches:
                try:
                    batch = IntkeyMessageFactory().create_batch(batch)
                    response = _post_batch_noendpoint(batch)
                    assert response['data'][0]['status'] == "COMMITTED"
                except urllib.error.HTTPError as error:
                    assert error.code == 404
            
    
    def post_and_verify(self, batch, how_many_updates):
        batch = IntkeyMessageFactory().create_batch(batch)
        LOGGER.info('Posting batch')
        response = _post_batch(batch)
        return response
    
    def make_txn_batches(self):
        LOGGER.debug('Making txn batches')
        batches = self.verifier.make_txn_batches()
        return batches



def _post_batch(batch):
    headers = {'Content-Type': 'application/octet-stream'}
    response = _query_rest_api(
        '/batches',
        data=batch, headers=headers, expected_code=202)
    response = _submit_request('{}&wait={}'.format(response['link'], WAIT))
    return response

def _post_batch_noendpoint(batch):
    headers = {'Content-Type': 'application/octet-stream'}
    response = _query_rest_api(
        '/',
        data=batch, headers=headers, expected_code=202)
    response = _submit_request('{}&wait={}'.format(response['link'], WAIT))
    return response

def _query_rest_api(suffix='', data=None, headers=None, expected_code=200):
    if headers is None:
        headers = {}
    url = 'http://localhost:8008' + suffix
    return _submit_request(urllib.request.Request(url, data, headers),
                           expected_code=expected_code)


def _submit_request(request, expected_code=200):
    conn = urllib.request.urlopen(request)
    assert expected_code == conn.getcode()

    response = conn.read().decode('utf-8')
    return json.loads(response)

class IntkeyTestVerifier:
    def __init__(self,
                 valid=('lark', 'thrush', 'jay', 'wren', 'finch'),
                 invalid=('cow', 'pig', 'sheep', 'goat', 'horse'),
                 verbs=('inc', 'inc', 'dec', 'inc', 'dec'),
                 validinvalid=('lark', 'cow'),
                 invalidvalid=('cow', 'lark'),
                 incdec=(1, 2, 3, 5, 8),
                 initial=(415, 325, 538, 437, 651)):
        self.valid = valid
        self.invalid = invalid
        self.verbs = verbs
        self.incdec = incdec
        self.initial = initial
        self.validinvalid = validinvalid
        self.invalidvalid = invalidvalid
        self.sets = ['set' for _ in range(len(self.initial))]

    def make_txn_batches(self):
        populate = tuple(zip(self.sets, self.valid, self.initial))
        print(populate)
        valid_txns = tuple(zip(self.verbs, self.valid, self.incdec))
        invalid_txns = tuple(zip(self.verbs, self.invalid, self.incdec))
        valid_invalid_txns = tuple(zip(self.verbs, self.validinvalid, self.incdec))
        invalid_valid_txns = tuple(zip(self.verbs, self.invalidvalid, self.incdec))

        return populate, valid_txns, invalid_txns, valid_invalid_txns, invalid_valid_txns
    
    
    
   
