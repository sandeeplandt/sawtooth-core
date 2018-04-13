import time
import zmq
import unittest



from sawtooth_processor_test.message_factory import MessageFactory
from sawtooth_block_info.protobuf.block_info_pb2 import BlockInfoTxn
from sawtooth_block_info.protobuf.block_info_pb2 import BlockInfo
from sawtooth_block_info.protobuf.block_info_pb2 import BlockInfoConfig
from sawtooth_sdk.processor.exceptions import LocalConfigurationError
from sawtooth_block_info.processor.config.block_info import load_default_block_info_config, load_toml_block_info_config, merge_block_info_config
from sawtooth_block_info.common import FAMILY_NAME
from sawtooth_block_info.common import FAMILY_VERSION
from sawtooth_block_info.common import NAMESPACE
from sawtooth_block_info.common import CONFIG_ADDRESS
from sawtooth_block_info.common import DEFAULT_SYNC_TOLERANCE
from sawtooth_block_info.common import DEFAULT_TARGET_COUNT
from sawtooth_block_info.common import create_block_address



class TestBlockInfoConfig(unittest.TestCase):
    def test_load_default_block_info_config(self):
        """ Tests the default return value of config file """
        bc=load_default_block_info_config()
        self.assertEqual(bc.connect, "tcp://localhost:4004")
        #self.assertEqual(bc.connect, "hi")
        
    def test_load_toml_block_info_config_ne(self):
        """ Tests toml load file if it is not present """
        filename="test.toml"
        cf=load_toml_block_info_config(filename)
        self.assertEqual(cf.connect, None)
    
    def test_load_toml_block_info_config(self):
        """ Tests value inside toml load file """
        filename="test_block_info.toml"
        with open(filename, 'w') as fd:
            fd.write('connect = "tcp://blarg:1234"')
        config = load_toml_block_info_config(filename)
        self.assertEqual(config.connect, "tcp://blarg:1234")

    def test_merge_config(self):
            """ Tests the merge of all toml config files """
            L=[]
            bc1=load_default_block_info_config()
            bc2=load_default_block_info_config()
            bc3=load_default_block_info_config()
            L.append(bc1)
            L.append(bc2)
            L.append(bc3)
            mc=merge_block_info_config(L)
            self.assertEqual(mc.connect, "tcp://localhost:4004")
            
    def test_to_toml(self):
        tt=load_default_block_info_config()
        self.assertEqual(tt.to_toml_string(), ['connect = "tcp://localhost:4004"'])
            
    def test_repr(self):
        repr=load_default_block_info_config()
        self.assertEqual(repr.__repr__(), "BlockInfoConfig(connect='tcp://localhost:4004')")
        
    def test_load_toml_block_info_config_invalidkeys(self):
        filename="a.toml"
        with open(filename, 'w') as fd:
            fd.write('ty = "tcp://test:4004"')
        with self.assertRaises(LocalConfigurationError):
            config = load_toml_block_info_config(filename)
          
    
  
        
    

