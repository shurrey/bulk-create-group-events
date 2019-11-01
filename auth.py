
"""
Copyright (C) 2016, Blackboard Inc.
All rights reserved.
Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
Neither the name of Blackboard Inc. nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY BLACKBOARD INC ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL BLACKBOARD INC. BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

Created on May 25, 2016

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

requests.packages.urllib3.disable_warnings()

#Tls1Adapter allows for connection to sites with non-CA/self-signed
#  certificates e.g.: Learn Dev VM
class Tls1Adapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=ssl.PROTOCOL_TLSv1)

class AuthToken():
    target_url = ''
    def __init__(self, URL):

        #Example Only. Change to your key
        self.KEY = "C4185313-B502-8AB5-9CFF-10529A2851A6"
        
        #Example Only. Change to your secret
        self.SECRET = "ODJm2RrZy0pM24zFYaUc9lFx6wOcPWi9Z9YHG8ErUAfX6eomsx2NJIjSSSO3UIVq90vTaY23JOqXxezRKYIk8s9nJ5w5MaibVv"

        aud = 'blackboard.smallworldlabs.com'
        uid = '13'
        scope = 'create delete read update'
        iat = datetime.datetime.utcnow()
        exp = iat + datetime.timedelta(seconds=60)
        print("exp: " + str(exp) + " iat: " + str(iat))
        headers = {
            'alg': 'HS256'
            
        }
        print("HEADERS: " + str(headers))
        claims = {"iss" : self.KEY ,"sub" : uid ,"exp" : exp, "iat" : iat, "aud" : aud, "scope" : scope }
        print("CLAIMS: " + str(claims))
        self.ASSERTION = jwt.encode(claims, self.SECRET)
        
        print("ASSERTION: " + str(self.ASSERTION))
        self.CREDENTIALS = 'urn:ietf:params:oauth:grant-type:jwt-bearer'
        print("CREDENTIALS: " + self.CREDENTIALS)
        self.PAYLOAD = {
            'grant_type' : self.CREDENTIALS,
            'assertion' : self.ASSERTION
            
        }
        print("PAYLOAD: " + str(self.PAYLOAD))
        self.TOKEN = None
        self.target_url = URL
        self.EXPIRES_AT = ''

    def getKey(self):
        return self.KEY

    def getSecret(self):
        return self.SECRET

    def setToken(self):
        OAUTH_URL = self.target_url + '/token'

        if self.TOKEN is None:
            session = requests.session()
            session.mount('https://', Tls1Adapter()) # remove for production

        # Authenticate
            print("[auth:setToken] POST Request URL: " + OAUTH_URL)
            #print("[auth:setToken] JSON Payload: \n" + json.dumps(self.PAYLOAD, indent=4, separators=(',', ': ')))

            r = session.post(OAUTH_URL, data=self.PAYLOAD, auth=(self.KEY, self.SECRET), verify=False)

            print("[auth:setToken()] STATUS CODE: " + str(r.status_code) )
            #strip quotes from result for better dumps
            res = json.loads(r.text)
            print("[auth:setToken()] RESPONSE: \n" + json.dumps(res,indent=4, separators=(',', ': ')))

            if r.status_code == 200:
                parsed_json = json.loads(r.text)
                self.TOKEN = parsed_json['access_token']
                self.EXPIRES = parsed_json['expires_in']
                m, s = divmod(self.EXPIRES, 60)
                #h, m = divmod(m, 60)
                #print "%d:%02d:%02d" % (h, m, s)
                self.NOW = datetime.datetime.now()
                self.EXPIRES_AT = self.NOW + datetime.timedelta(seconds = s, minutes = m)
                print ("[auth:setToken()] Token Expires at " + self.EXPIRES_AT.strftime("%H:%M:%S"))

                print ("[auth:setToken()] TOKEN: " + self.TOKEN)

                #there is the possibility the reaquired token may expire
                #before we are done so perform expiration sanity check...
                if self.isExpired(self.EXPIRES_AT):
                    self.setToken()

            else:
                print("[auth:setToken()] ERROR")
        else:
            print ("[auth:setToken()] TOKEN set")

    def getToken(self):
        #if token time is less than a one second then
        # print that we are pausing to clear
        # re-auth and return the new token
        if self.isExpired(self.EXPIRES_AT):
            self.setToken()

        return self.TOKEN

    def isExpired(self, expiration_datetime):
        expired = False
        print ("[auth:isExpired()] Token Expires at " + expiration_datetime.strftime("%H:%M:%S"))

        time_left = (expiration_datetime - datetime.datetime.now()).total_seconds()
        print ("[auth:isExpired()] Time Left on Token (in seconds): " + str(time_left))
        if time_left < 1:
            print ("[auth:isExpired()] Token almost expired retrieving new token in two seconds.")
            time.sleep( 1 )
            expired = True

        return expired
