
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
import urllib
import json
import os


from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory
from sawtooth_signing import ParseError
from sawtooth_signing.secp256k1 import Secp256k1PrivateKey

from sawtooth_rest_api.protobuf.validator_pb2 import Message
from sawtooth_rest_api.protobuf import client_batch_submit_pb2
from sawtooth_rest_api.protobuf import client_batch_pb2
from sawtooth_rest_api.protobuf import client_list_control_pb2

from sawtooth_rest_api.protobuf.batch_pb2 import Batch
from sawtooth_rest_api.protobuf.batch_pb2 import BatchList
from sawtooth_rest_api.protobuf.batch_pb2 import BatchHeader
from sawtooth_rest_api.protobuf.transaction_pb2 import TransactionHeader
from sawtooth_rest_api.protobuf.transaction_pb2 import Transaction


from google.protobuf.json_format import MessageToDict


from utils import get_batches,  get_transactions, get_state, post_batch, get_blocks, \
                  get_state_list , _delete_genesis , _start_validator, \
                  _stop_validator , _create_genesis , wait_for_rest_apis , _get_client_address, \
                  _stop_settings_tp, _start_settings_tp

from payload import get_signer, create_intkey_transaction , create_batch

               

from utils import get_batches, post_batch,  get_signer , get_blocks , create_batch, \
                  create_intkey_transaction , get_state_list , _delete_genesis , _start_validator, \
                  _stop_validator


from google.protobuf.json_format import MessageToDict

                  

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
                  
                  


@pytest.fixture(scope="function")
def break_genesis(request):
    """Setup Function for deleting the genesis data
       and restarting the validator with no genesis
       
       Waits for services to start again before 
       sending the request again
    """
    _stop_validator()
    LOGGER.info("Deleting the genesis data")
    _delete_genesis()
    _start_validator()

    
@pytest.fixture(scope="function")
def setup_settings_tp(request):
    _stop_settings_tp()
    print("settings tp is connected")
    
    def teardown():
        print("Connecting settings tp")
        _start_settings_tp()
     
    request.addfinalizer(teardown) 

@pytest.fixture(scope="function")
def invalid_batch():
    """Setup method for creating invalid batches
    """
    signer = get_signer()
    
    LOGGER.info("Creating intkey transactions with set operations")
    
    txns = [
        create_invalid_intkey_transaction("set", 'a', 0, [], signer),
    ]

    

@pytest.fixture(scope="module")
def setup_batch(request):
    """Setup method for posting batches and returning the 
       response
    """
    data = {}
    signer = get_signer()
    expected_trxn_ids  = []
    expected_batch_ids = []
    initial_state_length = len(get_state_list())

    LOGGER.info("Creating intkey transactions with set operations")
    
    txns = [
        create_intkey_transaction("set", 'a', 0, [], signer),
    ]

    for txn in txns:
        data = MessageToDict(
                txn,
                including_default_value_fields=True,
                preserving_proto_field_name=True)

        trxn_id = data['header_signature']
        expected_trxn_ids.append(trxn_id)
    
    data['expected_trxn_ids'] = expected_trxn_ids


    LOGGER.info("Creating batches for transactions 1trn/batch")

    batches = [create_batch([txn], signer) for txn in txns]

    post_batch_list = [BatchList(batches=[batch]).SerializeToString() for batch in batches]
    
    return post_batch_list

@pytest.fixture(scope="function")
def setup_batch_multiple_transcation():
    data = {}
    signer = get_signer()
    transactions= []
    expected_trxns  = []
    expected_batches = []
    initial_state_length = len(get_state_list())

    LOGGER.info("Creating intkey transactions with set operations")
    for val in range(15):
        txns = create_intkey_transaction("set", [] , 50 , signer)
        transactions.append(txns)
        
            
    for txn in transactions:
        #print(txn)
        data = MessageToDict(
                txn,
                including_default_value_fields=True,
                preserving_proto_field_name=True)

        trxn_id = data['header_signature']
        expected_trxns.append(trxn_id)
    
    
    
    batch_s= create_batch(transactions, signer)        
    #print(batch_s)
    post_batch_list = BatchList(batches=[batch_s]).SerializeToString()
    
    LOGGER.info("Submitting batches to the handlers")
    
    #for batch in post_batch_list:
    try:
        response = post_batch(post_batch_list)
    except urllib.error.HTTPError as error:
        LOGGER.info("Rest Api is not reachable")
        data = json.loads(error.fp.read().decode('utf-8'))
        LOGGER.info(data['error']['title'])
        LOGGER.info(data['error']['message'])    
    
    return expected_trxns




    for batch in batches:
        data = MessageToDict(
                batch,
                including_default_value_fields=True,
                preserving_proto_field_name=True)

        batch_id = data['header_signature']
        expected_batch_ids.append(batch_id)
    
    data['expected_batch_ids'] = expected_batch_ids
    data['signer_key'] = signer.get_public_key().as_hex()

    post_batch_list = [BatchList(batches=[batch]).SerializeToString() for batch in batches]
    
    LOGGER.info("Submitting batches to the handlers")
    
    for batch in post_batch_list:
        try:
            response = post_batch(batch)
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is not reachable")
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
      
    block_list = get_blocks()
    data['block_list'] = block_list
    block_ids = [block['header_signature'] for block in block_list]
    data['block_ids'] = block_ids
    batch_ids = [block['header']['batch_ids'][0] for block in block_list]
    data['batch_ids'] = batch_ids
    expected_head_id = block_ids[0]
    data['expected_head_id'] = expected_head_id
    yield data


@pytest.fixture(scope="module")
def delete_genesis():
    LOGGER.info("Deleting the genesis data")
    _delete_genesis()
    _stop_validator()
    _create_genesis()
    _start_validator()

def _create_genesis():
    LOGGER.info("creating the genesis data")
    batch_path = '~'
    os.chdir(batch_path)
    cmd = "sudo -u sawadm config-genesis.batch"
    subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)


    