"""
Copyright (C) 2019, Blackboard Inc.
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
Neither the name of Blackboard Inc. nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY BLACKBOARD INC ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL BLACKBOARD INC. BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Created on October 30, 2019

@author: shurrey
"""

import json
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
import time
import jwt
import datetime
import ssl
import sys

#Tls1Adapter allows for connection to sites with non-CA/self-signed
#  certificates e.g.: Learn Dev VM
class Tls1Adapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)

class Events():
    def __init__(self, target_url, token, user_id, group_id, category_id):
        self.target_url = target_url
        self.token = token
        self.user_id = user_id;
        self.group_id = group_id;
        self.category_id = category_id;
        self.EVENTS_PATH = '/event-categories/' + category_id + '/events'
        self.event_id = ''
        self.start = ''
        self.end = ''
        
    def getEventId(self):
        return self.event_id

    def createEvent(self, start, end):
        print('[Event:createEvent] token: ' + self.token)
        
        #"Authorization: Bearer $token"
        authStr = 'Bearer ' + self.token
        print('[Event:createEvent] authStr: ' + authStr)
        
        session = requests.session()
        session.mount('https://', Tls1Adapter()) # remove for production with commercial cert
        print("[Event:createEvent] POST Request URL: https://" + self.target_url + self.EVENTS_PATH)

        self.start = start
        self.end = end

        self.PAYLOAD = {
            "userId" : self.user_id,
            "name" : "My Event",
            "description" : "My Event's Description",
            "startDate" : self.start,
            "endDate" : self.end,
            "public" : True,
            "allowGuests" : True,
            "status" : "60",
            "timezone" : "America/New_York",
            "groupId" : self.group_id,
            "fields" : [
                {
                    "id" : "6",
                    "data" : "https://bit.ly/my-link"
                }
            ]
        }

        print("[Event:createEvent] JSON Payload: "  + json.dumps(self.PAYLOAD,indent=4, separators=(',', ': ')))
        
        r = session.post(self.target_url + self.EVENTS_PATH, headers={ 'Authorization':authStr,'Content-Type':'application/json','Accept':'application/json' }, json=self.PAYLOAD, verify=False)
        
        print("[Event:createEvent] STATUS CODE: " + str(r.status_code) )
        print("[Event:createEvent] RESPONSE:")
        
        if r.text:
            res = json.loads(r.text)
            self.event_id = res['id'];
            print(json.dumps(res,indent=4, separators=(',', ': ')))
        else:
            print("NONE")