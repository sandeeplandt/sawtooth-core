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

    
    LOGGER.info("Creating batches for transactions 1trn/batch")

    batches = [create_batch([txn], signer) for txn in txns]

    post_batch_list = [BatchList(batches=[batch]).SerializeToString() for batch in batches]
    
    return post_batch_list



    