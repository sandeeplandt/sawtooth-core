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
   
from conftest import setup
from utils import get_state_list, get_batches, post_batch, get_state_list, get_state_limit, get_state, get_batch_statuses
  
from base import RestApiBaseTest
   
   
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)
   
pytestmark = [pytest.mark.get, pytest.mark.state]
 
 
class TestStateList(RestApiBaseTest):
    """This class tests the state list with different parameters
    """
    def test_api_get_state_list(self, setup):
        """Tests the state list by submitting intkey batches
        """
        signer_key = setup['signer_key']
        expected_head = setup['expected_head']
        expected_batches = setup['expected_batches']
        expected_txns = setup['expected_txns']
               
        try:   
            response = get_state_list()
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is Unreachable")
            
        batches = response['data'][:-1]  
                      
        self.assert_check_batch_seq(batches , expected_batches , expected_txns)
#         self.assert_valid_head(response , expected_head)
                           
    def test_api_get_state_list_invalid_batch(self, invalid_batch):
        """Tests that transactions are submitted and committed for
        each block that are created by submitting invalid intkey batches
        """    
        batch= invalid_batch[0]
        try:
            response = post_batch(batch)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
            assert data['error']['code'] == 34
            
    def test_api_get_state_list_head(self, setup):   
        """Tests that GET /state is reachable with head parameter 
        """
        LOGGER.info("Starting test for state with head parameter")
        expected_head = setup['expected_head']
                  
        try:
            response = get_state_list(head_id=expected_head)
        except  urllib.error.HTTPError as error:
            LOGGER.info("Rest Api not reachable")
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
                  
        assert response['head'] == expected_head , "request is not correct"
           
    def test_api_get_state_list_bad_head(self, setup):   
        """Tests that GET /state is unreachable with bad head parameter 
        """       
        LOGGER.info("Starting test for state with bad head parameter")
        bad_head = 'f' 
                       
        try:
            batch_list = get_state_list(head_id=bad_head)
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is not reachable")
            data = json.loads(error.fp.read().decode('utf-8'))
            if data:
                LOGGER.info(data['error']['title'])
                LOGGER.info(data['error']['message'])
                assert data['error']['code'] == 60
                assert data['error']['title'] == 'Invalid Resource Id'
      
    def test_api_get_state_list_address(self, setup):   
        """Tests that GET /state is reachable with address parameter 
        """
        LOGGER.info("Starting test for state with address parameter")
        expected_head = setup['expected_head']
        address = setup['address'][0]
                  
        try:
            response = get_state_list(address=address)
        except  urllib.error.HTTPError as error:
            LOGGER.info("Rest Api not reachable")
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
                  
        assert response['head'] == expected_head , "request is not correct"
           
    def test_api_get_state_list_bad_address(self, setup):   
        """Tests that GET /state is unreachable with bad address parameter 
        """       
        LOGGER.info("Starting test for state with bad address parameter")
        bad_address = 'f' 
                       
        try:
            batch_list = get_state_list(address=bad_address)
        except urllib.error.HTTPError as error:
            LOGGER.info("Rest Api is not reachable")
            data = json.loads(error.fp.read().decode('utf-8'))
            if data:
                LOGGER.info(data['error']['title'])
                LOGGER.info(data['error']['message'])
                assert data['error']['code'] == 60
                assert data['error']['title'] == 'Invalid Resource Id'
                                           
    def test_api_get_paginated_state_list(self, setup):   
        """Tests GET /state is reachbale using paging parameters 
        """
        LOGGER.info("Starting test for state with paging parameters")
        batch_ids   =  setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        start = 1
        limit = 1
                    
        try:
            response = get_state_list(start=start , limit=limit)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
            assert data['error']['code'] == 54
      
    def test_api_get_state_list_bad_paging(self, setup):   
        """Tests GET /state is reachbale using bad paging parameters 
        """
        LOGGER.info("Starting test for state with bad paging parameters")
        batch_ids   =  setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        start = -1
        limit = -1
                    
        try:
            response = get_state_list(start=start , limit=limit)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
            assert data['error']['code'] == 53
                 
    def test_api_get_state_list_invalid_start(self, setup):   
        """Tests that GET /state is unreachable with invalid start parameter 
        """
        LOGGER.info("Starting test for state with invalid start parameter")
        batch_ids   =  setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        start = -1
                         
        try:  
            response = get_state_list(start=start)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
            assert data['error']['code'] == 54
          
    def test_api_get_state_list_invalid_limit(self, setup):   
        """Tests that GET /state is unreachable with bad limit parameter 
        """
        LOGGER.info("Starting test for state with bad limit parameter")
        batch_ids = setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        limit = 0
                     
        try:  
            response = get_state_list(limit=limit)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
            assert data['error']['code'] == 53
      
    def test_api_get_state_list_count(self, setup):   
        """Tests that GET /state is unreachable with bad limit parameter 
        """
        LOGGER.info("Starting test for state with bad limit parameter")
        expected_head = setup['expected_head']
        count = 1
                     
        try:  
            response = get_state_list(count=count)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
          
        assert response['head'] == expected_head , "request is not correct"
    
    def test_api_get_state_list_no_count(self, setup):   
        """Tests that GET /state is unreachable with bad limit parameter 
        """
        LOGGER.info("Starting test for state with bad limit parameter")
        batch_ids =  setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        count = 0
                     
        try:  
            response = get_state_list(count=count)
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
            assert data['error']['code'] == 53
                     
    def test_api_get_state_list_reversed(self, setup):   
        """verifies that GET /state is unreachable with bad head parameter 
        """
        LOGGER.info("Starting test for state with bad head parameter")
        batch_ids = setup['batch_ids']
        expected_head = setup['expected_head']
        expected_id = batch_ids[0]
        reverse = True
                         
        try:
            response = get_state_list(reverse=reverse)
        except urllib.error.HTTPError as error:
            assert response.code == 400
                        
        assert response['head'] == expected_head , "request is not correct"
        assert response['paging']['start'] == None ,  "request is not correct"
        assert response['paging']['limit'] == None ,  "request is not correct"
        assert bool(response['data']) == True
   
    def test_api_get_state_list_bad_protobufs(self):
         """Verifies requests for lists of batches break with bad protobufs.
   
         Expects to find:
             - a status of INTERNAL_ERROR
             - that head_id, paging, and batches are missing
         """
         response = self.make_bad_request(head_id=B_1)
   
         self.assertEqual(self.status.INTERNAL_ERROR, response.status)
         self.assertFalse(response.head_id)
         self.assertFalse(response.paging.SerializeToString())
         self.assertFalse(response.batches)
 
    @pytest.mark.usefixtures('break_genesis')
    def test_api_get_state_list_no_genesis(self , break_genesis):
        """Verifies requests for lists of state breaks with no genesis.
    
         Expects to find:
             - a status of NOT_READY
        """
        try:
            response = get_state_list()
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
            assert data['error']['code'] == 15
  
    @pytest.mark.usefixtures('setup_settings_tp')
    def test_api_get_state_list_no_settings_tp(self , setup_settings_tp):
        try:
            response = get_state_list()
        except urllib.error.HTTPError as error:
            data = json.loads(error.fp.read().decode('utf-8'))
            LOGGER.info(data['error']['title'])
            LOGGER.info(data['error']['message'])
            assert data['error']['code'] == 15
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
      
# class TestStateGet():
#     def test_api_get_state_id():
#   
#         
#       
#     def test_api_get_bad_state_id(self):
#         pass    
