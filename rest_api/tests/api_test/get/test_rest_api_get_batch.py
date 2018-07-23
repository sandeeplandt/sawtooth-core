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
import pytest
import logging
import json
import urllib.request
import urllib.error
  
#from fixtures import setup
from utils import get_state_list
 
from base import RestApiBaseTest
state_address = 70

 
from fixtures import break_genesis, invalid_batch
from utils import get_batches, post_batch, post_batch_statuses, get_state, get_state_limit,  get_blocks,\
                  get_state_list , _delete_genesis , _start_validator, \
                  _stop_validator , _create_genesis , wait_for_rest_apis , _get_client_address, \
                  _stop_settings_tp, _start_settings_tp, get_batch_statuses
from google.protobuf.json_format import MessageToDict

from base import RestApiBaseTest
from payload import get_signer, create_intkey_transaction , create_batch


pytestmark = [pytest.mark.get , pytest.mark.batch]

  
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
  

class TestBatchList(RestApiBaseTest):
    """This class tests the batch list with different parameters
    """
    def test_api_get_batch_list(self, setup):
        """Tests the batch list by submitting intkey batches
        """
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        expected_txns = setup['expected_txns']
                                 
        try:   
            response = get_batches()
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is Unreachable")
              
        batches = response['data'][:-1]  
                         
        self.assert_check_batch_seq(batches, expected_batches, expected_txns)
        self.assert_valid_head(response, expected_head)
            
    def test_api_get_batch_list_head(self, setup):   
        """Tests that GET /batches is reachable with head parameter 
        """
        LOGGER.info("Starting test for batch with head parameter")
        expected_head = setup['expected_head']
                 
        try:
            response = get_batches(head_id=expected_head)
        except  urllib.error.HTTPError as error:
            LOGGER.info("Rest Api not reachable")
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
                 
        assert response['head'] == expected_head , "request is not correct"
          
    def test_api_get_batch_list_bad_head(self, setup):   
        """Tests that GET /batches is unreachable with bad head parameter 
        """       
        LOGGER.info("Starting test for batch with bad head parameter")
        bad_head = 'f' 
                      
        try:
            batch_list = get_batches(head_id=bad_head)
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is not reachable")
            data = json.loads(error.fp.read().decode('utf-8'))
            if data:
                LOGGER.info(data['error']['title'])
                LOGGER.info(data['error']['message'])
                assert data['error']['code'] == 60
                assert data['error']['title'] == 'Invalid Resource Id'
               
    def test_api_get_batch_list_id(self, setup):   
        """Tests that GET /batches is reachable with id as parameter 
        """
        LOGGER.info("Starting test for batch with id parameter")
                      
        batch_ids   =  setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
                     
        try:
            response = get_batches(id=expected_id)
        except:
            LOGGER.info("Rest Api is not reachable")
                    
                    
        assert response['head'] == expected_head, "request is not correct"
        assert response['paging']['start'] == None , "request is not correct"
        assert response['paging']['limit'] == None , "request is not correct"
                
    def test_api_get_batch_list_bad_id(self, setup):   
        """Tests that GET /batches is unreachable with bad id parameter 
        """
        LOGGER.info("Starting test for batch with bad id parameter")
        bad_id = 'f' 
                      
        try:
            batch_list = get_batches(head_id=bad_id)
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is not reachable")
            data = json.loads(error.fp.read().decode('utf-8'))
            if data:
                LOGGER.info(data['error']['title'])
                LOGGER.info(data['error']['message'])
                assert data['error']['code'] == 60
                assert data['error']['title'] == 'Invalid Resource Id'
              
    def test_api_get_batch_list_head_and_id(self, setup):   
        """Tests GET /batches is reachable with head and id as parameters 
        """
        LOGGER.info("Starting test for batch with head and id parameter")
        batch_ids =  setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
                       
                
        response = get_batches(head_id=expected_head , id=expected_id)
                      
        assert response['head'] == expected_head , "head is not matching"
        assert response['paging']['start'] == None ,  "start parameter is not correct"
        assert response['paging']['limit'] == None ,  "request is not correct"
        assert bool(response['data']) == True
                
               
    def test_api_get_paginated_batch_list(self, setup):   
        """Tests GET /batches is reachbale using paging parameters 
        """
        LOGGER.info("Starting test for batch with paging parameters")
        batch_ids   =  setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        start = 1
        limit = 1
                   
        try:
            response = get_batches(start=start , limit=limit)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
            assert data['error']['code'] == 54
                
    def test_api_get_batch_list_invalid_start(self, setup):   
        """Tests that GET /batches is unreachable with invalid start parameter 
        """
        LOGGER.info("Starting test for batch with invalid start parameter")
        batch_ids   =  setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        start = -1
                        
        try:  
            response = get_batches(start=start)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
            assert data['error']['code'] == 54
         
    def test_api_get_batch_list_invalid_limit(self, setup):   
        """Tests that GET /batches is unreachable with bad limit parameter 
        """
        LOGGER.info("Starting test for batch with bad limit parameter")
        batch_ids = setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        limit = 0
                    
        try:  
            response = get_batches(limit=limit)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
            assert data['error']['code'] == 53
   
    def test_api_get_batch_list_no_count(self, setup):   
        """Tests that GET /batches is unreachable with bad limit parameter 
        """
        LOGGER.info("Starting test for batch with bad limit parameter")
        batch_ids =  setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        limit = 0
                    
        try:  
            response = get_batches(limit=limit)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
            assert data['error']['code'] == 53
                    
    def test_api_get_batch_list_reversed(self, setup):   
        """verifies that GET /batches is unreachable with bad head parameter 
        """
        LOGGER.info("Starting test for batch with bad head parameter")
        batch_ids = setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        reverse = True
                        
        try:
            response = get_batches(reverse=reverse)
        except urllib.error.HTTPError as error:
            assert response.code == 400
                       
        assert response['head'] == expected_head , "request is not correct"
        assert response['paging']['start'] == None ,  "request is not correct"
        assert response['paging']['limit'] == None ,  "request is not correct"
        assert bool(response['data']) == True
                
    def test_api_get_state_multiple_batches_multiple_address(self, setup):
        """Tests that GET /state with address parameter 
        """
        LOGGER.info("Starting test for batch with bad limit parameter")
        expected_head = setup['expected_head']
        address = setup['address'][0]
        try:
            response = get_state_list(address=address)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
            assert data['error']['code'] == 53
        assert response['head'] == expected_head , "request is not correct"
            
    def test_api_get_state_address_limit(self, setup):
        """Tests that GET /state with limit parameter 
        """
        LOGGER.info("Starting test for state with address parameter")
                 
        try:
                length = len(get_state_limit(3))
                assert length == 3
        except urllib.error.HTTPError as e:
                errdata = e.file.read().decode("utf-8")
                assert e.code == 404
    
    def test_api_get_state_invalid_state_address(self, setup):
        """Tests that GET /state with invalid state address 
        """
        LOGGER.info("Starting test for batch with bad limit parameter")
        state_addresses = setup['address'] 
        try:
            addresses=[get_state(address[:-1]) for address in state_addresses]
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
            assert data['error']['code'] == 62
    
    def test_api_get_state_invalid_resource_id(self, setup):
        """Tests that GET /state with invalid resource id 
        """
        LOGGER.info("Starting test for batch with bad limit parameter") 
        batch_ids = setup['batch_ids']
       
        try:
        
            get_batch_statuses(batch_ids) 
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
            assert data['error']['code'] == 60
            
    def test_api_get_state_data_address_prefix_namespace(self, setup):
        """Tests the state data address with 6 hex characters long 
        namespace prefix
        """   
        try:   
            for state in get_state_list()['data']:
                namespace = state['address'][:6]
                get_state_list(address=namespace)
        except urllib.error.HTTPError as error:
            LOGGER.info("Not able to access related state address using namespace prefix")
            
            
    def test_api_get_state_data_address_length(self, setup):
        """Tests the state data address length is 70 hex character long
        with proper prefix namespace
        """   
        try:
            response = get_state_list()   
            for state in get_state_list()['data']:
                #Access each address using of state
                address = len(response['data'][0]['address'])
        except urllib.error.HTTPError as error:
            LOGGER.info("State address is not 70 character long")        
        assert address == state_address
        
        
    def test_api_get_state_data_address_with_odd_hex_value(self, setup):
        """Tests the state data address fail with odd hex character 
        address 
        """   
        try:
            response = get_state_list()   
            for state in get_state_list()['data']:
                #Access each address using of state
                address = len(response['data'][0]['address'])
                if(address%2 == 0):
                    pass
        except urllib.error.HTTPError as error:
            LOGGER.info("Odd state address is not correct")
            
    def test_api_get_state_data_address_with_reduced_length(self, setup):
        """Tests the state data address with reduced even length hex character long 
        """   
        try:
            response = get_state_list()   
            for state in get_state_list()['data']:
                #Access each address using of state
                address = response['data'][0]['address']
                nhex = address[:-4]
                get_state_list(address = nhex)
        except urllib.error.HTTPError as error:
            LOGGER.info("Reduced length data address failed to processed")        
            
                    
    def test_api_get_state_data_address_64_Hex(self, setup):
        """Tests the state data address with 64 hex give empty data 
        """   
        try:
            response = get_state_list()   
            for state in get_state_list()['data']:
                #Access each address using of state
                address = response['data'][0]['address']
                nhex = address[6:70]
                naddress = get_state_list(address = nhex)
                assert naddress['data'] == []
        except urllib.error.HTTPError as error:
            LOGGER.info("state data address with 64 hex characters not processed ")        
                    
                    
    def test_api_get_state_data_address_alter_bytes(self, setup):
        """Tests the state data address with alter bytes give empty data 
        """   
        try:
            response = get_state_list()   
            for state in get_state_list()['data']:
                #Access each address using of state
                address = response['data'][0]['address']
                nhex = address[6:8]
                naddress = get_state_list(address = nhex)
                assert naddress['data'] == []
        except urllib.error.HTTPError as error:
            LOGGER.info("state data address with altered bytes not processed ")    
            
    def test_api_get_state_single_txns(self, setup):   
         """Tests that GET /state for single transaction
         """
         LOGGER.info("Starting test for state with bad limit parameter")
         expected_head = setup['expected_head']
                     
         try:  
             response = get_state_list()
         except urllib.error.HTTPError as error:
             data = json.loads(error.fp.read().decode('utf-8'))
             LOGGER.info(data['error']['title'])
             LOGGER.info(data['error']['message'])          
         assert response['head'] == expected_head , "request is not correct"    

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
  
 
