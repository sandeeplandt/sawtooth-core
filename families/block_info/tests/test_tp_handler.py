import time
import zmq
import unittest




from sawtooth_processor_test.message_factory import MessageFactory
from sawtooth_block_info.protobuf.block_info_pb2 import BlockInfoTxn
from sawtooth_block_info.protobuf.block_info_pb2 import BlockInfo
from sawtooth_block_info.protobuf.block_info_pb2 import BlockInfoConfig
from sawtooth_block_info.processor.handler import BlockInfoTransactionHandler, validate_hex, validate_timestamp
from sawtooth_block_info.common import FAMILY_NAME
from sawtooth_block_info.common import FAMILY_VERSION
from sawtooth_block_info.common import NAMESPACE
from sawtooth_block_info.common import CONFIG_ADDRESS
from sawtooth_block_info.common import DEFAULT_SYNC_TOLERANCE
from sawtooth_block_info.common import DEFAULT_TARGET_COUNT
from sawtooth_block_info.common import create_block_address
from sawtooth_sdk.processor.exceptions import InvalidTransaction


def create_block_info(block_num,
                      signer_public_key="2" * 66,
                      header_signature="1" * 128,
                      timestamp=None,
                      previous_block_id="0" * 128):
    if timestamp is None:
        timestamp = int(time.time())

    return BlockInfo(
        block_num=block_num,
        signer_public_key=signer_public_key,
        header_signature=header_signature,
        timestamp=timestamp,
        previous_block_id=previous_block_id)

class TestHandler(unittest.TestCase):
    
    def test_validate_hex_previd(self):
        """ Tests previous block id is in valid hex """
        block_info = create_block_info(block_num=1)
        vp=validate_hex(block_info.previous_block_id, 128)
        self.assertEqual(vp, True)
        
    def test_validate_hex_sign_public_key(self):
        """ Tests signer public key is in valid hex """
        block_info = create_block_info(block_num=1)
        vp=validate_hex(block_info.signer_public_key, 66)
        self.assertEqual(vp, True)
        
    def test_validate_hex_header_sign_key(self):
        """ Tests header signature is in valid hex """
        block_info = create_block_info(block_num=1)
        vp=validate_hex(block_info.header_signature, 128)
        self.assertEqual(vp, True)
        
    def test_validate_timestamp(self):
        """ Tests the timestamp is greater than zero """
        block_info = create_block_info(block_num=1)
        now = time.time()
        if (block_info.timestamp - now) < DEFAULT_SYNC_TOLERANCE:
            validate_timestamp(block_info.timestamp,DEFAULT_SYNC_TOLERANCE)
            self.assertTrue(True)
          
    def test_validate_hex_ve(self):
        vp=validate_hex("test", 128)
        self.assertEqual(vp, False)
   