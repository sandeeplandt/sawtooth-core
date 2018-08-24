# Copyright 2016 Intel Corporation
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

import cbor
import pytest
import random
import hashlib
import string

from sawtooth_intkey.processor.handler import INTKEY_ADDRESS_PREFIX
from sawtooth_intkey.processor.handler import make_intkey_address
from sawtooth_signing import create_context
from sawtooth_signing import CryptoFactory

from sawtooth_sdk.protobuf.processor_pb2 import TpRegisterRequest
from sawtooth_sdk.protobuf.processor_pb2 import TpProcessResponse
from sawtooth_sdk.protobuf.processor_pb2 import TpProcessRequest
from sawtooth_sdk.protobuf.transaction_pb2 import Transaction
from sawtooth_sdk.protobuf.batch_pb2 import Batch
from sawtooth_sdk.protobuf.batch_pb2 import BatchList
from sawtooth_sdk.protobuf.batch_pb2 import BatchHeader
from sawtooth_sdk.protobuf.transaction_pb2 import TransactionHeader

def _signer():
    context = create_context('secp256k1')
    return CryptoFactory(context).new_signer(
        context.new_random_private_key())

class IntkeyMessageFactory:
    def __init__(self, signer=None):
        signer = _signer()
        self._signer = signer
        self.family_name='intkey'
        self.family_version='1.0'
        
    def get_public_key(self):
        return self._signer.get_public_key().as_hex()
    
    @property
    def namespace(self):
        return self.namespaces[0]

    @staticmethod
    def sha512(content):
        return hashlib.sha512(content).hexdigest()

    def _dumps(self, obj):
        return cbor.dumps(obj, sort_keys=True)

    def _loads(self, data):
        return cbor.loads(data)

    def create_tp_register(self):
        return self.create_tp_register()

    def create_tp_response(self, status):
        return self.create_tp_response(status)

    def _create_txn(self, txn_function, verb, name, value):
        payload = self._dumps({'Verb': verb, 'Name': name, 'Value': value})

        addresses = [make_intkey_address(name)]

        return txn_function(payload, addresses, addresses, [])

    def create_tp_process_request(self, verb, name, value,):
        txn_function = self.create_tp_process_request
        return self._create_txn(txn_function, verb, name, value)

    def create_transaction(self, verb, name, value,):
        txn_function = self.create_transaction_up
        return self._create_txn(txn_function, verb, name, value)

    def create_batch(self, triples):
        txns = [
            self.create_transaction(verb, name, value)
            for verb, name, value in triples
        ]

        return self.create_batch_up(txns)
    
    def create_batch_up(self, transactions):
        try:
            txn_signatures = [txn.header_signature for txn in transactions]
        except AttributeError:
            txn_signatures = [txn.signature for txn in transactions]

        header = BatchHeader(
            signer_public_key=self._signer.get_public_key().as_hex(),
            transaction_ids=txn_signatures
        ).SerializeToString()

        signature = self._signer.sign(header)

        batch = Batch(
            header=header,
            transactions=transactions,
            header_signature=signature)

        batch_list = BatchList(batches=[batch])

        return batch_list.SerializeToString()
    
    def create_transaction_up(self, payload, inputs, outputs, deps, batcher=None):
        header, signature = self._create_header_and_sig(
            payload, inputs, outputs, deps, batcher=batcher)

        return Transaction(
            header=header.SerializeToString(),
            payload=payload,
            header_signature=signature)
        
    def _create_signature(self, header):
        return self._signer.sign(header)

    def _create_header_and_sig(self, payload, inputs, outputs, deps,
                               set_nonce=True, batcher=None):
        header = self._create_transaction_header(
            payload, inputs, outputs, deps, set_nonce, batcher)
        signature = self._create_signature(header.SerializeToString())
        return header, signature
    
    def _create_transaction_header(self, payload, inputs, outputs, deps,
                                   set_nonce=True, batcher_pub_key=None):

        if set_nonce:
            nonce = hex(random.randint(0, 2**64))
        else:
            nonce = ""
        txn_pub_key = self._signer.get_public_key().as_hex()
        if batcher_pub_key is None:
            batcher_pub_key = txn_pub_key

        header = TransactionHeader(
            signer_public_key=txn_pub_key,
            family_name=self.family_name,
            family_version=self.family_version,
            inputs=inputs,
            outputs=outputs,
            dependencies=deps,
            payload_sha512=self.sha512(payload),
            batcher_public_key=batcher_pub_key,
            nonce=nonce
        )
        return header
   
