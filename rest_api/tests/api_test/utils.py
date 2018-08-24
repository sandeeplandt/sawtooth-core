
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

from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.error import URLError


import base64
import argparse
import cbor
import subprocess
import shlex
import requests
import hashlib
import os

import time



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

from google.protobuf.message import DecodeError
from google.protobuf.json_format import MessageToDict

INTKEY_ADDRESS_PREFIX = hashlib.sha512(
    'intkey'.encode('utf-8')).hexdigest()[0:6]

    
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
    
WAIT = 300


def get_blocks(head_id=None , id=None , start=None , limit=None , reverse=None):  
    if all(v is not None for v in [head_id , id]):
        response = query_rest_api('/blocks?head={}&id={}'.format(head_id , id))
        return response
    if all(v is not None for v in [start , limit]):
        response = query_rest_api('/blocks?start={}&limit={}'.format(start , limit))
        return response
    if limit is not None:
        response = query_rest_api('/blocks?limit=%s'% limit)
        return response 
    if start is not None:
        response = query_rest_api('/blocks?start=%s'% start)
        return response 
    if head_id is not None:
        response = query_rest_api('/blocks?head=%s'% head_id)
        return response 
    if id is not None:
        response = query_rest_api('/blocks?id=%s'% id)
        return response
    if reverse:
        response = query_rest_api('/blocks?reverse')
        return response
    else:
        response = query_rest_api('/blocks')
        return response


def get_batches(head_id=None , id=None , start=None , limit=None , reverse=None):  

    if all(v is not None for v in [head_id , id]):
        response = query_rest_api('/batches?head={}&id={}'.format(head_id , id))
        return response
    if all(v is not None for v in [start , limit]):
        response = query_rest_api('/batches?start={}&limit={}'.format(start , limit))
        return response
    if limit is not None:
        response = query_rest_api('/batches?limit=%s'% limit)
        return response 
    if start is not None:
        response = query_rest_api('/batches?start=%s'% start)
        return response 
    if head_id is not None:
        response = query_rest_api('/batches?head=%s'% head_id)
        return response 
    if id is not None:
        response = query_rest_api('/batches?id=%s'% id)
        return response
    if reverse:
        response = query_rest_api('/batches?reverse')
        return response
    else:
        response = query_rest_api('/batches')
        return response

def get_batch(batch_id):
    response = query_rest_api('/batches/%s' % batch_id)
    return response

def get_transactions(head_id=None , id=None , start=None , limit=None , reverse=None):
    if all(v is not None for v in [head_id , id]):
        response = query_rest_api('/transactions?head={}&id={}'.format(head_id , id))
        return response
    if all(v is not None for v in [start , limit]):
        response = query_rest_api('/transactions?start={}&limit={}'.format(start , limit))
        return response
    if limit is not None:
        response = query_rest_api('/transactions?limit=%s'% limit)
        return response 
    if start is not None:
        response = query_rest_api('/transactions?start=%s'% start)
        return response 
    if head_id is not None:
        response = query_rest_api('/transactions?head=%s'% head_id)
        return response 
    if id is not None:
        response = query_rest_api('/transactions?id=%s'% id)
        return response
    if reverse:
        response = query_rest_api('/transactions?reverse')
        return response
    else:
        response = query_rest_api('/transactions')
        return response

    return response['data']

def get_transactions():
    response = query_rest_api('/transactions')
    return response['data']


def get_transaction(transaction_id):
    response = query_rest_api('/transactions/%s' % transaction_id)
    return response['data']


def get_state_list(head_id=None , id=None , start=None , limit=None , reverse=None):
    if all(v is not None for v in [head_id , id]):
        response = query_rest_api('/state?head={}&id={}'.format(head_id , id))
        return response
    if all(v is not None for v in [start , limit]):
        response = query_rest_api('/state?start={}&limit={}'.format(start , limit))
        return response
    if limit is not None:
        response = query_rest_api('/state?limit=%s'% limit)
        return response 
    if start is not None:
        response = query_rest_api('/state?start=%s'% start)
        return response 
    if head_id is not None:
        response = query_rest_api('/state?head=%s'% head_id)
        return response 
    if id is not None:
        response = query_rest_api('/state?id=%s'% id)
        return response
    if reverse:
        response = query_rest_api('/state?reverse')
        return response
    else:
        response = query_rest_api('/state')
        return response

def get_state(address):
    response = query_rest_api('/state/%s' % address)
    return response


def post_batch(batch, headers="None"):
    if headers=="True":
        headers = {'Content-Type': 'application/json'}  
    else:
        headers = {'Content-Type': 'application/octet-stream'}
    response = query_rest_api(
        '/batches', data=batch, headers=headers)
    response = submit_request('{}&wait={}'.format(response['link'], WAIT))
    return response 

def query_rest_api(suffix='', data=None, headers=None):
    if headers is None:
        headers = {}
    url = _get_client_address() + suffix
    return submit_request(urllib.request.Request(url, data, headers))

def submit_request(request):
    response = urllib.request.urlopen(request).read().decode('utf-8')
    return json.loads(response)

def _delete_genesis():
    folder = '/var/lib/sawtooth'
    for the_file in os.listdir(folder):
        file_path = os.path.join(folder, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)



def _get_node_chain(node_list):
    chain_list = []
    for node in node_list:
        try:
            result = requests.get(node + "/blocks").json()
            chain_list.append(result['data'])
        except:
            LOGGER.warning("Couldn't connect to %s REST API", node)
    return chain_list
    

def check_for_consensus(chains , block_num):
    LOGGER.info("Checking Consensus on block number %s" , block_num)
    blocks = []
    for chain in chains:
        if chain is not None:
            block = chain[-(block_num + 1)]
            blocks.append(block)
        else:
            return False
    block0 = blocks[0]
    for block in blocks[1:]:
        if block0["header_signature"] != block["header_signature"]:
            LOGGER.error("Validators not in consensus on block %s", block_num)
            LOGGER.error("BLOCK DUMP: %s", blocks)
            return False
        else:
            LOGGER.info('Validators in Consensus on block number %s' , block_num)
    return True



def _get_node_list():
    client_address = _get_client_address()
    node_list = [_make_http_address(peer) for peer in _get_peers_list(client_address)]
    node_list.append(_get_client_address())
    return node_list
        

def _get_peers_list(rest_client, fmt='json'):
    cmd_output = _run_peer_command(
        'sawtooth peer list --url {} --format {}'.format(
            rest_client,
            fmt))

    if fmt == 'json':
        parsed = json.loads(cmd_output)

    elif fmt == 'csv':
        parsed = cmd_output.split(',')

    return set(parsed)

def _get_node_chains(node_list):
    chain_list = []
    for node in node_list:
        try:
            result = requests.get(node + "/blocks").json()
            chain_list.append(result['data'])
        except:
            LOGGER.warning("Couldn't connect to %s REST API", node)
    return chain_list
    
def check_for_consensus(chains , block_num):
    LOGGER.info("Checking Consensus on block number %s" , block_num)
    blocks = []
    for chain in chains:
        if chain is not None:
            block = chain[-(block_num + 1)]
            blocks.append(block)
        else:
            return False
    block0 = blocks[0]
    for block in blocks[1:]:
        if block0["header_signature"] != block["header_signature"]:
            LOGGER.error("Validators not in consensus on block %s", block_num)
            LOGGER.error("BLOCK DUMP: %s", blocks)
            return False
        else:
            LOGGER.info('Validators in Consensus on block number %s' , block_num)
    return True

def _run_peer_command(command):
    return subprocess.check_output(
        shlex.split(command)
    ).decode().strip().replace("'", '"')

def _send_cmd(cmd_str):
    LOGGER.info('Sending %s', cmd_str)

    subprocess.run(
        shlex.split(cmd_str),
        check=True)

def _make_http_address(node_number):
    node = node_number.replace('tcp' , 'http')
    node_number = node.replace('8800' , '8008')
    return node_number

def _get_client_address():  
    command = "ifconfig lo | grep 'inet addr' | cut -d ':' -f 2 | cut -d ' ' -f 1"
    node_ip = subprocess.check_output(command , shell=True).decode().strip().replace("'", '"')
    return 'http://' + node_ip + ':8008'

def _start_validator():
    LOGGER.info('Starting the validator')
    cmd = "sudo -u sawtooth sawtooth-validator -vv"
    subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
    
def _stop_validator():
    LOGGER.info('Stopping the validator')
    cmd = "sudo kill -9  $(ps aux | grep 'sawtooth-validator' | awk '{print $2}')"
    subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)



def _start_settings_tp():
    LOGGER.info('Starting settings-tp')
    cmd = " sudo -u sawtooth  settings-tp -vv "
    subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)

def _stop_settings_tp():
    LOGGER.info('Stopping the settings-tp')
    cmd = "sudo kill -9  $(ps aux | grep 'settings-tp' | awk '{print $2}')"
    subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE) 

def _create_genesis():
    LOGGER.info("creating the genesis data")
    _create_genesis_batch()
    os.chdir("/home/aditya")
    cmd = "sawadm genesis config-genesis.batch"
    subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
    
    
def _create_genesis_batch():
    LOGGER.info("creating the config genesis batch")
    os.chdir("/home/aditya")
    cmd = "sawset genesis --force"
    subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE)
    
    

def wait_until_status(url, status_code=200, tries=5):
    """Pause the program until the given url returns the required status.

    Args:
        url (str): The url to query.
        status_code (int, optional): The required status code. Defaults to 200.
        tries (int, optional): The number of attempts to request the url for
            the given status. Defaults to 5.
    Raises:
        AssertionError: If the status is not recieved in the given number of
            tries.
    """
    attempts = tries
    while attempts > 0:
        try:
            response = urlopen(url)
            if response.getcode() == status_code:
                return

        except HTTPError as err:
            if err.code == status_code:
                return

            LOGGER.debug('failed to read url: %s', str(err))
        except URLError as err:
            LOGGER.debug('failed to read url: %s', str(err))

        sleep_time = (tries - attempts + 1) * 2
        LOGGER.debug('Retrying in %s secs', sleep_time)
        time.sleep(sleep_time)

        attempts -= 1

    raise AssertionError(
        "{} is not available within {} attempts".format(url, tries))


def wait_for_rest_apis(endpoints, tries=5):
    """Pause the program until all the given REST API endpoints are available.

    Args:
        endpoints (list of str): A list of host:port strings.
        tries (int, optional): The number of attempts to request the url for
            availability.
    """
    for endpoint in endpoints:
        http = 'http://'
        url = endpoint if endpoint.startswith(http) else http + endpoint
        wait_until_status(
            '{}/blocks'.format(url),
            status_code=200,
            tries=tries)
def post_batch_statuses(batch):
    headers = {'content-type': 'application/json'}
    response = query_rest_api(
        '/batch_statuses', data=batch, headers=headers)
    #response = submit_request('{}&wait={}'.format(response['link'], WAIT))
    return response

def get_batch_statuses(batch_id):
    response = query_rest_api('/batch_statuses?id={}' % batch_id )
    #return base64.b64decode(response['data'])
    return response['data']  

def get_state_limit(limit):
    response = query_rest_api('/state?limit=%s' % limit)
    #return base64.b64decode(response['data'])
    return response['data']


def get_reciepts(reciept_id):
    response = query_rest_api('/receipts?id=%s' % reciept_id)
    return response


def post_receipts(receipts):
    headers = {'Content-Type': 'application/json'}
     
    response = query_rest_api('/receipts', data=receipts, headers=headers)

    return response

def make_intkey_address(name):
    return INTKEY_ADDRESS_PREFIX + hashlib.sha512(
        name.encode('utf-8')).hexdigest()[-64:]


class IntKeyPayload(object):
    def __init__(self, verb, name, value):
        self._verb = verb
        self._name = name
        self._value = value

        self._cbor = None
        self._sha512 = None

    def to_hash(self):
        return {
            'Verb': self._verb,
            'Name': self._name,
            'Value': self._value
        }

    def to_cbor(self):
        if self._cbor is None:
            self._cbor = cbor.dumps(self.to_hash(), sort_keys=True)
        return self._cbor

    def sha512(self):
        if self._sha512 is None:
            self._sha512 = hashlib.sha512(self.to_cbor()).hexdigest()
        return self._sha512


def create_intkey_transaction(verb, name, value, deps, signer):
    payload = IntKeyPayload(
        verb=verb, name=name, value=value)

    # The prefix should eventually be looked up from the
    # validator's namespace registry.
    addr = make_intkey_address(name)

    header = TransactionHeader(
        signer_public_key=signer.get_public_key().as_hex(),
        family_name='intkey',
        family_version='1.0',
        inputs=[addr],
        outputs=[addr],
        dependencies=deps,
        payload_sha512=payload.sha512(),
        batcher_public_key=signer.get_public_key().as_hex())

    header_bytes = header.SerializeToString()

    signature = signer.sign(header_bytes)

    transaction = Transaction(
        header=header_bytes,
        payload=payload.to_cbor(),
        header_signature=signature)

    return transaction


def create_batch(transactions, signer):
    transaction_signatures = [t.header_signature for t in transactions]

    header = BatchHeader(
        signer_public_key=signer.get_public_key().as_hex(),
        transaction_ids=transaction_signatures)

    header_bytes = header.SerializeToString()

    signature = signer.sign(header_bytes)

    batch = Batch(
        header=header_bytes,
        transactions=transactions,
        header_signature=signature)

    return batch

def get_signer():
    context = create_context('secp256k1')
    private_key = context.new_random_private_key()
    crypto_factory = CryptoFactory(context)
    return crypto_factory.new_signer(private_key)



def _expand_block(cls, block):
    """Deserializes a Block's header, and the header of its Batches.
    """
    cls._parse_header(BlockHeader, block)
    if 'batches' in block:
        block['batches'] = [cls._expand_batch(b) for b in block['batches']]
    return block


def _expand_batch(cls, batch):
    """Deserializes a Batch's header, and the header of its Transactions.
    """
    cls._parse_header(BatchHeader, batch)
    if 'transactions' in batch:
        batch['transactions'] = [
            cls._expand_transaction(t) for t in batch['transactions']]
    return batch


def _expand_transaction(cls, transaction):
    """Deserializes a Transaction's header.
    """
    return cls._parse_header(TransactionHeader, transaction)


def _parse_header(cls, header_proto, resource):
    """Deserializes a resource's base64 encoded Protobuf header.
    """
    header = header_proto()
    try:
        header_bytes = base64.b64decode(resource['header'])
        header.ParseFromString(header_bytes)
    except (KeyError, TypeError, ValueError, DecodeError):
        header = resource.get('header', None)
        LOGGER.error(
            'The validator sent a resource with %s %s',
            'a missing header' if header is None else 'an invalid header:',
            header or '')
        raise errors.ResourceHeaderInvalid()

    resource['header'] = cls._message_to_dict(header)
    return resource

