# Copyright 2018 Intel Corporation
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
import pytest
import logging
import json
import urllib.request
import urllib.error
import base64
import argparse
import cbor
import subprocess
import shlex
import requests
import hashlib

from google.protobuf.json_format import MessageToDict


from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey

from sawtooth_rest_api.protobuf.batch_pb2 import Batch
from sawtooth_rest_api.protobuf.batch_pb2 import BatchList
from sawtooth_rest_api.protobuf.batch_pb2 import BatchHeader
from sawtooth_rest_api.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_rest_api.protobuf.transaction_pb2 import Transaction

from utils import post_batch, get_state_list , get_blocks , get_transactions, \
                  get_batches , get_state, check_for_consensus,\
                  _get_node_list, _get_node_chains, post_batch_statuses, get_batch_statuses
from base import RestApiBaseTest
from conftest import setup
                  

from payload import get_signer, create_intkey_transaction, create_batch, create_intkey_same_transaction
                  

from payload import get_signer, create_intkey_transaction, create_batch, check_key_state



LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

BLOCK_TO_CHECK_CONSENSUS = 1

pytestmark = pytest.mark.post

class TestPostBatchList(RestApiBaseTest):
    """This class tests the batch list with different parameters
    """
    def test_rest_api_post_batch(self, setup):
        """Tests that transactions are submitted and committed for
        each block that are created by submitting intkey batches
        """
        LOGGER.info('Starting test for batch post')
    
        signer = get_signer()
        expected_trxn_ids  = []
        expected_batch_ids = []
        initial_state_length = len(get_state_list())
    
        LOGGER.info("Creating intkey transactions with set operations")
        txns = [
            create_intkey_transaction("set", 'a', 0, [], signer),
            create_intkey_transaction("set", 'b', 0, [], signer),
            create_intkey_transaction("set", 'C', 0, [], signer),
        ]
    
        for txn in txns:
            data = MessageToDict(
                    txn,
                    including_default_value_fields=True,
                    preserving_proto_field_name=True)
    
            trxn_id = data['header_signature']
            expected_trxn_ids.append(trxn_id)
    
        LOGGER.info("Creating batches for transactions 1trn/batch")
    
        batches = [create_batch([txn], signer) for txn in txns]
    
        for batch in batches:
            data = MessageToDict(
                    batch,
                    including_default_value_fields=True,
                    preserving_proto_field_name=True)
    
            batch_id = data['header_signature']
            expected_batch_ids.append(batch_id)
    
        post_batch_list = [BatchList(batches=[batch]).SerializeToString() for batch in batches]
    
        LOGGER.info("Submitting batches to the handlers")
    
        for batch in post_batch_list:
            try:
                response = post_batch(batch)
            except urllib.error.HTTPError as error:
                data = error.fp.read().decode('utf-8')
                LOGGER.info(data)
    
            block_batch_ids = [block['header']['batch_ids'][0] for block in get_blocks()]
            state_addresses = [state['address'] for state in get_state_list()['data']]
            state_head_list = [get_state(address)['head'] for address in state_addresses]
            committed_transaction_list = get_transactions()
            final_state_length= len(get_state_list())
            for trxn in committed_transaction_list:
                print(trxn['header_signature'])
                print(trxn['family_name'])
                print(trxn['family_version'])
                print(trxn['signer_public_key'])
                print(trxn['batcher_public_key'])
    
            if response['data'][0]['status'] == 'COMMITTED':
                LOGGER.info('Batch is committed')
    
                """check transaction is submitted successfully"""
    
    
    
                """check block is created for the batch"""
    
                for batch in batch_ids:
                    if batch in block_batch_ids:
                        LOGGER.info("Block is created for the respective batch")
    
                """check state is updated when batch is committed  successfully"""
    
    
                assert initial_state_length ==  initial_state_length + 1
            elif response['data'][0]['status'] == 'INVALID':
                LOGGER.info('Batch submission failed')
    
                if any(['message' in response['data'][0]['invalid_transactions'][0]]):
                    message = response['data'][0]['invalid_transactions'][0]['message']
                    LOGGER.info(message)
    
                """check transaction is not submitted successfully"""
    
    
                """check block is not created for the batch"""
    
                for batch in batch_ids:
                    if batch in block_batch_ids:
                        LOGGER.info("Block is created for the respective batch")
    
                """check state is not updated when batch submission fails"""
    
                assert initial_state_length == final_state_length, "State should not be updated when batch submission fails"
    
    
    
        node_list = _get_node_list()
        chains = _get_node_chains(node_list)
        assert check_for_consensus(chains , BLOCK_TO_CHECK_CONSENSUS) == True
        
    def test_rest_api_post_bad_protobuf(self,setup):
            """Tests when a bad protobuf is passed 
            """
            bad_protobuf=b'a'
            
            try:
                response = post_batch(batch=bad_protobuf)
            except urllib.error.HTTPError as error:
                data = json.loads(error.fp.read().decode('utf-8'))
                LOGGER.info(data['error']['title'])
                LOGGER.info(data['error']['message'])
                assert data['error']['code'] == 35
                
    
    
    def test_rest_api_post_wrong_header(self,setup):
        """Tests rest api by posting with wrong header
        """
        LOGGER.info('Starting test for batch post')
    
        signer = get_signer()
        expected_trxn_ids  = []
        expected_batch_ids = []
        initial_state_length = len(get_state_list())
    
        LOGGER.info("Creating intkey transactions with set operations")
        txns = [
            create_intkey_transaction("set", [] , 50 , signer),
            create_intkey_transaction("set", [] , 50 , signer),
            create_intkey_transaction("set", [] , 50 , signer),
        ]
    
        for txn in txns:
            data = MessageToDict(
                    txn,
                    including_default_value_fields=True,
                    preserving_proto_field_name=True)
    
            trxn_id = data['header_signature']
            expected_trxn_ids.append(trxn_id)
    
        LOGGER.info("Creating batches for transactions 1trn/batch")
    
        batches = [create_batch([txn], signer) for txn in txns]
    
        for batch in batches:
            data = MessageToDict(
                    batch,
                    including_default_value_fields=True,
                    preserving_proto_field_name=True)
    
            batch_id = data['header_signature']
            expected_batch_ids.append(batch_id)
    
        post_batch_list = [BatchList(batches=[batch]).SerializeToString() for batch in batches]
    
        LOGGER.info("Submitting batches to the handlers")
    
        for batch in post_batch_list:
            try:
                response = post_batch(batch,headers="True")
            except urllib.error.HTTPError as e:
                errdata = e.file.read().decode("utf-8")
                error = json.loads(errdata)
                LOGGER.info(error['error']['message'])
                assert (json.loads(errdata)['error']['code']) == 42
                assert e.code == 400
            '''
            block_batch_ids = [block['header']['batch_ids'][0] for block in get_blocks()]
            state_addresses = [state['address'] for state in get_state_list()['data']]
            state_head_list = [get_state(address)['head'] for address in state_addresses]
            '''
    def test_rest_api_post_same_txns(self, setup):
        """Tests the rest-api by submitting multiple transactions with same key
        """
        LOGGER.info('Starting test for batch post')
    
        signer = get_signer()
        expected_trxn_ids  = []
        expected_batch_ids = []
        initial_state_length = len(get_state_list())
    
        LOGGER.info("Creating intkey transactions with set operations")
        txns = [
            create_intkey_same_transaction("set", [] , 50 , signer),
            create_intkey_same_transaction("set", [] , 50 , signer),
            create_intkey_same_transaction("set", [] , 50 , signer),
        ]
    
        for txn in txns:
            data = MessageToDict(
                    txn,
                    including_default_value_fields=True,
                    preserving_proto_field_name=True)
    
            trxn_id = data['header_signature']
            expected_trxn_ids.append(trxn_id)
    
        LOGGER.info("Creating batches for transactions 1trn/batch")
    
        batches = [create_batch([txn], signer) for txn in txns]
        #print (batches)
    
        for batch in batches:
            data = MessageToDict(
                    batch,
                    including_default_value_fields=True,
                    preserving_proto_field_name=True)
    
            batch_id = data['header_signature']
            expected_batch_ids.append(batch_id)
    
        post_batch_list = [BatchList(batches=[batch]).SerializeToString() for batch in batches]
    
        LOGGER.info("Submitting batches to the handlers")
    
        for batch in post_batch_list:
            try:
                response = post_batch(batch,headers="None")
                assert response['data'][0]['status'] == "INVALID"
            except urllib.error.HTTPError as e:
                errdata = e.file.read().decode("utf-8")
                error = json.loads(errdata)
                LOGGER.info(error['error']['message'])
                assert (json.loads(errdata)['error']['code']) == 42
                assert e.code == 400
         
    
    def test_api_post_empty_batch(self, setup):
        """Tests rest-api post by submitting empty batch.
        """
        batch=bytearray()
        try:
                    response=post_batch(batch)
        except urllib.error.HTTPError as e:
                    errdata = e.file.read().decode("utf-8")
                    error = json.loads(errdata)
                    assert (json.loads(errdata)['error']['code']) == 34
                    assert e.code == 400
                    
    def test_post_batch_not_decodable(self, setup):
        """Test rest-api when batch is not decodable
        """
           
        post_batch_list = setup['batch_list']
        batch=bytearray([0x13, 0x00, 0x00, 0x00, 0x08, 0x00])
        try:
                    
                    response=post_batch(batch)
                       
        except urllib.error.HTTPError as e:
                    errdata = e.file.read().decode("utf-8")
                    error = json.loads(errdata)
                    LOGGER.info(error['error']['message'])
                    assert (json.loads(errdata)['error']['code']) == 35
                    assert e.code == 400
                    
    def test_rest_api_state_multiple_txns_batches(self, setup):
        """Tests rest-api state by submitting multiple
            transactions in multiple batches
        """
        LOGGER.info('Starting test for batch post')
    
        signer = get_signer()
        expected_trxn_ids  = []
        expected_batch_ids = []
        initial_state_length = len(get_state_list())
    
        LOGGER.info("Creating intkey transactions with set operations")
        txns = [
            create_intkey_transaction("set", [] , 50 , signer),
            create_intkey_transaction("set", [] , 50 , signer),
            create_intkey_transaction("set", [] , 50 , signer),
        ]
    
        for txn in txns:
            data = MessageToDict(
                    txn,
                    including_default_value_fields=True,
                    preserving_proto_field_name=True)
    
            trxn_id = data['header_signature']
            expected_trxn_ids.append(trxn_id)
    
        LOGGER.info("Creating batches for transactions 1trn/batch")
    
        batches = [create_batch([txn], signer) for txn in txns]
    
        for batch in batches:
            data = MessageToDict(
                    batch,
                    including_default_value_fields=True,
                    preserving_proto_field_name=True)
    
            batch_id = data['header_signature']
            expected_batch_ids.append(batch_id)
    
        post_batch_list = [BatchList(batches=[batch]).SerializeToString() for batch in batches]
    
        LOGGER.info("Submitting batches to the handlers")
    
        for batch in post_batch_list:
            try:
                response = post_batch(batch,headers="None")
                response = get_state_list()
            except urllib.error.HTTPError as e:
                errdata = e.file.read().decode("utf-8")
                error = json.loads(errdata)
                LOGGER.info(error['error']['message'])
                assert (json.loads(errdata)['error']['code']) == 42
                assert e.code == 400
        final_state_length = len(get_state_list())
        assert initial_state_length == final_state_length
        
    def test_api_post_batch_different_signer(self, setup):
        signer_trans = get_signer() 
        intkey=create_intkey_transaction("set",[],50,signer_trans)
        translist=[intkey]
        signer_batch = get_signer()
        batch= create_batch(translist,signer_batch)
        batch_list=[BatchList(batches=[batch]).SerializeToString()]
        for batc in batch_list:
                try:
                    response = post_batch(batc)
                    print(response)
                except urllib.error.HTTPError as error:
                    LOGGER.info("Rest Api is not reachable")
                    data = json.loads(error.fp.read().decode('utf-8'))
                    LOGGER.info(data['error']['title'])
                    LOGGER.info(data['error']['message'])
                    assert data['error']['code'] == 30
                    assert data['error']['title'] =='Submitted Batches Invalid' 
                    
    def test_api_post_batch_different_signer(self, setup):
        signer_trans = get_signer() 
        intkey=create_intkey_transaction("set",[],50,signer_trans)
        translist=[intkey]
        signer_batch = get_signer()
        batch= create_batch(translist,signer_batch)
        batch_list=[BatchList(batches=[batch]).SerializeToString()]
        for batc in batch_list:
                try:
                    response = post_batch(batc)
                    print(response)
                except urllib.error.HTTPError as error:
                    LOGGER.info("Rest Api is not reachable")
                    data = json.loads(error.fp.read().decode('utf-8'))
                    LOGGER.info(data['error']['title'])
                    LOGGER.info(data['error']['message'])
                    assert data['error']['code'] == 30
                    assert data['error']['title'] =='Submitted Batches Invalid' 
                    
class TestBatchStatusesList(RestApiBaseTest):
    """This class tests the batch list with different parameters
    """
    def test_api_post_batch_status_15ids(self, setup):   
        """verifies that GET /batches is unreachable with bad head parameter 
        """
        LOGGER.info("Starting test for batch with bad head parameter")
        data = {}
        batch_ids = setup['batch_ids']
        data['batch_ids'] = batch_ids
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        reverse = True
        data_str=json.dumps(data['batch_ids']).encode()
                        
        try:
            response = post_batch_statuses(data_str)
            assert response['data'][0]['status'] == "COMMITTED"
        except urllib.error.HTTPError as error:
            assert response.code == 400
   
    def test_api_post_batch_status_10ids(self, setup):   
        """verifies that GET /batches is unreachable with bad head parameter 
        """
        LOGGER.info("Starting test for batch with bad head parameter")
        data = {}
        values = []
        batch_ids = setup['batch_ids']
        data['batch_ids'] = batch_ids
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        reverse = True
        for i in range(10):
            values.append(data['batch_ids'][i])
        data_str=json.dumps(values).encode()
                        
        try:
            response = post_batch_statuses(data_str)
            assert response['data'][0]['status'] == "COMMITTED"
        except urllib.error.HTTPError as error:
            assert response.code == 400
            
    def test_api_inc_notstate_txns(self, setup):
        """Tests the rest-api by submitting intkey inc transactions 
        """
        LOGGER.info('Starting test for intkey inc post')
    
        signer = get_signer()
        # check set
        response=check_key_state(100)
        if response==1:
            
            LOGGER.info("Checking intkey increment operations")
            txns = [
                create_intkey_transaction("inc", [] , 50 , signer),   
            ]
        
            for txn in txns:
                data = MessageToDict(
                        txn,
                        including_default_value_fields=True,
                        preserving_proto_field_name=True)
        
                trxn_id = data['header_signature']
                #expected_trxn_ids.append(trxn_id)
        
            LOGGER.info("Creating batches for transactions 1trn/batch")
        
            batches = [create_batch([txn], signer) for txn in txns]
        
            for batch in batches:
                data = MessageToDict(
                        batch,
                        including_default_value_fields=True,
                        preserving_proto_field_name=True)
        
                batch_id = data['header_signature']
                #expected_batch_ids.append(batch_id)
        
            post_batch_list = [BatchList(batches=[batch]).SerializeToString() for batch in batches]
        
            LOGGER.info("Submitting batches to the handlers")
            for batch in post_batch_list:
                try:
                    response = post_batch(batch,headers="None")
                    self.assert_commit_invalid(response['data'][0]['status'])
                except urllib.error.HTTPError as e:
                    self.assert_400()     
        else:
            LOGGER.info("key is already set")
            self.assert_False()
            
    def test_api_dec_notstate_txns(self, setup):
        """Tests the rest-api by submitting intkey dec transactions 
        """
        LOGGER.info('Starting test for intkey dec post')
    
        
        LOGGER.info('Starting test for batch post')
        response=check_key_state(100)
        if response==1:
    
            signer = get_signer()
        
            LOGGER.info("Creating intkey transactions with dec operations")
            txns = [
                create_intkey_transaction("dec", [] , 50 , signer),
            ]
        
            for txn in txns:
                data = MessageToDict(
                        txn,
                        including_default_value_fields=True,
                        preserving_proto_field_name=True)
        
                trxn_id = data['header_signature']
                #expected_trxn_ids.append(trxn_id)
        
            LOGGER.info("Creating batches for transactions 1trn/batch")
        
            batches = [create_batch([txn], signer) for txn in txns]
            #print (batches)
        
            for batch in batches:
                data = MessageToDict(
                        batch,
                        including_default_value_fields=True,
                        preserving_proto_field_name=True)
        
                batch_id = data['header_signature']
                #expected_batch_ids.append(batch_id)
        
            post_batch_list = [BatchList(batches=[batch]).SerializeToString() for batch in batches]
        
            LOGGER.info("Submitting batches to the handlers")
        
            for batch in post_batch_list:
                try:
                    response = post_batch(batch,headers="None")
                    self.assert_commit_invalid(response['data'][0]['status'])
                except urllib.error.HTTPError as e:
                    pass
                    self.assert_400()
        else:
            LOGGER.info("Key is already set")
            self.assert_False()
                
    def test_api_post_batch_statuses_int_err(self, setup):   
        """verifies post /batch_statuses with internal error
        """
        data = {}
        values = []
        batch_ids = setup['batch_ids']
        data['batch_ids'] = batch_ids
        for i in range(1):
            values.append(data['batch_ids'][i])
        data_str=json.dumps(values).encode()
        data=data_str[::-1]
                        
        try:
            response = post_batch_statuses(data)
        except urllib.error.HTTPError as error:
            self.assert_500(error.code)
            
    def test_api_post_batch_statuses_bad_req(self, setup):   
        """verifies post /batch_statuses with bad request
        """
        data = {}
        values = []
        batch_ids = setup['batch_ids']
        data['batch_ids'] = batch_ids
        for i in range(1):
            values.append(data['batch_ids'][i])
            v=values.pop()
        data_str=json.dumps(v).encode()
                        
        try:
            response = post_batch_statuses(data_str)
        except urllib.error.HTTPError as error:
            self.assert_400(error.code)
    
            
    


# def test_rest_post_two_trans_batch():
#     """Tests two same intkey transaction in one batch
#     """
#     signer = get_signer()
#
#     txns = [
#         create_intkey_transaction("set", 'a', 0, [], signer),
#         create_intkey_transaction("set", 'a', 0, [], signer),
#     ]
#
#     batches = [create_batch([txn], signer) for txn in txns]
#     print(batches)
#
#     batch_list = [BatchList(batches=[batch]).SerializeToString() for batch in batches]
#     print(batch_list)
#
#
#     for batch in batch_list:
#         post_batch(batch)
#


# def test_rest_post_two_trans_batch():
#     """Tests two same intkey transaction in two different batches
#     """
#     signer = get_signer()
#
#     txns = [
#         create_intkey_transaction("set", 'a', 0, [], signer),
#         create_intkey_transaction("set", 'a', 0, [], signer),
#     ]
#
#     batches = [create_batch([txn], signer) for txn in txns]
#     print(batches)
#
#     batch_list = [BatchList(batches=[batch]).SerializeToString() for batch in batches]
#     print(batch_list)
#
#
#     for batch in batch_list:
#         post_batch(batch)
